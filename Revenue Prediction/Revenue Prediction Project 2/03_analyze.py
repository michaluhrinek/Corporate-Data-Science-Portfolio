#train a forecasting model and predict the next 30 days of revenue
#import libraries
import pandas as pd
import numpy as np
import json
import os
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error #this same idea as XGBoost model,

#settings
TEST_SIZE             = 0.20  #use last 20% of data for testing
FORECAST_HORIZON_DAYS = 30    #how many days to forecast into the future
LAG_DAYS              = [1, 7, 14, 28]
ROLLING_WINDOWS       = [7, 28]

#load the feature data
df = pd.read_csv("data/features.csv", parse_dates=["date"])
df = df.sort_values("date").reset_index(drop=True)

#columns the model learns from (everything except date and revenue)
feature_cols = [c for c in df.columns if c not in ["date", "revenue"]]

#split by time - first 80% is training, last 20% is testing
#IMPORTANT: never shuffle time series data, always split in order
split_idx = int(len(df) * (1 - TEST_SIZE))
train = df.iloc[:split_idx]
test  = df.iloc[split_idx:]

print(f"Train: {len(train)} rows ({train['date'].min().date()} to {train['date'].max().date()})")
print(f"Test:  {len(test)} rows ({test['date'].min().date()} to {test['date'].max().date()})")

X_train = train[feature_cols]
y_train = train["revenue"]
X_test  = test[feature_cols]
y_test  = test["revenue"]

#train the model - HistGradientBoosting is sklearn's fast gradient boosting (same idea as LightGBM)
model = HistGradientBoostingRegressor(
    max_iter=500,
    learning_rate=0.05,
    max_depth=6,
    random_state=42,
)
model.fit(X_train, y_train)

#evaluate model on the test set
test_pred = model.predict(X_test)
mae  = mean_absolute_error(y_test, test_pred)
rmse = np.sqrt(mean_squared_error(y_test, test_pred))
mape = np.mean(np.abs((y_test.to_numpy() - test_pred) / y_test.to_numpy())) * 100

#naive baseline: predict that tomorrow = today (simplest possible forecast)
naive_pred = test["lag_1"].to_numpy()
n_mae  = mean_absolute_error(y_test, naive_pred)
n_rmse = np.sqrt(mean_squared_error(y_test, naive_pred))
n_mape = np.mean(np.abs((y_test.to_numpy() - naive_pred) / y_test.to_numpy())) * 100

improvement = (n_mae - mae) / n_mae * 100

print(f"\nModel:  MAE={mae:.1f}  RMSE={rmse:.1f}  MAPE={mape:.2f}%")
print(f"Naive:  MAE={n_mae:.1f}  RMSE={n_rmse:.1f}  MAPE={n_mape:.2f}%")
print(f"Model beats naive by {improvement:.1f}%")

#save test predictions
os.makedirs("data", exist_ok=True)
test_out = test[["date", "revenue"]].copy()
test_out["predicted"] = test_pred
test_out.to_csv("data/test_predictions.csv", index=False)

#retrain on ALL data before forecasting the future
model_full = HistGradientBoostingRegressor(
    max_iter=500, learning_rate=0.05, max_depth=6, random_state=42,
)
model_full.fit(df[feature_cols], df["revenue"])

#forecast next 30 days - each day uses the previous day's prediction as input
history = df[["date", "revenue"]].copy()
forecasts = []

for _ in range(FORECAST_HORIZON_DAYS):
    last_date = history["date"].iloc[-1]
    next_date = last_date + pd.Timedelta(days=1)

    #build the features for the next day using recent history
    row = {
        "dayofweek": next_date.dayofweek,
        "month":     next_date.month,
        "dayofyear": next_date.dayofyear,
        "is_weekend": int(next_date.dayofweek >= 5),
    }
    for lag in LAG_DAYS:
        row[f"lag_{lag}"] = history["revenue"].iloc[-lag]
    for w in ROLLING_WINDOWS:
        row[f"roll_mean_{w}"] = history["revenue"].iloc[-w:].mean()
        row[f"roll_std_{w}"]  = history["revenue"].iloc[-w:].std()

    #predict and store result
    yhat = float(model_full.predict(pd.DataFrame([row]))[0])
    forecasts.append({"date": next_date, "revenue": yhat})

    #add prediction to history so the next day can use it as a lag
    history = pd.concat([history, pd.DataFrame([{"date": next_date, "revenue": yhat}])], ignore_index=True)

forecast_df = pd.DataFrame(forecasts)
forecast_df.to_csv("data/forecast.csv", index=False)

#save summary results
os.makedirs("outputs", exist_ok=True)
results = {
    "train_size": len(train),
    "test_size":  len(test),
    "metrics": {
        "model": {"MAE": float(mae), "RMSE": float(rmse), "MAPE": float(mape)},
        "naive": {"MAE": float(n_mae), "RMSE": float(n_rmse), "MAPE": float(n_mape)},
        "improvement_over_naive_pct": float(improvement),
    },
    "forecast_horizon_days": FORECAST_HORIZON_DAYS,
    "forecast_total":     float(forecast_df["revenue"].sum()),
    "forecast_daily_avg": float(forecast_df["revenue"].mean()),
}
with open("outputs/results.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nForecast saved to data/forecast.csv")
print(f"Results saved to outputs/results.json")

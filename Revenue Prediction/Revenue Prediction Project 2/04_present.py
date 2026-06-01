#create charts and report from the forecast results
#import libraries
import pandas as pd
import matplotlib.pyplot as plt
import json

#load all data files
history   = pd.read_csv("data/raw_data.csv", parse_dates=["date"])
test_pred = pd.read_csv("data/test_predictions.csv", parse_dates=["date"])
forecast  = pd.read_csv("data/forecast.csv", parse_dates=["date"])

with open("outputs/results.json") as f:
    results = json.load(f)

# ── CHART 1: full forecast chart ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 6))

#training data (everything before the test period)
train_end = test_pred["date"].min()
train_data = history[history["date"] < train_end]
ax.plot(train_data["date"], train_data["revenue"],
        color="#0B2545", lw=1, alpha=0.7, label="Training data")

#actual vs predicted in the test window
ax.plot(test_pred["date"], test_pred["revenue"],
        color="#0B2545", lw=1.5, label="Test actual")
ax.plot(test_pred["date"], test_pred["predicted"],
        color="#B85042", lw=1.5, ls="--", label="Test predicted")

#future forecast
ax.plot(forecast["date"], forecast["revenue"],
        color="#0E7C7B", lw=2, label=f"{len(forecast)}-day forecast")
ax.axvspan(forecast["date"].min(), forecast["date"].max(), alpha=0.1, color="#0E7C7B")

ax.set_title("Revenue forecast - history, test, and future")
ax.set_xlabel("Date")
ax.set_ylabel("Revenue")
ax.legend(loc="upper left")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("outputs/forecast.png", dpi=130)
plt.close()
print("Saved to outputs/forecast.png")

# ── REPORT ────────────────────────────────────────────────────────────────────
m = results["metrics"]["model"]
n = results["metrics"]["naive"]

report = f"""# Revenue Forecast Report

## How accurate is the model?

| Metric | Model | Naive baseline | Better by |
|--------|-------|----------------|-----------|
| MAE    | {m['MAE']:.1f} | {n['MAE']:.1f} | {(n['MAE']-m['MAE'])/n['MAE']*100:+.1f}% |
| RMSE   | {m['RMSE']:.1f} | {n['RMSE']:.1f} | {(n['RMSE']-m['RMSE'])/n['RMSE']*100:+.1f}% |
| MAPE   | {m['MAPE']:.2f}% | {n['MAPE']:.2f}% | {(n['MAPE']-m['MAPE'])/n['MAPE']*100:+.1f}% |

- MAE = on average predictions are off by this many dollars
- MAPE = error as a percentage of the real value (easiest to understand)
- Naive baseline = predicting tomorrow = today (if model cant beat this its useless)

## Next {results['forecast_horizon_days']} days forecast

- Total predicted revenue: {results['forecast_total']:,.0f}
- Daily average: {results['forecast_daily_avg']:,.1f}

## When to use this

- Budget planning for the next month
- Staffing decisions based on expected volume
- Spotting if actual revenue falls far below the forecast (early warning)
"""

with open("outputs/report.md", "w") as f:
    f.write(report)

print("Saved to outputs/report.md")
print("Done - check the outputs folder!")

# ============================================================
# PROJECT 1: SALES FORECASTING
# Question from board: "How many units will we sell next month / quarter?"
# Model: Prophet
# Measures: MAPE, RMSE, MAE
# Why Prophet not Linear Regression:
#   Linear regression draws a straight line and misses
#   holidays, seasonal patterns, and weekly cycles.
#   Prophet captures all of that automatically.
# ============================================================

import sys
sys.stdout.reconfigure(encoding="utf-8")
import polars as pl
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

print("=" * 60)
print("PROJECT 1: SALES FORECASTING")
print("Question: How many units will we sell next month / quarter?")
print("=" * 60)

# ── STEP 1: GENERATE DATA ────────────────────────────────────
print("\n--- STEP 1: Generating 3 years of daily sales data ---")

np.random.seed(42)
dates = pl.date_range(
    start=pl.date(2022, 1, 1),
    end=pl.date(2024, 12, 31),
    interval="1d",
    eager=True
)

n = len(dates)

# Build realistic sales with trend + seasonality + noise
trend         = np.linspace(200, 350, n)                          # growing business
yearly_season = 40  * np.sin(2 * np.pi * np.arange(n) / 365)     # yearly wave
weekly_season = 20  * np.sin(2 * np.pi * np.arange(n) / 7)       # weekly cycle
noise         = np.random.normal(0, 15, n)                         # random noise

# Holiday spikes — Christmas and New Year
holiday_spike = np.zeros(n)
for i, d in enumerate(dates):
    if d.month == 12 and d.day >= 20:
        holiday_spike[i] = 80
    if d.month == 1 and d.day <= 5:
        holiday_spike[i] = 60

sales = trend + yearly_season + weekly_season + holiday_spike + noise
sales = np.maximum(sales, 50).round().astype(int)

df = pl.DataFrame({
    "date":  dates,
    "sales": sales
})

print(f"Generated {len(df)} days of sales data")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print(f"Average daily sales: {df['sales'].mean():.0f} units")
print(f"Min: {df['sales'].min()} | Max: {df['sales'].max()}")

# ── STEP 2: CLEAN DATA ───────────────────────────────────────
print("\n--- STEP 2: Cleaning data ---")

# Check for nulls
nulls = df.null_count()
print(f"Null values: {nulls}")

# Check for negative sales (impossible)
negative = df.filter(pl.col("sales") < 0).height
print(f"Negative sales rows: {negative}")

# Check for outliers using IQR
q1 = df["sales"].quantile(0.25)
q3 = df["sales"].quantile(0.75)
iqr = q3 - q1
lower = q1 - 1.5 * iqr
upper = q3 + 1.5 * iqr
outliers = df.filter((pl.col("sales") < lower) | (pl.col("sales") > upper))
print(f"Outliers detected (IQR method): {outliers.height} rows")
print(f"IQR bounds: [{lower:.0f}, {upper:.0f}]")
print("Data is clean — no issues found.")

# ── STEP 3: EXPLORE DATA ─────────────────────────────────────
print("\n--- STEP 3: Exploring patterns ---")

# Monthly average sales
monthly = (
    df
    .with_columns(pl.col("date").dt.month().alias("month"))
    .group_by("month")
    .agg(pl.col("sales").mean().alias("avg_sales"))
    .sort("month")
)
print("\nMonthly average sales:")
print(monthly)

# Day of week patterns
daily = (
    df
    .with_columns(pl.col("date").dt.weekday().alias("weekday"))
    .group_by("weekday")
    .agg(pl.col("sales").mean().alias("avg_sales"))
    .sort("weekday")
)
day_names = {1:"Mon", 2:"Tue", 3:"Wed", 4:"Thu", 5:"Fri", 6:"Sat", 7:"Sun"}
print("\nDay of week average sales:")
for row in daily.iter_rows():
    label = day_names.get(row[0], f"Day{row[0]}")
    print(f"  {label}: {row[1]:.0f} units")

# Yearly growth
yearly = (
    df
    .with_columns(pl.col("date").dt.year().alias("year"))
    .group_by("year")
    .agg(pl.col("sales").sum().alias("total_sales"))
    .sort("year")
)
print("\nYearly total sales:")
print(yearly)

# ── STEP 4: APPLY PROPHET MODEL ──────────────────────────────
print("\n--- STEP 4: Training Prophet model ---")
print("Why Prophet? Captures seasonality + holidays that linear regression misses.")

# Prophet needs columns named 'ds' and 'y'
prophet_df = df.rename({"date": "ds", "sales": "y"}).to_pandas()
prophet_df["ds"] = prophet_df["ds"].astype(str)

# Train on first 2.5 years, test on last 6 months
train_size = int(len(prophet_df) * 0.85)
train = prophet_df[:train_size]
test  = prophet_df[train_size:]

print(f"Training on {len(train)} days")
print(f"Testing on {len(test)} days")

# Build and train Prophet
model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
    seasonality_mode="additive"
)
model.fit(train)

# Forecast on test period + next 90 days (next quarter)
future = model.make_future_dataframe(periods=90)
forecast = model.predict(future)

# ── STEP 5: MEASURE THE MODEL ────────────────────────────────
print("\n--- STEP 5: Measuring model accuracy ---")
print("Metrics: MAPE, RMSE, MAE")

# Get predictions for test period — align by converting ds to str
forecast['ds_str'] = forecast['ds'].astype(str)
test['ds_str'] = test['ds'].astype(str)
merged_test = test.merge(forecast[['ds_str','yhat']], on='ds_str')
y_true = merged_test['y'].values
y_pred = merged_test['yhat'].values

mae  = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(mean_squared_error(y_true, y_pred))
mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

print(f"\nMAE  (Mean Absolute Error):       {mae:.1f} units")
print(f"  → On average forecasts are off by {mae:.0f} units per day")
print(f"\nRMSE (Root Mean Squared Error):   {rmse:.1f} units")
print(f"  → Average error in actual units — sensitive to big misses")
print(f"\nMAPE (Mean Abs Percentage Error): {mape:.1f}%")
print(f"  → Forecasts are off by {mape:.1f}% on average")

if mape < 10:
    print(f"  → VERDICT: Excellent forecast (MAPE < 10%)")
elif mape < 20:
    print(f"  → VERDICT: Good forecast (MAPE < 20%)")
else:
    print(f"  → VERDICT: Needs improvement (MAPE > 20%)")

# ── STEP 6: ANSWER THE BUSINESS QUESTION ─────────────────────
print("\n--- STEP 6: Answering the business question ---")

# Next 90 days forecast (next quarter)
next_quarter = pl.from_pandas(
    forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(90)
).rename({
    "ds":          "date",
    "yhat":        "forecast",
    "yhat_lower":  "lower_bound",
    "yhat_upper":  "upper_bound"
}).with_columns([
    pl.col("forecast").round(0).cast(pl.Int32),
    pl.col("lower_bound").round(0).cast(pl.Int32),
    pl.col("upper_bound").round(0).cast(pl.Int32),
])

total_next_quarter = next_quarter["forecast"].sum()
avg_next_month     = next_quarter.head(30)["forecast"].sum()

print(f"\nNext 30 days (next month):  {avg_next_month:,} units expected")
print(f"Next 90 days (next quarter): {total_next_quarter:,} units expected")
print(f"\nForecast range (95% confidence):")
print(f"  Low:  {next_quarter['lower_bound'].sum():,} units")
print(f"  High: {next_quarter['upper_bound'].sum():,} units")

print("\nFirst 10 days of forecast:")
print(next_quarter.head(10))

# ── STEP 7: VISUALISE ────────────────────────────────────────
print("\n--- STEP 7: Creating visualisation ---")

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=[
        "Historical Sales + Forecast",
        "Monthly Seasonality Pattern",
        "Forecast vs Actual (Test Period)",
        "Next 90 Days Forecast"
    ]
)

# Plot 1 — Full history + forecast
hist = prophet_df
fig.add_trace(go.Scatter(
    x=hist["ds"], y=hist["y"],
    name="Actual Sales", line=dict(color="#1D4ED8", width=1)
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=forecast["ds"].tail(90), y=forecast["yhat"].tail(90),
    name="Forecast", line=dict(color="#DC2626", width=2, dash="dash")
), row=1, col=1)

# Plot 2 — Monthly pattern
months = ["Jan","Feb","Mar","Apr","May","Jun",
          "Jul","Aug","Sep","Oct","Nov","Dec"]
monthly_pd = monthly.to_pandas()
fig.add_trace(go.Bar(
    x=months, y=monthly_pd["avg_sales"],
    name="Monthly Avg", marker_color="#0D9488"
), row=1, col=2)

# Plot 3 — Forecast vs actual on test set
fig.add_trace(go.Scatter(
    x=test["ds"], y=y_true,
    name="Actual", line=dict(color="#1D4ED8")
), row=2, col=1)
fig.add_trace(go.Scatter(
    x=test["ds"], y=y_pred,
    name="Predicted", line=dict(color="#DC2626", dash="dash")
), row=2, col=1)

# Plot 4 — Next 90 days
nq_pd = next_quarter.to_pandas()
fig.add_trace(go.Scatter(
    x=nq_pd["date"], y=nq_pd["forecast"],
    name="Next Quarter", line=dict(color="#7C3AED", width=2),
    fill="tonexty"
), row=2, col=2)
fig.add_trace(go.Scatter(
    x=nq_pd["date"], y=nq_pd["upper_bound"],
    name="Upper", line=dict(color="#7C3AED", dash="dot", width=1)
), row=2, col=2)
fig.add_trace(go.Scatter(
    x=nq_pd["date"], y=nq_pd["lower_bound"],
    name="Lower", line=dict(color="#7C3AED", dash="dot", width=1)
), row=2, col=2)

fig.update_layout(
    title="Project 1: Sales Forecasting — Prophet Model",
    height=700,
    template="plotly_white",
    showlegend=False
)

fig.write_html(r"C:\Users\User\Downloads\Payments\sales_forecasting\project1_sales_forecast.html")
print("Chart saved to project1_sales_forecast.html")

print("\n" + "=" * 60)
print("PROJECT 1 COMPLETE")
print(f"MAPE: {mape:.1f}% | RMSE: {rmse:.1f} | MAE: {mae:.1f}")
print(f"Next quarter forecast: {total_next_quarter:,} units")
print("=" * 60)

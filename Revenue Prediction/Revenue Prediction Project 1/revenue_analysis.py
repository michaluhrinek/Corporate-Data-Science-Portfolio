# ============================================================
# PROJECT 3: REVENUE ANALYSIS
# Questions from board:
#   A. "What will our total revenue be next quarter?" → Prophet
#   B. "Which of our 500 customers generate most revenue?" → Random Forest Regressor
# Model A: Prophet (MAPE, RMSE, MAE)
# Model B: Random Forest Regressor (R², RMSE, MAE)
# NOTE from board correction: R² is NOT a Prophet metric.
#   R² belongs to regression models only.
# ============================================================

import sys
sys.stdout.reconfigure(encoding="utf-8")
import polars as pl
import numpy as np
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

print("=" * 60)
print("PROJECT 3: REVENUE ANALYSIS")
print("Question A: What will total revenue be next quarter?")
print("Question B: Which customers generate most revenue?")
print("=" * 60)

# ════════════════════════════════════════════════════════════
# PART A — TOTAL REVENUE FORECAST (Prophet)
# ════════════════════════════════════════════════════════════
print("\n" + "─" * 60)
print("PART A: Total Revenue Forecast — Prophet")
print("─" * 60)

# ── STEP 1: GENERATE TIME SERIES DATA ───────────────────────
print("\n--- STEP 1: Generating 3 years of monthly revenue data ---")

np.random.seed(42)
dates = pl.date_range(
    start=pl.date(2022, 1, 1),
    end=pl.date(2024, 12, 31),
    interval="1mo",
    eager=True
)

n = len(dates)
trend         = np.linspace(80000, 150000, n)
yearly_season = 15000 * np.sin(2 * np.pi * np.arange(n) / 12)
q4_boost      = np.array([8000 if d.month in [10, 11, 12] else 0 for d in dates])
noise         = np.random.normal(0, 3000, n)
revenue       = (trend + yearly_season + q4_boost + noise).round(2)

revenue_df = pl.DataFrame({
    "date":    dates,
    "revenue": revenue
})

print(f"Generated {len(revenue_df)} months of revenue data")
print(f"Average monthly revenue: ${revenue_df['revenue'].mean():,.0f}")
print(f"Min: ${revenue_df['revenue'].min():,.0f} | Max: ${revenue_df['revenue'].max():,.0f}")

# ── STEP 2: CLEAN ───────────────────────────────────────────
print("\n--- STEP 2: Cleaning revenue data ---")
print(f"Null values: {revenue_df.null_count().to_pandas().sum().sum()}")
print(f"Negative revenue rows: {revenue_df.filter(pl.col('revenue') < 0).height}")

# Check for anomalies
mean_rev = revenue_df["revenue"].mean()
std_rev  = revenue_df["revenue"].std()
anomalies = revenue_df.filter(
    (pl.col("revenue") > mean_rev + 3 * std_rev) |
    (pl.col("revenue") < mean_rev - 3 * std_rev)
)
print(f"Revenue anomalies (Z-score > 3): {anomalies.height}")
print("Data clean — ready for modelling.")

# ── STEP 3: EXPLORE ─────────────────────────────────────────
print("\n--- STEP 3: Exploring revenue patterns ---")

quarterly = (
    revenue_df
    .with_columns([
        pl.col("date").dt.year().alias("year"),
        pl.col("date").dt.quarter().alias("quarter")
    ])
    .group_by(["year", "quarter"])
    .agg(pl.col("revenue").sum().alias("quarterly_revenue"))
    .sort(["year", "quarter"])
)
print("\nQuarterly revenue breakdown:")
print(quarterly)

yearly = (
    revenue_df
    .with_columns(pl.col("date").dt.year().alias("year"))
    .group_by("year")
    .agg(pl.col("revenue").sum().alias("annual_revenue"))
    .sort("year")
)
print("\nAnnual revenue:")
print(yearly)

growth = (
    yearly["annual_revenue"][2] - yearly["annual_revenue"][0]
) / yearly["annual_revenue"][0] * 100
print(f"\nRevenue growth 2022 to 2024: {growth:.1f}%")

# ── STEP 4: PROPHET FORECAST ────────────────────────────────
print("\n--- STEP 4: Applying Prophet model ---")
print("Why Prophet: Captures Q4 spike, seasonal patterns, trend.")
print("Why NOT linear regression: misses seasonal patterns completely.")

prophet_df = revenue_df.rename(
    {"date": "ds", "revenue": "y"}
).to_pandas()
prophet_df["ds"] = prophet_df["ds"].astype(str)

# Train / test split
train = prophet_df[:-6]   # all except last 6 months
test  = prophet_df[-6:]   # last 6 months for validation

model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=False,
    daily_seasonality=False,
    seasonality_mode="multiplicative"
)
model.fit(train)

# Forecast 6 months back (test) + 3 months forward (next quarter)
future   = model.make_future_dataframe(periods=9, freq="MS")
forecast = model.predict(future)

# ── STEP 5: MEASURE ─────────────────────────────────────────
print("\n--- STEP 5: Measuring forecast accuracy ---")
print("Metrics: MAPE, RMSE, MAE")
print("NOTE: R² is NOT used for time series — that is a regression metric only.")

test_fc = forecast[forecast["ds"].isin(test["ds"])]
y_true  = test["y"].values
y_pred  = test_fc["yhat"].values

mae_a  = mean_absolute_error(y_true, y_pred)
rmse_a = np.sqrt(mean_squared_error(y_true, y_pred))
mape_a = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

print(f"\nMAE:  ${mae_a:,.0f} per month")
print(f"  → Forecasts are off by ${mae_a:,.0f} per month on average")
print(f"RMSE: ${rmse_a:,.0f} per month")
print(f"  → Sensitive to large misses like Q4 spikes")
print(f"MAPE: {mape_a:.1f}%")
print(f"  → Forecasts off by {mape_a:.1f}% on average")
print(f"  → For a CFO say: 'Our forecast has {mape_a:.1f}% average error'")

if mape_a < 10:
    print(f"  VERDICT: Excellent (MAPE < 10%)")
elif mape_a < 20:
    print(f"  VERDICT: Good (MAPE < 20%)")

# ── STEP 6: ANSWER QUESTION A ───────────────────────────────
print("\n--- STEP 6: Answering Question A ---")
print("What will total revenue be next quarter?")

next_quarter_fc = forecast.tail(3)
total_fc        = next_quarter_fc["yhat"].sum()
low_fc          = next_quarter_fc["yhat_lower"].sum()
high_fc         = next_quarter_fc["yhat_upper"].sum()

print(f"\nNext quarter forecast:")
print(f"  Expected: ${total_fc:,.0f}")
print(f"  Low  (95% CI): ${low_fc:,.0f}")
print(f"  High (95% CI): ${high_fc:,.0f}")

for _, row in next_quarter_fc.iterrows():
    ds_str = str(row['ds'])[:7]
    print(f"  {ds_str}: ${row['yhat']:,.0f} "
          f"(${row['yhat_lower']:,.0f} - ${row['yhat_upper']:,.0f})")

# ════════════════════════════════════════════════════════════
# PART B — WHICH CUSTOMERS GENERATE MOST REVENUE? (RF Regressor)
# ════════════════════════════════════════════════════════════
print("\n" + "─" * 60)
print("PART B: Customer Revenue Prediction — Random Forest Regressor")
print("─" * 60)

# ── STEP 1: GENERATE CUSTOMER DATA ──────────────────────────
print("\n--- STEP 1: Generating customer data for 500 customers ---")

np.random.seed(123)
nc = 500

contract_months  = np.random.randint(1, 36, nc)
team_size        = np.random.randint(1, 200, nc)
products_used    = np.random.randint(1, 8, nc)
industry_code    = np.random.randint(0, 5, nc)   # 0=Tech, 1=Finance, 2=Construction, 3=Healthcare, 4=Retail
support_level    = np.random.randint(1, 4, nc)    # 1=Basic, 2=Pro, 3=Enterprise
login_freq       = np.random.uniform(1, 30, nc)

# Revenue formula — larger teams, longer contracts, more products = more revenue
base_revenue = (
    team_size        * 45
  + contract_months  * 200
  + products_used    * 800
  + support_level    * 1500
  + login_freq       * 50
  + np.random.normal(0, 2000, nc)
)
annual_revenue_cust = np.maximum(base_revenue, 1000).round(2)

industries = ["Tech", "Finance", "Construction", "Healthcare", "Retail"]

customers = pl.DataFrame({
    "customer_id":      [f"CORP_{i:03d}" for i in range(nc)],
    "contract_months":  contract_months,
    "team_size":        team_size,
    "products_used":    products_used,
    "industry":         [industries[i] for i in industry_code],
    "industry_code":    industry_code,
    "support_level":    support_level,
    "login_frequency":  login_freq.round(1),
    "annual_revenue":   annual_revenue_cust,
})

print(f"Generated {nc} enterprise customers")
print(f"Average annual revenue: ${customers['annual_revenue'].mean():,.0f}")
print(f"Total portfolio revenue: ${customers['annual_revenue'].sum():,.0f}")

# ── STEP 2: CLEAN ───────────────────────────────────────────
print("\n--- STEP 2: Cleaning customer data ---")
print(f"Null values: {customers.null_count().to_pandas().sum().sum()}")
print(f"Revenue below $0: {customers.filter(pl.col('annual_revenue') < 0).height}")
print("Data clean.")

# ── STEP 3: EXPLORE ─────────────────────────────────────────
print("\n--- STEP 3: Exploring revenue patterns ---")

by_industry = (
    customers
    .group_by("industry")
    .agg([
        pl.col("annual_revenue").mean().alias("avg_revenue"),
        pl.col("annual_revenue").sum().alias("total_revenue"),
        pl.col("customer_id").count().alias("customer_count")
    ])
    .sort("avg_revenue", descending=True)
)
print("\nRevenue by industry:")
print(by_industry)

by_support = (
    customers
    .group_by("support_level")
    .agg(pl.col("annual_revenue").mean().alias("avg_revenue"))
    .sort("support_level")
)
print("\nRevenue by support tier:")
print(by_support)

# ── STEP 4: RANDOM FOREST REGRESSOR ─────────────────────────
print("\n--- STEP 4: Random Forest Regressor ---")
print("Why: Predicting a NUMBER (annual revenue) from multiple features.")
print("Why Random Forest not Linear Regression: team_size and products_used")
print("have non-linear interactions — RF captures those automatically.")

feat_cols = [
    "contract_months", "team_size", "products_used",
    "industry_code", "support_level", "login_frequency"
]

X = customers.select(feat_cols).to_numpy()
y = customers["annual_revenue"].to_numpy()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

rf = RandomForestRegressor(
    n_estimators=100,
    max_depth=8,
    random_state=42
)
rf.fit(X_train, y_train)

y_pred_rf = rf.predict(X_test)

# ── STEP 5: MEASURE ─────────────────────────────────────────
print("\n--- STEP 5: Measuring model accuracy ---")
print("Metrics: R², RMSE, MAE")
print("NOTE: These are REGRESSION metrics — output is a number, not yes/no.")
print("Never use AUC-ROC or F1 when predicting a number.")

r2   = r2_score(y_test, y_pred_rf)
rmse = np.sqrt(mean_squared_error(y_test, y_pred_rf))
mae  = mean_absolute_error(y_test, y_pred_rf)

print(f"\nR²:   {r2:.3f}")
print(f"  → Model explains {r2*100:.1f}% of revenue variation across customers")
print(f"  → Want > 0.70. Your score: {'Good' if r2 > 0.7 else 'Needs improvement'}")
print(f"\nRMSE: ${rmse:,.0f}")
print(f"  → Average prediction error is ${rmse:,.0f} per customer")
print(f"\nMAE:  ${mae:,.0f}")
print(f"  → Average absolute error is ${mae:,.0f} per customer")

# Feature importance
importance_df = pl.DataFrame({
    "feature":    feat_cols,
    "importance": rf.feature_importances_.tolist()
}).sort("importance", descending=True)

print(f"\nFeature importance (what drives revenue most?):")
for row in importance_df.iter_rows():
    bar = "█" * int(row[1] * 50)
    print(f"  {row[0]:<20} {row[1]:.3f}  {bar}")

# ── STEP 6: ANSWER QUESTION B ───────────────────────────────
print("\n--- STEP 6: Answering Question B ---")
print("Which of our 500 customers will generate most revenue?")

all_predictions = rf.predict(X)

revenue_ranking = customers.with_columns(
    pl.Series("predicted_revenue", all_predictions.round(0).astype(int))
).sort("predicted_revenue", descending=True)

print("\nTop 10 highest-value customers:")
print(
    revenue_ranking
    .select(["customer_id", "industry", "team_size",
             "products_used", "support_level", "predicted_revenue"])
    .head(10)
)

top20_revenue = revenue_ranking.head(20)["predicted_revenue"].sum()
total_revenue = revenue_ranking["predicted_revenue"].sum()
concentration = top20_revenue / total_revenue * 100

print(f"\nRevenue concentration insight:")
print(f"  Top 20 customers (4%) generate ${top20_revenue:,.0f}")
print(f"  That is {concentration:.1f}% of total predicted revenue")
print(f"  → Focus account management on these 20 customers first")

# ── STEP 7: VISUALISE BOTH PARTS ────────────────────────────
print("\n--- STEP 7: Creating visualisation ---")

fig = make_subplots(
    rows=2, cols=3,
    subplot_titles=[
        "Part A: Revenue History + Forecast",
        "Part A: Forecast vs Actual (Test)",
        "Part A: Next Quarter Forecast",
        "Part B: Predicted vs Actual Revenue",
        "Part B: Feature Importance",
        "Part B: Top 20 Customers by Revenue"
    ]
)

# A1 — Full revenue history + forecast
fig.add_trace(go.Scatter(
    x=prophet_df["ds"], y=prophet_df["y"],
    name="Actual", line=dict(color="#1D4ED8", width=2)
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=forecast["ds"].tail(9).tolist(),
    y=forecast["yhat"].tail(9).tolist(),
    name="Forecast", line=dict(color="#DC2626", dash="dash", width=2)
), row=1, col=1)

# A2 — Forecast vs actual test period
fig.add_trace(go.Scatter(
    x=list(range(len(y_true))),
    y=y_true,
    name="Actual", line=dict(color="#1D4ED8")
), row=1, col=2)
fig.add_trace(go.Scatter(
    x=list(range(len(y_pred))),
    y=y_pred,
    name="Predicted", line=dict(color="#DC2626", dash="dash")
), row=1, col=2)

# A3 — Next quarter bars
fig.add_trace(go.Bar(
    x=[str(r["ds"])[:7] for _, r in next_quarter_fc.iterrows()],
    y=[r["yhat"] for _, r in next_quarter_fc.iterrows()],
    marker_color=["#0D9488", "#0D9488", "#0D9488"],
    name="Next Quarter"
), row=1, col=3)

# B1 — Predicted vs Actual scatter
fig.add_trace(go.Scatter(
    x=y_test.tolist(), y=y_pred_rf.tolist(),
    mode="markers",
    marker=dict(color="#7C3AED", opacity=0.5, size=4),
    name="Predictions"
), row=2, col=1)

# B2 — Feature importance
imp_pd = importance_df.to_pandas()
fig.add_trace(go.Bar(
    x=imp_pd["importance"],
    y=imp_pd["feature"],
    orientation="h",
    marker_color="#D97706",
    name="Importance"
), row=2, col=2)

# B3 — Top 20 customers
top20 = revenue_ranking.head(20).to_pandas()
fig.add_trace(go.Bar(
    x=top20["customer_id"],
    y=top20["predicted_revenue"],
    marker_color="#1D4ED8",
    name="Top 20"
), row=2, col=3)

fig.update_layout(
    title="Project 3: Revenue Analysis — Prophet + Random Forest",
    height=750,
    template="plotly_white",
    showlegend=False
)

fig.write_html(r"C:\Users\User\Downloads\Payments\revenue_analysis\project3_revenue_analysis.html")
print("Chart saved to project3_revenue_analysis.html")

print("\n" + "=" * 60)
print("PROJECT 3 COMPLETE")
print(f"\nPart A — Prophet Forecast:")
print(f"  MAPE: {mape_a:.1f}% | RMSE: ${rmse_a:,.0f} | MAE: ${mae_a:,.0f}")
print(f"  Next quarter expected: ${total_fc:,.0f}")
print(f"\nPart B — Random Forest Regressor:")
print(f"  R²: {r2:.3f} | RMSE: ${rmse:,.0f} | MAE: ${mae:,.0f}")
print(f"  Top driver of revenue: {importance_df['feature'][0]}")
print("=" * 60)

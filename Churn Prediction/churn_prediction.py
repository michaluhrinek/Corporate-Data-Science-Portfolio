# ============================================================
# PROJECT 2: CUSTOMER CHURN PREDICTION
# Question from board: "Which customers will leave next month?"
# Model 1: Logistic Regression (yes/no — will they churn?)
# Model 2: XGBoost (upgrade for accuracy)
# Model 3: Survival Analysis (WHEN will they churn?)
# Measures: AUC-ROC, Recall, Precision, F1
# Survival: C-index, Hazard Ratio, Log-rank test
# ============================================================

import sys
sys.stdout.reconfigure(encoding="utf-8")
import polars as pl
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, recall_score, precision_score,
    f1_score, confusion_matrix, classification_report
)
from xgboost import XGBClassifier
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.statistics import logrank_test
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

print("=" * 60)
print("PROJECT 2: CUSTOMER CHURN PREDICTION")
print("Questions:")
print("  1. Which customers will leave next month? (Logistic/XGB)")
print("  2. When will they leave? (Survival Analysis)")
print("=" * 60)

# ── STEP 1: GENERATE DATA ────────────────────────────────────
print("\n--- STEP 1: Generating customer data ---")

np.random.seed(42)
n = 5000

# Generate realistic churn drivers
days_since_login     = np.random.exponential(15, n)
features_used        = np.random.randint(1, 20, n)
usage_trend          = np.random.uniform(-1, 1, n)
support_tickets      = np.random.poisson(1.5, n)
contract_days_left   = np.random.randint(0, 365, n)
monthly_revenue      = np.random.uniform(50, 800, n)
tenure_days          = np.random.randint(30, 1825, n)
price_increase       = np.random.binomial(1, 0.2, n)

# Churn probability — higher when:
# login gap long, few features, usage dropping, contract expiring
churn_score = (
    0.03 * days_since_login
  - 0.05 * features_used
  - 0.3  * usage_trend
  + 0.15 * support_tickets
  - 0.002 * contract_days_left
  + 0.4  * price_increase
  + np.random.normal(0, 0.3, n)
)
churn_prob = 1 / (1 + np.exp(-churn_score))
churned    = (churn_prob > 0.55).astype(int)

# Days until churn for survival analysis (censored if not churned)
days_to_churn = np.where(
    churned == 1,
    np.random.randint(1, 90, n),
    tenure_days
)

df = pl.DataFrame({
    "customer_id":        [f"CUST_{i:04d}" for i in range(n)],
    "days_since_login":   days_since_login.round(1),
    "features_used":      features_used,
    "usage_trend":        usage_trend.round(3),
    "support_tickets":    support_tickets,
    "contract_days_left": contract_days_left,
    "monthly_revenue":    monthly_revenue.round(2),
    "tenure_days":        tenure_days,
    "price_increase":     price_increase,
    "churned":            churned,
    "days_to_churn":      days_to_churn,
})

churn_rate = churned.mean() * 100
print(f"Total customers: {n:,}")
print(f"Churned: {churned.sum():,} ({churn_rate:.1f}%)")
print(f"Retained: {(1-churned).sum():,} ({100-churn_rate:.1f}%)")

# ── STEP 2: CLEAN DATA ───────────────────────────────────────
print("\n--- STEP 2: Cleaning data ---")

print(f"Null values: {df.null_count().to_pandas().sum().sum()}")
print(f"Duplicate customers: {len(df) - df['customer_id'].n_unique()}")

# Check class imbalance
print(f"\nClass balance check:")
print(f"  Churned (1):  {churned.sum():,} ({churn_rate:.1f}%)")
print(f"  Retained (0): {(1-churned).sum():,} ({100-churn_rate:.1f}%)")
if churn_rate < 20:
    print("  WARNING: Imbalanced data — Recall is more important than Accuracy")

# Basic stats
print("\nKey feature statistics:")
print(df.select([
    "days_since_login", "features_used",
    "support_tickets", "monthly_revenue"
]).describe())

# ── STEP 3: EXPLORE DATA ─────────────────────────────────────
print("\n--- STEP 3: Exploring churn patterns ---")

# Churn by features used
feature_groups = (
    df
    .with_columns(
        pl.when(pl.col("features_used") <= 5).then(pl.lit("Low (1-5)"))
          .when(pl.col("features_used") <= 12).then(pl.lit("Medium (6-12)"))
          .otherwise(pl.lit("High (13+)"))
          .alias("feature_group")
    )
    .group_by("feature_group")
    .agg(
        pl.col("churned").mean().alias("churn_rate"),
        pl.col("churned").count().alias("count")
    )
    .sort("churn_rate", descending=True)
)
print("\nChurn rate by feature usage:")
print(feature_groups)

# Average revenue at risk
churned_revenue = (
    df.filter(pl.col("churned") == 1)["monthly_revenue"].sum()
)
print(f"\nMonthly revenue at risk from churned customers: ${churned_revenue:,.0f}")

# ── STEP 4: LOGISTIC REGRESSION ──────────────────────────────
print("\n--- STEP 4: Logistic Regression ---")
print("Why: Labeled data, yes/no output, interpretable coefficients")

features = [
    "days_since_login", "features_used", "usage_trend",
    "support_tickets", "contract_days_left",
    "monthly_revenue", "price_increase"
]

X = df.select(features).to_numpy()
y = df["churned"].to_numpy()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler  = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

lr = LogisticRegression(random_state=42, max_iter=1000)
lr.fit(X_train_s, y_train)

y_pred_lr   = lr.predict(X_test_s)
y_proba_lr  = lr.predict_proba(X_test_s)[:, 1]

auc_lr  = roc_auc_score(y_test, y_proba_lr)
rec_lr  = recall_score(y_test, y_pred_lr)
prec_lr = precision_score(y_test, y_pred_lr)
f1_lr   = f1_score(y_test, y_pred_lr)

print(f"\nLogistic Regression Results:")
print(f"  AUC-ROC:   {auc_lr:.3f}  (want > 0.80)")
print(f"  Recall:    {rec_lr:.3f}  (want > 0.75) ← MOST IMPORTANT")
print(f"  Precision: {prec_lr:.3f}  (want > 0.70)")
print(f"  F1-Score:  {f1_lr:.3f}  (want > 0.75)")

print(f"\nWhy Recall is most important:")
print(f"  Missing a churner = lost ${monthly_revenue.mean():.0f}/month revenue")
print(f"  False alarm = just one unnecessary retention call")

# Feature importance via coefficients
coef_df = pl.DataFrame({
    "feature":     features,
    "coefficient": lr.coef_[0].tolist()
}).sort("coefficient", descending=True)
print(f"\nFeature coefficients (positive = increases churn risk):")
print(coef_df)

# ── STEP 5: XGBOOST UPGRADE ──────────────────────────────────
print("\n--- STEP 5: XGBoost upgrade ---")
print("Why upgrade: Captures non-linear relationships between features")

xgb = XGBClassifier(
    n_estimators=100, max_depth=4,
    random_state=42, eval_metric="logloss",
    verbosity=0
)
xgb.fit(X_train, y_train)

y_pred_xgb  = xgb.predict(X_test)
y_proba_xgb = xgb.predict_proba(X_test)[:, 1]

auc_xgb  = roc_auc_score(y_test, y_proba_xgb)
rec_xgb  = recall_score(y_test, y_pred_xgb)
prec_xgb = precision_score(y_test, y_pred_xgb)
f1_xgb   = f1_score(y_test, y_pred_xgb)

print(f"\nXGBoost Results:")
print(f"  AUC-ROC:   {auc_xgb:.3f}")
print(f"  Recall:    {rec_xgb:.3f}")
print(f"  Precision: {prec_xgb:.3f}")
print(f"  F1-Score:  {f1_xgb:.3f}")

print(f"\nModel comparison:")
print(f"  {'Metric':<12} {'Logistic':>10} {'XGBoost':>10} {'Winner':>10}")
print(f"  {'-'*44}")
for m, lr_s, xgb_s in [
    ("AUC-ROC",   auc_lr,  auc_xgb),
    ("Recall",    rec_lr,  rec_xgb),
    ("Precision", prec_lr, prec_xgb),
    ("F1-Score",  f1_lr,   f1_xgb),
]:
    winner = "XGBoost" if xgb_s > lr_s else "Logistic"
    print(f"  {m:<12} {lr_s:>10.3f} {xgb_s:>10.3f} {winner:>10}")

# ── STEP 6: SURVIVAL ANALYSIS ────────────────────────────────
print("\n--- STEP 6: Survival Analysis ---")
print("Question: WHEN will each customer churn?")
print("Why: Logistic gives yes/no. Survival gives timeline per customer.")

surv_df = df.select([
    "days_to_churn", "churned",
    "features_used", "usage_trend",
    "days_since_login", "monthly_revenue"
]).to_pandas()

# Cox Proportional Hazards
cox = CoxPHFitter()
cox.fit(
    surv_df,
    duration_col="days_to_churn",
    event_col="churned"
)

print("\nCox Model Summary:")
cox.print_summary(decimals=3)

# C-index
c_index = cox.concordance_index_
print(f"\nC-index: {c_index:.3f}")
print(f"  (0.5 = random, 1.0 = perfect, want > 0.70)")

# Kaplan-Meier survival curves by feature usage
high_usage = surv_df[surv_df["features_used"] >= 10]
low_usage  = surv_df[surv_df["features_used"] < 10]

kmf_high = KaplanMeierFitter()
kmf_low  = KaplanMeierFitter()
kmf_high.fit(high_usage["days_to_churn"], high_usage["churned"], label="High Feature Usage")
kmf_low.fit(low_usage["days_to_churn"],  low_usage["churned"],  label="Low Feature Usage")

# Log-rank test
result = logrank_test(
    high_usage["days_to_churn"], low_usage["days_to_churn"],
    high_usage["churned"],       low_usage["churned"]
)
print(f"\nLog-rank test (High vs Low feature usage):")
print(f"  p-value: {result.p_value:.4f}")
if result.p_value < 0.05:
    print(f"  VERDICT: Significant difference — feature usage strongly predicts churn timing")
else:
    print(f"  VERDICT: No significant difference")

# ── STEP 7: PRIORITY ACTION LIST ────────────────────────────
print("\n--- STEP 7: Priority action list for sales team ---")

test_indices = np.arange(len(X_test))
test_df = df[int(len(df) * 0.8):]

priority = pl.DataFrame({
    "customer_id":      test_df["customer_id"].to_list(),
    "churn_probability": y_proba_xgb.tolist(),
    "monthly_revenue":  test_df["monthly_revenue"].to_list(),
}).with_columns(
    (pl.col("churn_probability") * pl.col("monthly_revenue"))
    .alias("priority_score")
).sort("priority_score", descending=True)

print("\nTop 10 customers to call TODAY:")
print(priority.head(10))

total_at_risk = (
    priority
    .filter(pl.col("churn_probability") > 0.7)["monthly_revenue"]
    .sum()
)
print(f"\nCustomers with >70% churn risk: {priority.filter(pl.col('churn_probability') > 0.7).height}")
print(f"Monthly revenue at risk: ${total_at_risk:,.0f}")

# ── STEP 8: VISUALISE ────────────────────────────────────────
print("\n--- STEP 8: Creating visualisation ---")

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=[
        "Churn Probability Distribution",
        "Model Comparison",
        "Survival Curves — Feature Usage",
        "Revenue at Risk by Churn Probability"
    ]
)

# Plot 1 — Churn probability distribution
fig.add_trace(go.Histogram(
    x=y_proba_xgb, nbinsx=30,
    marker_color="#DC2626", name="Churn Probability"
), row=1, col=1)

# Plot 2 — Model comparison bar chart
metrics = ["AUC-ROC", "Recall", "Precision", "F1-Score"]
lr_scores  = [auc_lr,  rec_lr,  prec_lr,  f1_lr]
xgb_scores = [auc_xgb, rec_xgb, prec_xgb, f1_xgb]

fig.add_trace(go.Bar(
    x=metrics, y=lr_scores, name="Logistic", marker_color="#1D4ED8"
), row=1, col=2)
fig.add_trace(go.Bar(
    x=metrics, y=xgb_scores, name="XGBoost", marker_color="#0D9488"
), row=1, col=2)

# Plot 3 — Survival curves
t_high, s_high = kmf_high.timeline, kmf_high.survival_function_.values.flatten()
t_low,  s_low  = kmf_low.timeline,  kmf_low.survival_function_.values.flatten()

fig.add_trace(go.Scatter(
    x=t_high, y=s_high, name="High Usage",
    line=dict(color="#0D9488", width=2)
), row=2, col=1)
fig.add_trace(go.Scatter(
    x=t_low, y=s_low, name="Low Usage",
    line=dict(color="#DC2626", width=2)
), row=2, col=1)

# Plot 4 — Revenue at risk
bins = [0, 0.3, 0.5, 0.7, 0.9, 1.0]
labels = ["<30%", "30-50%", "50-70%", "70-90%", ">90%"]
priority_pd = priority.to_pandas()
priority_pd["risk_bucket"] = np.digitize(
    priority_pd["churn_probability"], bins[1:]
)
revenue_by_risk = priority_pd.groupby("risk_bucket")["monthly_revenue"].sum()

fig.add_trace(go.Bar(
    x=labels[:len(revenue_by_risk)],
    y=revenue_by_risk.values,
    marker_color=["#22C55E","#84CC16","#EAB308","#F97316","#DC2626"],
    name="Revenue at Risk"
), row=2, col=2)

fig.update_layout(
    title="Project 2: Customer Churn Prediction",
    height=700,
    template="plotly_white",
    barmode="group"
)

fig.write_html(r"C:\Users\User\Downloads\Payments\Churm_prediction.py\project2_churn_prediction.html")
print("Chart saved to project2_churn_prediction.html")

print("\n" + "=" * 60)
print("PROJECT 2 COMPLETE")
print(f"XGBoost AUC-ROC: {auc_xgb:.3f} | Recall: {rec_xgb:.3f}")
print(f"Survival C-index: {c_index:.3f}")
print(f"Monthly revenue at risk: ${total_at_risk:,.0f}")
print("=" * 60)

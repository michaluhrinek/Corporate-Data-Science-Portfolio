import numpy as np
import pandas as pd
import scipy.stats as stats

# ==========================================
# 0. SETUP: GENERATE RAW CORRUPTED DATASET
# ==========================================
np.random.seed(42)
n_records = 20500

# Simulate a buggy data engineering pipeline
user_ids = np.random.randint(10000, 30000, size=n_records)  # Generates natural duplicates
groups = np.random.choice(['A', 'B'], size=n_records, p=[0.515, 0.485])  # Imbalanced allocation 
converted = np.random.choice([0, 1], size=n_records, p=[0.88, 0.12])

# Inject an intentional true conversion lift into variant B
b_indices = (groups == 'B')
converted[b_indices] = np.random.choice([0, 1], size=sum(b_indices), p=[0.85, 0.15])

# Generate revenue per user
revenue = np.where(converted == 1, np.random.exponential(scale=45, size=n_records), 0.0)

# Inject Data Corruption anomalies
revenue[np.random.choice(n_records, 15, replace=False)] = 25000.0  # 1. Outliers (Tracking bugs/Whales)
revenue[np.random.choice(n_records, 350, replace=False)] = np.nan  # 2. Missing data (Null drops)

# Assemble raw DataFrame
raw_df = pd.DataFrame({
    'user_id': user_ids,
    'group': groups,
    'converted': converted,
    'revenue': revenue
})

print("--- PIPELINE STARTING: AUDITING RAW DATA ---")

# ==========================================
# PART 1: DATA ACCURACY & QUALITY METRICS
# ==========================================

# 1. Duplication Rate
total_rows = len(raw_df)
unique_users = raw_df['user_id'].nunique()
dup_rate = ((total_rows - unique_users) / total_rows) * 100
print(f"[QUALITY] Duplication Rate: {dup_rate:.2f}%")

# Deduplicate to isolate unique user actions
clean_df = raw_df.drop_duplicates(subset=['user_id'], keep='first').copy()

# 2. Completeness (Missing Data Rate)
missing_rev = clean_df['revenue'].isna().sum()
missing_rate = (missing_rev / len(clean_df)) * 100
print(f"[QUALITY] Revenue Missing Rate: {missing_rate:.2f}%")

# Fill or drop null entries safely
clean_df['revenue'] = clean_df['revenue'].fillna(0.0)

# 3. Outlier Isolation (using Interquartile Range)
q1 = clean_df['revenue'].quantile(0.25)
q3 = clean_df['revenue'].quantile(0.75)
iqr = q3 - q1
upper_bound = q3 + (3 * iqr)  # Using extreme threshold (3x IQR)

outliers = clean_df[clean_df['revenue'] > upper_bound]
outlier_impact_ratio = (len(outliers) / len(clean_df)) * 100
print(f"[SAFETY] Outlier Record Impact: {outlier_impact_ratio:.2f}% (Threshold: >${upper_bound:.2f})")

# Clip outliers to protect variance calculation stability
clean_df['revenue_clipped'] = np.clip(clean_df['revenue'], 0, upper_bound)


# ==========================================
# PART 2: DATA INTEGRITY & EXPERIMENT SETUP
# ==========================================

# 4. Sample Ratio Mismatch (SRM) via Chi-Square Goodness-of-Fit
observed_counts = clean_df['group'].value_counts().sort_index().values  # Counts for [A, B]
expected_counts = [len(clean_df) * 0.50, len(clean_df) * 0.50]  # Expecting strict 50/50 split

chi2_stat, p_srm = stats.chisquare(f_obs=observed_counts, f_exp=expected_counts)
print(f"[INTEGRITY] SRM Chi2 Stat: {chi2_stat:.4f} | SRM p-value: {p_srm:.6f}")

if p_srm < 0.001:
    print("ALERT: Sample Ratio Mismatch detected! Traffic allocation framework is broken.")
else:
    print("PASS: Sample allocation matches distribution constraints.")


# ==========================================
# PART 3: STATISTICAL SIGNIFICANCE CALCULATIONS
# ==========================================

# Compute high level aggregate metrics per group
metrics = clean_df.groupby('group').agg(
    visitors=('user_id', 'count'),
    conversions=('converted', 'sum'),
    total_rev_raw=('revenue', 'sum'),
    total_rev_clipped=('revenue_clipped', 'sum')
).to_dict(orient='index')

n_a, conv_a = metrics['A']['visitors'], metrics['A']['conversions']
n_b, conv_b = metrics['B']['visitors'], metrics['B']['conversions']

rate_a = conv_a / n_a
rate_b = conv_b / n_b

# 5. Pool Conversion Rate
p_pool = (conv_a + conv_b) / (n_a + n_b)

# 6. Standard Error
se = np.sqrt(p_pool * (1 - p_pool) * (1/n_a + 1/n_b))

# 7. Z-Score
z_stat = (rate_b - rate_a) / se

# 8. Two-Sided P-Value
p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

# 9. Lift Expressions
abs_lift = rate_b - rate_a
rel_lift = abs_lift / rate_a

# 10. Confidence Intervals
margin_of_error = 1.96 * se  # 1.96 corresponding to a 95% confidence level
ci_lower = abs_lift - margin_of_error
ci_upper = abs_lift + margin_of_error


# ==========================================
# PART 4: EXECUTIVE REPORT
# ==========================================
print("\n" + "="*40 + "\nFINAL AUTOMATED STATISTICAL REPORT\n" + "="*40)
print(f"Group A Conversion Rate: {rate_a:.2%}")
print(f"Group B Conversion Rate: {rate_b:.2%}")
print(f"Absolute Lift Metric:    {abs_lift:+.2%}")
print(f"Relative Lift Growth:    {rel_lift:+.2%}")
print(f"Standard Error Value:    {se:.5f}")
print(f"Z-Score Vector Position: {z_stat:+.4f}")
print(f"Experiment P-Value:      {p_value:.6f}")
print(f"95% Confidence Interval: [{ci_lower:+.2%}, {ci_upper:+.2%}]")

if p_value < 0.05:
    print("\nDecision Framework Result: STATISTICALLY SIGNIFICANT WINNER DETECTED. Deploy variant B.")
else:
    print("\nDecision Framework Result: NO SIGNIFICANT LIFTS FOUND. Keep variant A or collect more samples.")

#statistical analysis - hypothesis testing
#import libraries
import polars as pl
import numpy as np
import json
import os
from scipy import stats

ALPHA = 0.05 #significance level - if p-value is below this the difference is real

#load the cleaned data from step 2
df = pl.read_csv("data/clean_data.csv", try_parse_dates=True)

#separate group A and group B values into simple lists
a = df.filter(pl.col("group") == "A")["value"].to_numpy()
b = df.filter(pl.col("group") == "B")["value"].to_numpy()

#print basic stats for each group                                           #len(a) — counts how many rows are in Group A
print(f"Group A: {len(a)} rows, mean = {a.mean():.4f}, std = {a.std():.4f}") #a.mean() — the average EUR/USD rate in that group
print(f"Group B: {len(b)} rows, mean = {b.mean():.4f}, std = {b.std():.4f}") #a.std() — standard deviation, how much the values jump around (higher = more volatile)

#test 1: are the MEANS different? (Welch's t-test)
t_stat, t_p = stats.ttest_ind(a, b, equal_var=False)
print(f"\nWelch t-test: t = {t_stat:.4f}, p = {t_p:.6f}") #t_stat — how many standard errors apart the two means are. The further from 0, the more different the groups look.
print(f"Means are significantly different: {'YES' if t_p < ALPHA else 'NO'}") #t_p — the p-value: probability of seeing this big a difference by pure chance, assuming the groups are actually the same. Small p-value = the difference is unlikely to be random.

#test 2: are the VARIANCES (volatility) different? (Levene's test)
lev_stat, lev_p = stats.levene(a, b, center="median")
print(f"\nLevene test: statistic = {lev_stat:.4f}, p = {lev_p:.6f}")
print(f"Variances are significantly different: {'YES' if lev_p < ALPHA else 'NO'}")

#cohen's d - measures HOW BIG the difference is, not just if it exists
n1, n2 = len(a), len(b)
pooled_std = np.sqrt(((n1 - 1) * a.std()**2 + (n2 - 1) * b.std()**2) / (n1 + n2 - 2))
cohens_d = (a.mean() - b.mean()) / pooled_std

if abs(cohens_d) < 0.2:
    effect_label = "negligible"
elif abs(cohens_d) < 0.5:
    effect_label = "small"
elif abs(cohens_d) < 0.8:
    effect_label = "medium"
else:
    effect_label = "large"

print(f"\nCohen's d = {cohens_d:.3f} ({effect_label} effect size)")

#save results to a file so 04_present.py can use them
os.makedirs("outputs", exist_ok=True)

results = {
    "group_A": {"n": int(len(a)), "mean": float(a.mean()), "std": float(a.std())},
    "group_B": {"n": int(len(b)), "mean": float(b.mean()), "std": float(b.std())},
    "ttest":   {"statistic": float(t_stat), "p_value": float(t_p), "significant": bool(t_p < ALPHA), "cohens_d": float(cohens_d), "effect_size": effect_label},
    "levene":  {"statistic": float(lev_stat), "p_value": float(lev_p), "significant": bool(lev_p < ALPHA)},
    "alpha": ALPHA
}

with open("outputs/results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nSaved to outputs/results.json")

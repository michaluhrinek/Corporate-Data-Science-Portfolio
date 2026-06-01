#create chart and report from the analysis results
#import libraries
import polars as pl
import matplotlib.pyplot as plt
import json

#load the cleaned data and the results from step 3
df = pl.read_csv("data/clean_data.csv", try_parse_dates=True)

with open("outputs/results.json") as f:
    results = json.load(f)

#split data into group A and group B for the chart
group_a = df.filter(pl.col("group") == "A")
group_b = df.filter(pl.col("group") == "B")

#create a chart with two panels side by side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

#left panel: time series line chart colored by group
ax1.plot(group_a["date"].to_list(), group_a["value"].to_list(), color="#0B2545", lw=0.9, label="Group A")
ax1.plot(group_b["date"].to_list(), group_b["value"].to_list(), color="#0E7C7B", lw=0.9, label="Group B")
ax1.set_title("Time series - Group A vs Group B")
ax1.set_xlabel("Date")
ax1.set_ylabel("Value")
ax1.legend()
ax1.grid(alpha=0.3)

#right panel: histogram showing how values are distributed in each group
ax2.hist(group_a["value"].to_list(), bins=40, color="#0B2545", alpha=0.55, label="Group A", density=True)
ax2.hist(group_b["value"].to_list(), bins=40, color="#0E7C7B", alpha=0.55, label="Group B", density=True)
ax2.set_title("Distribution comparison")
ax2.set_xlabel("Value")
ax2.set_ylabel("Density")
ax2.legend()
ax2.grid(alpha=0.3)

#save the chart
plt.tight_layout()
plt.savefig("outputs/distribution_comparison.png", dpi=130)
plt.close()
print("Chart saved to outputs/distribution_comparison.png")

#pull numbers out of results for the report
a = results["group_A"]
b = results["group_B"]
t = results["ttest"]
lv = results["levene"]

#write the plain text conclusion for means
if t["significant"]:
    mean_conclusion = f"YES - the means ARE different (p = {t['p_value']:.4f}). Group A avg = {a['mean']:.4f}, Group B avg = {b['mean']:.4f}. Effect size: {t['effect_size']}."
else:
    mean_conclusion = f"NO - no significant difference in means (p = {t['p_value']:.4f}). The difference could be random chance."

#write the plain text conclusion for variance
if lv["significant"]:
    more_or_less = "more" if b["std"] > a["std"] else "less"
    var_conclusion = f"YES - the variance IS different (p = {lv['p_value']:.4f}). Group B is {more_or_less} volatile than Group A."
else:
    var_conclusion = f"NO - no significant difference in variance (p = {lv['p_value']:.4f})."

#build and save the report as a text file
report = f"""# Hypothesis Test Report

## Group stats
- Group A: {a['n']} rows, mean = {a['mean']:.4f}, std = {a['std']:.4f}
- Group B: {b['n']} rows, mean = {b['mean']:.4f}, std = {b['std']:.4f}

## Test 1 - Are the averages different? (t-test)
- p-value: {t['p_value']:.6f}
- Cohen's d: {t['cohens_d']:.3f} ({t['effect_size']} effect)
- Conclusion: {mean_conclusion}

## Test 2 - Is the volatility different? (Levene test)
- p-value: {lv['p_value']:.6f}
- Conclusion: {var_conclusion}

## How to read p-values
- p below 0.05 = the difference is real, not random
- p above 0.05 = could just be chance, not conclusive
"""

with open("outputs/report.md", "w") as f:
    f.write(report)

print("Report saved to outputs/report.md")
print("Done - check the outputs folder!")

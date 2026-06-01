#create chart and report from the A/B test results
#import libraries
import matplotlib.pyplot as plt
import json

#load results from step 3
with open("outputs/results.json") as f:  #result is mix of numbers and text for presentation, its not a table so we use json format 
    r = json.load(f)

a = r["variant_A"]
b = r["variant_B"]

#create chart with two panels
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

#left panel: bar chart comparing conversion rates of A vs B
rates = [a["rate"], b["rate"]]
labels = ["A (control)", "B (new version)"]
colors = ["#0B2545", "#0E7C7B"]
bars = ax1.bar(labels, rates, color=colors, alpha=0.85)

#add the percentage number on top of each bar
for bar, rate in zip(bars, rates):
    ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.002,
             f"{rate:.2%}", ha="center", fontsize=13, fontweight="bold")

ax1.set_ylabel("Conversion rate")
ax1.set_title("Conversion rate: A vs B")
ax1.set_ylim(0, max(rates) * 1.4)
ax1.grid(axis="y", alpha=0.3)

#right panel: show the lift and its confidence interval on a line
ax2.axvline(0, color="#999", lw=1, ls="--") #zero line - if CI crosses this, result is not conclusive
ax2.errorbar(r["absolute_lift"], 0,
             xerr=[[r["absolute_lift"] - r["ci_95_low"]],
                   [r["ci_95_high"] - r["absolute_lift"]]],
             fmt="o", color="#0E7C7B", markersize=12, capsize=10, lw=2)
ax2.text(r["absolute_lift"], 0.1, f"  Lift: {r['absolute_lift']:+.2%}",
         fontsize=12, fontweight="bold")
ax2.set_yticks([])
ax2.set_xlabel("How much better is B compared to A")
ax2.set_title(f"95% confidence interval for the lift\np = {r['p_value']:.4f}")
ax2.set_ylim(-0.5, 0.5)
ax2.grid(axis="x", alpha=0.3)

plt.tight_layout()
plt.savefig("outputs/ab_results.png", dpi=130)
plt.close()
print("Chart saved to outputs/ab_results.png")

#decide on the verdict
if r["significant"] and r["absolute_lift"] > 0:
    verdict = f"SHIP IT - B wins! It converts {r['absolute_lift']:+.2%} more users ({r['relative_lift']:+.1%} relatively). This is statistically confirmed (p = {r['p_value']:.4f})."
elif r["significant"] and r["absolute_lift"] < 0:
    verdict = f"DO NOT SHIP - B is worse! It converts {abs(r['absolute_lift']):.2%} fewer users. This is statistically confirmed (p = {r['p_value']:.4f})."
else:
    verdict = f"NOT CONCLUSIVE - the difference of {r['absolute_lift']:+.2%} could just be random noise (p = {r['p_value']:.4f}). Need more data or the variants are truly the same."

#write the report
report = f"""# A/B Test Report

## Results

| Variant | Users | Converted | Rate |
|---------|-------|-----------|------|
| A (control)   | {a['n']} | {a['conversions']} | {a['rate']:.2%} |
| B (new version) | {b['n']} | {b['conversions']} | {b['rate']:.2%} |

- Absolute lift: {r['absolute_lift']:+.2%}
- Relative lift: {r['relative_lift']:+.2%}
- 95% confidence interval: [{r['ci_95_low']:+.2%}, {r['ci_95_high']:+.2%}]
- p-value: {r['p_value']:.6f}

## Verdict

{verdict}

## How to read this

- Absolute lift = how many more percentage points B converts vs A
- Relative lift = how much better B is in % terms relative to A
- p-value below 0.05 = the difference is real, not random
- Confidence interval = the true lift is likely somewhere in this range
- If the confidence interval includes zero = result is not conclusive
"""

with open("outputs/report.md", "w") as f:
    f.write(report)

print("Report saved to outputs/report.md")
print("Done - check the outputs folder!")

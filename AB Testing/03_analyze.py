#analyze the A/B test - compare conversion rates between group A and group B
#import libraries
import polars as pl
import numpy as np
import json
import os
from scipy import stats

ALPHA = 0.05 #if p-value is below this the difference is real, not random chance

#load clean data
df = pl.read_csv("data/clean_data.csv")

#get group A numbers
group_a = df.filter(pl.col("variant") == "A")
n_a = group_a.height                           #total users in A
conv_a = group_a["converted"].sum()            #users who converted in A
rate_a = conv_a / n_a                          #conversion rate for A
#total number of conversion / total number of users 


#get group B numbers
group_b = df.filter(pl.col("variant") == "B")
n_b = group_b.height                           #total users in B
conv_b = group_b["converted"].sum()            #users who converted in B
rate_b = conv_b / n_b                          #conversion rate for B

print(f"Group A: {conv_a} out of {n_a} converted = {rate_a:.2%}")  #.2% means 2 decimal places, it is formating 
print(f"Group B: {conv_b} out of {n_b} converted = {rate_b:.2%}")

#how much better (or worse) is B compared to A
abs_lift = rate_b - rate_a                     #e.g. 0.02 means 2 percentage points better
rel_lift = abs_lift / rate_a                   #e.g. 0.17 means 17% relatively better
print(f"\nAbsolute lift: {abs_lift:+.2%}")
print(f"Relative lift: {rel_lift:+.2%}")

# rate_B=b=0.14, rate_a=0.12 
#rel_lift = 0.2/0.12=0.1667 = so the b is 16.67% better 


#run the z-test - are the two conversion rates actually different or just random noise?
p_pool = (conv_a + conv_b) / (n_a + n_b)      #Combines all conversions and divides them by the total number of visitors from both groups.
se = np.sqrt(p_pool * (1 - p_pool) * (1/n_a + 1/n_b)) #standard error ,even a tiny difference in conversion rates can be statistically significant.
z_stat = (rate_b - rate_a) / se  # A Z-score above +1.96 or below -1.96 generally indicates a real effect.
                                 #z score Calculates how many standard deviations away your observed difference (rate_b - rate_a) is from zero.   
p_value = 2 * (1 - stats.norm.cdf(abs(z_stat))) #two-sided p-value Calculates the probability of seeing a difference this large purely by pure luck.
#If p_value < 0.05: The result is statistically significant. 
# The difference is real, and it is safe to launch Group B.If p_value >= 0.05: 
# The result is not significant. The difference is likely just random noise, and you
#  need more data or a better test variant.


print(f"\nz = {z_stat:.4f}, p = {p_value:.6f}") #f is decimal places, so 4 decimal, 6 decimal
print(f"Result is significant: {'YES - B is better!' if p_value < ALPHA and abs_lift > 0 else 'NO - not enough evidence'}")

#95% confidence interval - the real lift is likely somewhere in this range
ci_low  = abs_lift - 1.96 * se   #1.96 is a fixed magic number that comes from statistics — it represents 95% confidence on a bell curve.
ci_high = abs_lift + 1.96 * se
print(f"95% confidence interval for lift: [{ci_low:+.2%}, {ci_high:+.2%}]") #2decimal

#save results for the presentation step
os.makedirs("outputs", exist_ok=True)

results = {
    "alpha": ALPHA,
    "variant_A": {"n": int(n_a), "conversions": int(conv_a), "rate": float(rate_a)},
    "variant_B": {"n": int(n_b), "conversions": int(conv_b), "rate": float(rate_b)},
    "absolute_lift": float(abs_lift),
    "relative_lift": float(rel_lift),
    "z_statistic": float(z_stat),
    "p_value": float(p_value),
    "significant": bool(p_value < ALPHA),
    "ci_95_low": float(ci_low),
    "ci_95_high": float(ci_high),
}

with open("outputs/results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nSaved to outputs/results.json")

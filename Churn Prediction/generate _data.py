#this code is used for synthetic data generation so we can use them later 

import numpy as np
import polars as pl 

np.random.seed(42)
n = 5000
days_since_login   = np.random.exponential(15, n)     # most login often, a few gone for months
features_used      = np.random.randint(1, 20, n)       # how many product features they use (1-19)
usage_trend        = np.random.uniform(-1, 1, n)        # -1 dropping fast, +1 growing fast
support_tickets    = np.random.poisson(1.5, n)          # number of complaints (whole numbers)
contract_days_left = np.random.randint(0, 365, n)       # days left on contract
monthly_revenue    = np.random.uniform(50, 800, n)      # how much they pay per month
tenure_days        = np.random.randint(30, 1825, n)     # how long they have been a customer
price_increase     = np.random.binomial(1, 0.2, n)      # 1 = got a price increase, 0 = did not

# churn score — higher = more likely to churn
churn_score = (
    0.03 * days_since_login      # longer gap since login → bad
  - 0.05 * features_used         # more features used → good
  - 0.3  * usage_trend           # usage growing → good
  + 0.15 * support_tickets       # more complaints → bad
  - 0.002* contract_days_left    # contract expiring soon → bad
  + 0.4  * price_increase        # got price increase → bad
  + np.random.normal(0, 0.3, n)  # random noise — life is unpredictable
)

churn_prob = 1 / (1 + np.exp(-churn_score))  # squeeze score into 0-100%
churned    = (churn_prob > 0.55).astype(int)  # above 55% = churned

# for survival analysis — when did/will they leave?
days_to_churn = np.where(
    churned == 1,
    np.random.randint(1, 90, n),  # churned customers left within 90 days
    tenure_days                    # retained customers — still active
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
print(f"Total customers:  {n:,}")
print(f"Churned:          {churned.sum():,} ({churn_rate:.1f}%)")
print(f"Retained:         {(1-churned).sum():,} ({100-churn_rate:.1f}%)")

df.write_csv("syn_data.csv")
print("Data saved to syn_data.csv")



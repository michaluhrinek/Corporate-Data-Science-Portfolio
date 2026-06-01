#generating data for A/B testing - conversion rate
#import libraries
import polars as pl
import numpy as np
import os

#settings
n_users = 5000  #number of users per group
rate_a = 0.12
rate_b = 0.14

os.makedirs("data", exist_ok=True)

rng = np.random.default_rng(seed=42) #seed=42 means we get same results every run

#generate user IDs - using a smaller range so some IDs repeat naturally (simulates duplicates)
user_ids_a = rng.integers(10000, 14000, size=n_users).tolist()
user_ids_b = rng.integers(10000, 14000, size=n_users).tolist()

#generate group A users - each user either converted (1) or didnt (0)
converted_a = rng.binomial(1, rate_a, size=n_users).tolist() #12% chance of each user to convert
variant_a = ["A"] * n_users

#generate group B users
converted_b = rng.binomial(1, rate_b, size=n_users).tolist() #14% chance of each user to convert
variant_b = ["B"] * n_users

#combine both groups into one dataframe
df = pl.DataFrame({
    "user_id":  user_ids_a  + user_ids_b,
    "variant":  variant_a   + variant_b,
    "converted": converted_a + converted_b
})

#shuffle rows so A and B are mixed like during a real test
df = df.sample(fraction=1.0, shuffle=True, seed=42)

#save the data
df.write_csv("data/raw_data.csv")

print(f"Generated {len(df)} users ({n_users} per variant)")
print(f"Saved to data/raw_data.csv")

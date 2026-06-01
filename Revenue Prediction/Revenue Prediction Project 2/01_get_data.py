#generate synthetic daily sales data with realistic patterns
#import libraries
import polars as pl
import numpy as np
import os

#settings - change these to adjust the generated data
START_DATE = "2022-01-01"
END_DATE   = "2024-12-31"
BASELINE        = 1000  #starting daily revenue
GROWTH_PER_DAY  = 0.4   #how much revenue grows each day (slow upward trend)
WEEKLY_AMP      = 200   #how strong the weekly up/down pattern is
NOISE_STD       = 80    #how much random noise to add each day

os.makedirs("data", exist_ok=True)

rng = np.random.default_rng(seed=42)

#create a list of every day from start to end
dates = pl.date_range(pl.date(2022, 1, 1), pl.date(2024, 12, 31), "1d", eager=True)
n = len(dates)

#trend: revenue slowly grows over time
trend = BASELINE + np.arange(n) * GROWTH_PER_DAY

#weekly seasonality: revenue goes up and down in a 7-day wave (weekends vs weekdays)
weekly = WEEKLY_AMP * np.sin(2 * np.pi * np.arange(n) / 7)

#weekend boost: extra revenue on saturday and sunday
day_of_week = dates.dt.weekday().to_numpy()
weekend_boost = np.where(day_of_week >= 5, 150, 0)

#random daily noise: real sales are never perfectly smooth
noise = rng.normal(0, NOISE_STD, size=n)

#random promotional spikes: 15 random days with big sales events
spikes = np.zeros(n)
spike_days = rng.choice(n, size=15, replace=False)
spikes[spike_days] = rng.uniform(300, 700, size=15)

#combine everything into final revenue, clip so it never goes below 0
revenue = trend + weekly + weekend_boost + noise + spikes
revenue = np.clip(revenue, 0, None)

df = pl.DataFrame({"date": dates, "revenue": revenue})
df.write_csv("data/raw_data.csv")

print(f"Generated {len(df)} days of sales data")
print(f"Date range: {START_DATE} to {END_DATE}")
print(f"Saved to data/raw_data.csv")

#feature engineering - add useful columns so the model can learn patterns
#import libraries
import polars as pl

#load raw data
df = pl.read_csv("data/raw_data.csv", try_parse_dates=True)
df = df.sort("date")
print(f"Loaded {len(df)} rows")

#calendar features - tell the model what day/month it is
df = df.with_columns([
    pl.col("date").dt.weekday().alias("dayofweek"),     #0=monday, 6=sunday
    pl.col("date").dt.month().alias("month"),            #1-12
    pl.col("date").dt.ordinal_day().alias("dayofyear"),  #1-365
    (pl.col("date").dt.weekday() >= 5).cast(pl.Int32).alias("is_weekend") #1 if weekend
])

#lag features - show the model what revenue was X days ago
#this is how the model "remembers" the past
df = df.with_columns([
    pl.col("revenue").shift(1).alias("lag_1"),   #revenue yesterday
    pl.col("revenue").shift(7).alias("lag_7"),   #revenue 1 week ago
    pl.col("revenue").shift(14).alias("lag_14"), #revenue 2 weeks ago
    pl.col("revenue").shift(28).alias("lag_28"), #revenue 4 weeks ago
])

#rolling features - show the model the recent average and how volatile it has been
#shift(1) means we dont include todays value - that would be cheating
df = df.with_columns([
    pl.col("revenue").shift(1).rolling_mean(window_size=7).alias("roll_mean_7"),   #avg last 7 days
    pl.col("revenue").shift(1).rolling_std(window_size=7).alias("roll_std_7"),     #volatility last 7 days
    pl.col("revenue").shift(1).rolling_mean(window_size=28).alias("roll_mean_28"), #avg last 28 days
    pl.col("revenue").shift(1).rolling_std(window_size=28).alias("roll_std_28"),   #volatility last 28 days
])

#drop the first rows that have missing lag values (e.g. day 1 has no lag_28 yet)
rows_before = len(df)
df = df.drop_nulls()
print(f"Dropped {rows_before - len(df)} rows with missing lag/rolling values")
print(f"Features ready: {df.columns}")

df.write_csv("data/features.csv")
print(f"Saved to data/features.csv")

#cleaning and preparing of the data 
#import libraries 
import polars as pl

SPLIT_DATE = "2024-01-01"  #definition of the date for before and after 

#load the raw data we downloaded in step 1
df = pl.read_csv("data/raw_data.csv", try_parse_dates=True)
print(f"Loaded {len(df)} rows")

#remove outliers - values too far from the average (beyond 5 standard deviations)
mean = df["value"].mean()
std = df["value"].std()
rows_before = len(df)
df = df.filter((pl.col("value") - mean).abs() <= 5 * std)
print(f"Removed {rows_before - len(df)} outliers")

#split into two groups based on the split date into A and B 
df = df.with_columns(
    pl.when(pl.col("date") < pl.lit(SPLIT_DATE).str.to_date())
    .then(pl.lit("A"))
    .otherwise(pl.lit("B"))
    .alias("group")
)

#count how many rows are in each group
count_a = df.filter(pl.col("group") == "A").height
count_b = df.filter(pl.col("group") == "B").height
print(f"Group A (before {SPLIT_DATE}): {count_a} rows")
print(f"Group B (after  {SPLIT_DATE}): {count_b} rows")

#save the cleaned data
df.write_csv("data/clean_data.csv")
print("Saved to data/clean_data.csv")

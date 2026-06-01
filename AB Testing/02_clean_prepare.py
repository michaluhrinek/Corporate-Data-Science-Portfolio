#validate and clean the A/B test data
#import libraries
import polars as pl
from scipy import stats

#load the raw data
df = pl.read_csv("data/raw_data.csv")
print(f"Loaded {len(df)} rows")
print("-" * 40)

# ── CHECK 1: DUPLICATES ───────────────────────────────────────────────────────
#we keep only the first time we saw each user
duplicates = df.filter(df["user_id"].is_duplicated()) #finds duplicates 
print(f"[DUPLICATES] Removed: {len(duplicates)} duplicate users") #duplicates, how many ? 
df = df.unique(subset=["user_id"], keep="first") #keep only first user ID, second time or more it appears, we delete it 
print(f"[DUPLICATES] Rows remaining: {len(df)}")
print("-" * 40)

# ── CHECK 2: MISSING DATA ─────────────────────────────────────────────────────
#check if any values are blank/null in any column
missing_user_id   = df["user_id"].null_count()
missing_variant   = df["variant"].null_count()
missing_converted = df["converted"].null_count()
print(f"[MISSING] Missing user_id:   {missing_user_id}")
print(f"[MISSING] Missing variant:   {missing_variant}")
print(f"[MISSING] Missing converted: {missing_converted}")

#drop any rows that have missing values
df = df.drop_nulls()  #drops the row if even 1 column data is mssing 
print(f"[MISSING] Rows after dropping nulls: {len(df)}")
print("-" * 40) #just ----x 40 so it creates a line 

# ── CHECK 3: OUTLIERS ─────────────────────────────────────────────────────────
#converted is only 0 or 1 so outliers cant exist here
#if we had a revenue column we would check for extreme values like $25000 whale purchases
#we just verify no unexpected values snuck in
invalid_converted = df.filter(~pl.col("converted").is_in([0, 1]))
print(f"[OUTLIERS] Rows with invalid converted values (not 0 or 1): {len(invalid_converted)}")
df = df.filter(pl.col("converted").is_in([0, 1]))
print("-" * 40)  #just ----x 40 so it creates a line 

# ── CHECK 4: VALID VARIANTS ONLY ─────────────────────────────────────────────
df = df.filter(pl.col("variant").is_in(["A", "B"]))
count_a = df.filter(pl.col("variant") == "A").height
count_b = df.filter(pl.col("variant") == "B").height
print(f"[GROUPS] Variant A: {count_a} users")
print(f"[GROUPS] Variant B: {count_b} users")
print("-" * 40)

# ── CHECK 5: 50/50 SPLIT ─────────────────────────────────────────────────────
total = count_a + count_b
expected = total / 2
chi2, srm_p = stats.chisquare([count_a, count_b], [expected, expected])
if srm_p < 0.01:
    print(f"[SPLIT] WARNING: groups are not balanced (p={srm_p:.4f}) - randomization may be broken")
else:
    print(f"[SPLIT] Group balance check: OK (p={srm_p:.4f})")
print("-" * 40)

#save cleaned data
df.write_csv("data/clean_data.csv")
print(f"Saved to data/clean_data.csv ({len(df)} rows)")

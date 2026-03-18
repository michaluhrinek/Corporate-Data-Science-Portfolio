# Exploratory Data Analysis of Payments Errors
#import libraries 
import polars as pl
import os

# Define the correct file path for the errors dataset
error_file_path = r"C:\Users\X\Downloads\payments\payments_errors_2025.csv"       #change the X and rest of the path as per your system
output_path = r"C:\Users\X\Downloads\payments\payments_errors_analytics_2025.csv"   #change the X and rest of the path as per your system

# ─── LOAD ERROR DATA ───────────────────────────────────────────────────────────
if os.path.exists(error_file_path):
    print(f"Loading error data from: {error_file_path}")
    error_df = pl.read_csv(error_file_path, encoding="utf8-lossy", infer_schema_length=10000)
    print("\nError data loaded successfully!")
    print(f"Shape of Error Dataset: {error_df.shape}")
    print(f"Columns in Error Dataset:\n{error_df.columns}")
else:
    print(f"Error file not found: {error_file_path}")
    exit()

# Preview data
print("\nSample Error Data:")
print(error_df.head())

# ─── PREPROCESS INPUT DATA ─────────────────────────────────────────────────────
# Parse datetime columns (Ensure datetime parsing matches error_df schema)
datetime_columns = ["Created", "Actual Start", "Actual End", "Closed"]
for col in datetime_columns:
    if col in error_df.columns:
        error_df = error_df.with_columns(
            pl.col(col).str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S.%f", strict=False).alias(col)
        )
print("\nDatetime columns parsed successfully.")

# ─── CALCULATE TIME METRICS IN HOURS ───────────────────────────────────────────
error_df = error_df.with_columns([
    # Processing Time (Actual End - Actual Start)
    (
        (pl.col("Actual End") - pl.col("Actual Start")).dt.total_seconds() / 3600
    ).alias("Processing Time (hrs)"),

    # Response Time (Actual Start - Created)
    (
        (pl.col("Actual Start") - pl.col("Created")).dt.total_seconds() / 3600
    ).alias("Response Time (hrs)"),

    # Total Time (Closed - Created)
    (
        (pl.col("Closed") - pl.col("Created")).dt.total_seconds() / 3600
    ).alias("Total Time (hrs)"),
])

# ─── SUMMARY: OVERALL AVERAGES ─────────────────────────────────────────────────
print("=" * 60)
print("         PAYMENTS ERRORS - TIME ANALYTICS 2025")
print("=" * 60)

# Total Records and Closed Tickets Count
print(f"\nTotal Records Loaded    : {error_df.shape[0]:,}")
print(f"Closed Tickets (timed)  : {error_df.filter(pl.col('Total Time (hrs)').is_not_null()).shape[0]:,}")

print(f"\n--- Overall Average Times ---")
print(
    error_df.select([
        pl.col("Processing Time (hrs)").mean().alias("Avg Processing Time (hrs)"),
        pl.col("Response Time (hrs)").mean().alias("Avg Response Time (hrs)"),
        pl.col("Total Time (hrs)").mean().alias("Avg Total Time (hrs)"),
    ])
)

# ─── BY TEAM ───────────────────────────────────────────────────────────────────
print(f"\n--- Average Times by Team ---")
print(
    error_df.group_by("Assignment Group").agg([
        pl.col("Processing Time (hrs)").mean().round(2).alias("Avg Processing (hrs)"),
        pl.col("Response Time (hrs)").mean().round(2).alias("Avg Response (hrs)"),
        pl.col("Total Time (hrs)").mean().round(2).alias("Avg Total (hrs)"),
        pl.col("Number").count().alias("Total Errors"),
    ]).sort("Total Errors", descending=True)
)

# ─── BY PROCESS ────────────────────────────────────────────────────────────────
print(f"\n--- Average Times by Process ---")
print(
    error_df.group_by("Process").agg([
        pl.col("Processing Time (hrs)").mean().round(2).alias("Avg Processing (hrs)"),
        pl.col("Response Time (hrs)").mean().round(2).alias("Avg Response (hrs)"),
        pl.col("Total Time (hrs)").mean().round(2).alias("Avg Total (hrs)"),
        pl.col("Number").count().alias("Total Errors"),
    ]).sort("Total Errors", descending=True)
)

# ─── BY PRIORITY ───────────────────────────────────────────────────────────────
print(f"\n--- Average Times by Priority ---")
print(
    error_df.group_by("Priority").agg([
        pl.col("Processing Time (hrs)").mean().round(2).alias("Avg Processing (hrs)"),
        pl.col("Response Time (hrs)").mean().round(2).alias("Avg Response (hrs)"),
        pl.col("Total Time (hrs)").mean().round(2).alias("Avg Total (hrs)"),
        pl.col("Number").count().alias("Total Errors"),
    ]).sort("Avg Total (hrs)", descending=True)
)

# ─── BY MONTH ──────────────────────────────────────────────────────────────────
print(f"\n--- Monthly Error Count per Team ---")
print(
    error_df.with_columns(pl.col("Created").dt.month().alias("Month"))
    .group_by(["Month", "Assignment Group"])
    .agg(pl.col("Number").count().alias("Errors"))
    .sort(["Month", "Assignment Group"])
)

# ─── SAVE ENRICHED FILE ────────────────────────────────────────────────────────
error_df.write_csv(output_path)
print(f"\nEnriched dataset saved to: {output_path}")

# ─── PREVIEW ───────────────────────────────────────────────────────────────────
print(f"\n--- Preview (first 5 rows with time columns) ---")
print(error_df.select([
    "Number", "Assignment Group", "Process", "Priority",
    "Response Time (hrs)", "Processing Time (hrs)", "Total Time (hrs)"
]).head(5))
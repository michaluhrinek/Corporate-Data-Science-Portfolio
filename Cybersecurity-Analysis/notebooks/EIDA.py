#Exploratory Data Analysis

# Import necessary libraries
import polars as pl
import os

# Define file paths
input_file_path = r"C:\Users\X\Downloads\synthetic_cybersecurity_bank_data.csv" #input instead of X your user profile, your ID
output_file_path = r"C:\Users\X\Downloads\EIDA_data.csv"         #input instead of X your user profile, your ID

# Check if file exists
if not os.path.exists(input_file_path):
    print(f"File not found: {input_file_path}")
    exit()

# Load data
print(f"Loading data from: {input_file_path}")
try:
    df = pl.read_csv(
        input_file_path,
        encoding="utf8-lossy",
        ignore_errors=True,  # Skip problematic rows
        truncate_ragged_lines=True,  # Handle inconsistent column rows
    )
    print("\nData loaded successfully!")
    print(f"Shape of Dataset: {df.shape}")
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# Display the column names in the dataset
print("\nColumns in the dataset:")
print(df.columns)

# Quick look at the first few rows
print("\nSample Data:")
print(df.head())

# === Basic EIDA Analysis ===
# 1. Summary statistics
print("\n=== Summary Statistics ===")
print(df.describe())

# 2. Check for Null Values
print("\n=== NULL VALUES ANALYSIS ===")
null_counts = df.select(
    [pl.col(col_name).null_count().alias(f"Null Count for {col_name}") for col_name in df.columns]
)
print(null_counts)

# === Check for Duplicate Records ===
print("\n=== CHECK FOR DUPLICATE RECORDS ===")
duplicates_count = df.filter(df.is_duplicated()).height
print(f"Number of Duplicate Records: {duplicates_count}")
if duplicates_count > 0:
    print("\nSample Duplicate Records:")
    print(df.filter(df.is_duplicated()).head())

# === Check for Inconsistent Rows ===
print("\n=== CHECK FOR INCONSISTENCY IN DATETIME VALUES ===")
inconsistent_data = df.filter(
    (pl.col("Created") > pl.col("Start Date")) | (pl.col("Start Date") > pl.col("Closed"))
)

print(f"Number of Rows with Inconsistent Datetime Values: {inconsistent_data.height}")
if inconsistent_data.height > 0:
    print("\nSample Rows with Inconsistent Data:")
    print(inconsistent_data.head())

# Parse datetime columns using ISO 8601 format
datetime_columns = ["Created", "Start Date", "Closed"]
for col in datetime_columns:
    if col in df.columns:
        df = df.with_columns(
            pl.col(col).str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S.%f", strict=False).alias(col)
        )

print("\nDatetime columns parsed successfully!")
print(df.select(["Created", "Start Date", "Closed"]).head(10))

# Populate calculated columns===create Time to Response Hours, Processing Time Hours, Total Time Hours columns 
# Time to Response Hours
if all(col in df.columns for col in ["Created", "Start Date"]):
    df = df.with_columns(
        ((pl.col("Start Date") - pl.col("Created")).dt.total_seconds() / 3600).alias("Time to Response Hours")
    )
    print("\nAdded 'Time to Response Hours' column!")

# Processing Time Hours
if all(col in df.columns for col in ["Start Date", "Closed"]):
    df = df.with_columns(
        ((pl.col("Closed") - pl.col("Start Date")).dt.total_seconds() / 3600).alias("Processing Time Hours")
    )
    print("\nAdded 'Processing Time Hours' column!")

# Total Time Hours
if all(col in df.columns for col in ["Created", "Closed"]):
    df = df.with_columns(
        ((pl.col("Closed") - pl.col("Created")).dt.total_seconds() / 3600).alias("Total Time Hours")
    )
    print("\nAdded 'Total Time Hours' column!")

# Preview Calculated Columns
print("\nSample Calculated Columns:")
print(df.select(["Time to Response Hours", "Processing Time Hours", "Total Time Hours"]).head(10))

#test KPI and Average 
# 4. KPI_breach: Based on Priority and Processing Time Hours
if "KPI_breach" not in df.columns and all(col in df.columns for col in ["Priority", "Processing Time Hours"]):
    df = df.with_columns(
        (
            # Assign conditions based on priority thresholds
            pl.when((pl.col("Priority") == "Critical") & (pl.col("Processing Time Hours") > 4)).then(1)
            .when((pl.col("Priority") == "High") & (pl.col("Processing Time Hours") > 8)).then(1)
            .when((pl.col("Priority") == "Medium") & (pl.col("Processing Time Hours") > 24)).then(1)
            .when((pl.col("Priority") == "Low") & (pl.col("Processing Time Hours") > 48)).then(1)
            .otherwise(0)
        ).alias("KPI_breach")
    )

# Fill missing values with defaults for consistency
columns_to_clean = ["Time to Response Hours", "Processing Time Hours", "Total Time Hours", "KPI_breach"]
df = df.with_columns(
    [(pl.col(col).fill_null(0).alias(col)) for col in columns_to_clean]
)
# Display summary of calculated columns
print("\n=== Summary of Calculated Columns ===")
print(f"Columns in DataFrame: {df.columns}")
print(f"Shape: {df.shape}")

#averages of Time to Response, Processing Time and Total Time calculations
if "Time to Response Hours" in df.columns:
    print(f"Average Time to Response Hours: {df['Time to Response Hours'].mean():.2f}")
if "Processing Time Hours" in df.columns:
    print(f"Average Processing Time Hours: {df['Processing Time Hours'].mean():.2f}")
if "Total Time Hours" in df.columns:
    print(f"Average Total Time Hours: {df['Total Time Hours'].mean():.2f}")

print(df.select(["Priority","Processing Time Hours","KPI_breach"]).head(10))

# Save updated DataFrame
df.write_csv(output_file_path)

print(f"\nUpdated data saved to: {output_file_path}")

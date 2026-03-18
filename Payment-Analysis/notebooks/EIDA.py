# Exploratory Data Analysis of EIDA Payments
# Import necessary libraries
import polars as pl
import os

# Define file paths
volume_file_path = r"C:\Users\X\Downloads\payments\payments_volume_2025.csv"   #change the X and rest of the path as per your system
error_file_path = r"C:\Users\X\Downloads\payments\payments_errors_2025.csv"    #change the X and rest of the path as per your system

# Load volume data - volume_df
if os.path.exists(volume_file_path):
    print(f"Loading volume data from: {volume_file_path}")
    volume_df = pl.read_csv(volume_file_path, encoding="utf8-lossy", ignore_errors=True)
    print("\nVolume data loaded successfully!")
    print(f"Shape of Volume Dataset: {volume_df.shape}")
    print(f"Columns in Volume Dataset:\n{volume_df.columns}")
else:
    print(f"Volume file not found: {volume_file_path}")
    exit()

# Load error data - error_df
if os.path.exists(error_file_path):
    print(f"Loading error data from: {error_file_path}")
    error_df = pl.read_csv(error_file_path, encoding="utf8-lossy", ignore_errors=True)
    print("\nError data loaded successfully!")
    print(f"Shape of Error Dataset: {error_df.shape}")
    print(f"Columns in Error Dataset:\n{error_df.columns}")
else:
    print(f"Error file not found: {error_file_path}")
    exit()

# Preview data
print("\nSample Volume Data:")
print(volume_df.head())  # Show sample of the volume data for verification

print("\nSample Error Data:")
print(error_df.head())   # Show sample of the error data for verification

# === Analyzing the Volume Data ===
# get columns into same format for calculations
datetime_columns = ["Created", "Actual Start", "Actual End", "Closed"]
for col in datetime_columns:
    if col in volume_df.columns:
        volume_df = volume_df.with_columns(
            pl.col(col).str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S.%f", strict=False).alias(col)
        )

print("\nDatetime columns parsed successfully for Volume File!")

# Response Time Hours: Actual Start - Created
if all(col in volume_df.columns for col in ["Created", "Actual Start"]):
    volume_df = volume_df.with_columns(
        ((pl.col("Actual Start") - pl.col("Created")).dt.total_seconds() / 3600).alias("Response Time Hours")
    )

# Processing Time Hours: Actual End - Actual Start
if all(col in volume_df.columns for col in ["Actual Start", "Actual End"]):
    volume_df = volume_df.with_columns(
        ((pl.col("Actual End") - pl.col("Actual Start")).dt.total_seconds() / 3600).alias("Processing Time Hours")
    )

# Total Time Hours: Closed - Created
if all(col in volume_df.columns for col in ["Created", "Closed"]):
    volume_df = volume_df.with_columns(
        ((pl.col("Closed") - pl.col("Created")).dt.total_seconds() / 3600).alias("Total Time Hours")
    )

# Null handling for consistency in calculated columns
time_columns_volume = ["Response Time Hours", "Processing Time Hours", "Total Time Hours"]
volume_df = volume_df.with_columns(
    [pl.col(col).fill_null(0).alias(col) for col in time_columns_volume]
)

# Preview calculated columns in Volume file
print("\nSample Time Metrics for Volume File:")
print(volume_df.select(time_columns_volume).head())  # Display sample of calculated columns


# EIDA Analysis for volume_df
print("\n=== Exploratory Data Analysis (EIDA) for Volume Dataset ===")

# Display the column names in the dataset
print("\nColumns in the Volume Dataset:")
print(volume_df.columns)

# Quick look at the first few rows of the dataset
print("\nSample Data:")
print(volume_df.head())

# === Basic EIDA Analysis ===
# Summary statistics
print("\n=== Summary Statistics ===")
print(volume_df.describe())

# Check for Null Values
print("\n=== NULL VALUES ANALYSIS ===")
null_counts = volume_df.select(
    [pl.col(col_name).null_count().alias(f"Null Count for {col_name}") for col_name in volume_df.columns]
)
print("\nNull Counts by Column:")
print(null_counts)


#-------------------------------------------------------------------Error handeling part-----------------------------------------
# get columns in Error File into same data format for calculations
for col in datetime_columns:
    if col in error_df.columns:
        error_df = error_df.with_columns(
            pl.col(col).str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S.%f", strict=False).alias(col)
        )

print("\nDatetime columns parsed successfully for Error File!")

# Response Time Hours: Actual Start - Created (similar to the volume file logic)
if all(col in error_df.columns for col in ["Created", "Actual Start"]):
    error_df = error_df.with_columns(
        ((pl.col("Actual Start") - pl.col("Created")).dt.total_seconds() / 3600).alias("Response Time Hours")
    )

# Processing Time Hours: Actual End - Actual Start
if all(col in error_df.columns for col in ["Actual Start", "Actual End"]):
    error_df = error_df.with_columns(
        ((pl.col("Actual End") - pl.col("Actual Start")).dt.total_seconds() / 3600).alias("Processing Time Hours")
    )

# Total Time Hours: Closed - Created
if all(col in error_df.columns for col in ["Created", "Closed"]):
    error_df = error_df.with_columns(
        ((pl.col("Closed") - pl.col("Created")).dt.total_seconds() / 3600).alias("Total Time Hours")
    )

# Null handling for consistency
time_columns_error = ["Response Time Hours", "Processing Time Hours", "Total Time Hours"]
error_df = error_df.with_columns(
    [pl.col(col).fill_null(0).alias(col) for col in time_columns_error]
)

# Preview calculated columns in Error file
print("\nSample Time Metrics for Errors File:")
print(error_df.select(time_columns_error).head())  # Display sample of calculated columns

#-------------------------- EIDA Analysis for error_df -----------------------------------------
# EIDA Analysis for error_df
print("\n=== Exploratory Data Analysis (EIDA) for Error Dataset ===")

# Display the column names in the dataset
print("\nColumns in the Error Dataset:")
print(error_df.columns)

# Quick look at the first few rows of the dataset
print("\nSample Data:")
print(error_df.head())

# === Basic EIDA Analysis ===

# Summary statistics
print("\n=== Summary Statistics ===")
print(error_df.describe())

# Check for Null Values
print("\n=== NULL VALUES ANALYSIS ===")
null_counts = error_df.select(
    [pl.col(col_name).null_count().alias(f"Null Count for {col_name}") for col_name in error_df.columns]
)
print("\nNull Counts by Column:")
print(null_counts)

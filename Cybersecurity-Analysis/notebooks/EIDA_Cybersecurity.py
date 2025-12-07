#EIDA
# Import necessary libraries
import polars as pl
import os

# Define the file path
file_path = r"C:\Users\Downloads\test_III_with_KPI_breach.csv"

# Check if file exists
if os.path.exists(file_path):
    print("File exists!")
    
    try:
        df = pl.read_csv(
            file_path,
            encoding="utf8-lossy",
            ignore_errors=True,  # Skip problematic rows
            truncate_ragged_lines=True  # Handle inconsistent columns
        )
        print(df)
        print(f"Shape: {df.shape}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("File not found!")

# Reading the CSV file again, even after file validation
df = pl.read_csv(r"C:\Users\Downloads\test_III_with_KPI_breach.csv", encoding="utf8-lossy", ignore_errors=True)


# Display the first 10 rows of the dataframe
new_df = df.head(10)
print(new_df)

# Print all the columns in the dataframe
print(df.columns)

# Select specific columns of interest
created_df = df.select("Created", "Number", "Priority", "Assignment group","Change Environment",
                        "Requested by", "State", "Short description", 
                        "Risk score",
                        "Actual end", "Actual start","Time to Response Hours","Processing Time Hours","Total Time Hours","KPI_breach",
                         "Urgency","Closed")
print(created_df)
final_data=created_df

#dataset overview
print("\n=== DATASET OVERVIEW ===")
print(f"Total Records: {final_data.height}")
print(f"Columns: {final_data.columns}")

# Summary Statistics for the DataFrame
print("\n=== SUMMARY STATISTICS ===")
print(final_data.describe())

# Check Column Data Types
print("\n=== COLUMN FORMATS ===")
print(final_data.schema)

# Check for Duplicates
print("\n=== CHECK FOR DUPLICATE RECORDS ===")
duplicates_count = final_data.filter(final_data.is_duplicated()).height
print(f"Number of Duplicate Records: {duplicates_count}")

if duplicates_count > 0:
    print("\nDuplicate Records:")
    print(final_data.filter(final_data.duplicated()).head())

# Check for Nulls
print("\n=== CHECK FOR NULL VALUES ===")
null_counts = final_data.select([
    pl.col(col_name).null_count().alias(f"Null Count in {col_name}")
    for col_name in final_data.columns
])
print(null_counts)


# Check if there are rows with inconsistent data (e.g., rows having `Created > Actual start`)
print("\n=== CHECK FOR INCONSISTENCY ===")
inconsistent_data = final_data.filter(
    (pl.col("Created") > pl.col("Actual start")) | 
    (pl.col("Actual start") > pl.col("Actual end"))
)
print(f"Number of Rows with Inconsistent Datetime Values: {inconsistent_data.height}")
if inconsistent_data.height > 0:
    print("\nRows with Inconsistent Data:")
    print(inconsistent_data.head())
    

# Show data quality summary
print("\n=== DATA QUALITY SUMMARY ===")
total_records = final_data.height
records_with_response_time = final_data.filter(pl.col("Time to Response Hours") > 0).height
records_with_processing_time = final_data.filter(pl.col("Processing Time Hours") > 0).height
records_with_total_time = final_data.filter(pl.col("Total Time Hours") > 0).height

# New KPI summary
records_meeting_kpi = final_data.filter(pl.col("KPI_breach") == 1).height
records_NOT_meeting_kpi = total_records - records_meeting_kpi
# Show data quality summary
print("\n=== DATA QUALITY SUMMARY ===")
total_records = final_data.height
records_with_response_time = final_data.filter(pl.col("Time to Response Hours") > 0).height
records_with_processing_time = final_data.filter(pl.col("Processing Time Hours") > 0).height
records_with_total_time = final_data.filter(pl.col("Total Time Hours") > 0).height
print(f"Total Records: {total_records}")
print(f"Total Records: {total_records}")
print(f"Records with Time to Response: {records_with_response_time} ({(records_with_response_time / total_records) * 100:.2f}%)")   
print(f"Records with Processing Time: {records_with_processing_time} ({(records_with_processing_time / total_records) * 100:.2f}%)")
print(f"Records with Total Time: {records_with_total_time} ({(records_with_total_time / total_records) * 100:.2f}%)")
print(f"Records meeting KPI: {records_meeting_kpi} ({(records_meeting_kpi / total_records) * 100:.2f}%)")
print(f"Records NOT meeting KPI: {records_NOT_meeting_kpi} ({(records_NOT_meeting_kpi / total_records) * 100:.2f}%)")


# Calculate total records and records with KPI_breach by priority
kpi_by_priority = final_data.group_by("Priority").agg([
    (pl.col("KPI_breach") == 0).sum().alias("Records Meeting KPI"),
    pl.col("KPI_breach").count().alias("Total Records")
])
# Add a new column that calculates the percentage of records meeting the KPI for each priority
kpi_by_priority = kpi_by_priority.with_columns(
    (pl.col("Records Meeting KPI") / pl.col("Total Records") * 100).alias("Percentage KPI Met")
)
# Print KPI percentage by priority
print("\n=== KPI Breach Percentage by Priority ===")
print(kpi_by_priority)


#EIDA part ==============================================================================
# 1. Which Assignment group has the most breaches?
assignment_group_breaches = final_data.filter(pl.col("KPI_breach") == 0) \
    .group_by("Assignment group") \
    .agg([
        pl.count().alias("Number of Breaches")
    ]) \
    .sort("Number of Breaches", descending=True)  # Sort by breaches in descending order

print("\n=== Assignment Group: Most Breaches ===")
print(assignment_group_breaches)

# 2. Which Requested by has the most breaches?
requested_by_breaches = final_data.filter(pl.col("KPI_breach") == 0) \
    .group_by("Requested by") \
    .agg([
        pl.count().alias("Number of Breaches")
    ]) \
    .sort("Number of Breaches", descending=True)  # Sort by breaches in descending order

print("\n=== Requested By: Most Breaches ===")
print(requested_by_breaches)

# 3. Breaches per Change Environment - Including Number and Percentage
# Step 1: Calculate total records and breaches for each Change Environment
environment_breaches = final_data.filter(pl.col("KPI_breach") == 0) \
    .group_by("Change Environment") \
    .agg([
        pl.count().alias("Number of Breaches")
    ])

# 3. Breaches per Change Environment - Including Number and Percentage
# Step 1: Calculate total breaches for each Change Environment
environment_breaches = final_data.filter(pl.col("KPI_breach") == 0) \
    .group_by("Change Environment") \
    .agg([
        pl.len().alias("Number of Breaches")  # Count rows with KPI_breach = 0
    ])  # Ensure Change Environment column exists in the dataset

# Step 2: Calculate total records per Change Environment
environment_total = final_data.group_by("Change Environment").agg([
    pl.len().alias("Total Records")  # Total number of rows per Change Environment
])

# Step 3: Join the breaches and totals to calculate percentage of breaches
environment_breach_summary = environment_breaches.join(environment_total, on="Change Environment") \
    .with_columns([
        (pl.col("Number of Breaches") / pl.col("Total Records") * 100).alias("Percentage of Breaches")
    ])

print("\n=== Number and Percentage of Breaches per Change Environment ===")
print(environment_breach_summary.sort("Percentage of Breaches", descending=True))  # Sort output by percentage of breaches



# Save the final dataframe to a CSV file
output_file_path = r"C:\Users\Downloads\EIDA_data.csv"
final_data.write_csv(output_file_path)

print(f"\nFinal data with time metrics and KPI checks saved to: {output_file_path}")
#Root Cause Analysis 

#import libraries 
import os
import polars as pl 
#define filepath ===========
# === Define File Paths ===
input_file_path = r"C:\Users\X\Downloads\synthetic_cybersecurity_bank_data.csv"    #input instead of X your user profile, your ID
output_file_path = r"C:\Users\X\Downloads\Root_Cause_Analysis_Output.csv"         #input instead of X your user profile, your ID

# === Step 1: Load the Dataset ===
print(f"Loading data from: {input_file_path}")

if not os.path.exists(input_file_path):
    print(f"File not found: {input_file_path}")
    exit()

try:
    # Load the dataset using Polars
    df = pl.read_csv(
        input_file_path,
        encoding="utf8-lossy",
        ignore_errors=True,  # Skip problematic rows
        truncate_ragged_lines=True,
    )
    print("\nData loaded successfully!")
    print(f"Shape of Dataset: {df.shape}")
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# Display column names and sample rows
print("\n=== Columns in the Dataset ===")
print(df.columns)
print("\n=== Sample Data ===")
print(df.head(10))


# === Step 2: Parse Datetime Columns ===
datetime_columns = ["Created", "Start Date", "Closed"]

# Verify and parse columns using ISO 8601
for col in datetime_columns:
    if col in df.columns:
        try:
            df = df.with_columns(
                pl.col(col).str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S.%f", strict=False).alias(col)
            )
        except Exception as e:
            print(f"Error parsing column `{col}`: {e}")

print("\n=== Parsed Datetime Columns ===")
print(df.select(datetime_columns).head())


# === Step 3: Populate Calculated Columns ===

# Time to Response Hours (Start Date - Created)
if all(col in df.columns for col in ["Created", "Start Date"]):
    df = df.with_columns(
        ((pl.col("Start Date") - pl.col("Created")).dt.total_seconds() / 3600).alias("Time to Response Hours")
    )

# Processing Time Hours (Closed - Start Date)
if all(col in df.columns for col in ["Start Date", "Closed"]):
    df = df.with_columns(
        ((pl.col("Closed") - pl.col("Start Date")).dt.total_seconds() / 3600).alias("Processing Time Hours")
    )

# Total Time Hours (Closed - Created)
if all(col in df.columns for col in ["Created", "Closed"]):
    df = df.with_columns(
        ((pl.col("Closed") - pl.col("Created")).dt.total_seconds() / 3600).alias("Total Time Hours")
    )

print("\n=== Sample Calculated Columns ===")
print(df.select(["Time to Response Hours", "Processing Time Hours", "Total Time Hours"]).head())


# === Step 4: Identify KPI Breaches ===
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
print("\n=== KPI Breaches Added ===")
print(df.select(["Priority", "Processing Time Hours", "KPI_breach"]).head())

# === Step 5: Root Cause Analysis ===

## A. KPI Breach Analysis by Priority
print("\n=== RCA: KPI Breach by Priority ===")
# Calculate total tickets per priority from the full dataset
total_tickets_per_priority = df.group_by("Priority").agg(
    pl.count().alias("Total Tickets")
)
# Calculate number of breaches and average processing time for breached tickets
breach_stats_priority = df.filter(pl.col("KPI_breach") == 1).group_by("Priority").agg(
    [
        pl.col("KPI_breach").count().alias("Number of Breaches"),
        pl.col("Processing Time Hours").mean().alias("Avg Processing Time (Hours)"),
    ]
)
# Join breach stats with total tickets per priority to get correct denominator
priority_rca = breach_stats_priority.join(total_tickets_per_priority, on="Priority", how="left").with_columns(
    (pl.col("Number of Breaches") / pl.col("Total Tickets") * 100).alias("Breach Percentage (%)")
).sort("Breach Percentage (%)", descending=True)
print(priority_rca)

## B. RCA by Assignment Group 
print("\n=== RCA: Breach by Assignment Group ===")
# Calculate total tickets per assignment group from the full dataset
total_tickets_per_group = df.group_by("Assignment Group").agg(
    pl.count().alias("Total Tickets")
)
# Calculate number of breaches and average processing time for breached tickets
breach_stats = df.filter(pl.col("KPI_breach") == 1).group_by("Assignment Group").agg(
    [
        pl.col("KPI_breach").count().alias("Number of Breaches"),
        pl.col("Processing Time Hours").mean().alias("Avg Processing Time (Hours)"),
    ]
)
# Join breach stats with total tickets per group to get correct denominator
assignment_rca = breach_stats.join(total_tickets_per_group, on="Assignment Group", how="left").with_columns(
    (pl.col("Number of Breaches") / pl.col("Total Tickets") * 100).alias("Breach Percentage (%)")
).sort("Breach Percentage (%)", descending=True)
print(assignment_rca)

## C. RCA by Reopen Count in Assignment Group
print("\n=== RCA: Analysis of Reopen Count ===")
# Calculate total tickets per assignment group from the full dataset
total_tickets_per_group = df.group_by("Assignment Group").agg(
    pl.count().alias("Total Tickets")
)
# Calculate total reopen count and average processing time for tickets with Reopen Count > 0
reopen_stats = df.filter(pl.col("Reopen Count") > 0).group_by("Assignment Group").agg(
    [
        pl.col("Reopen Count").sum().alias("Total Reopen Count"),
        pl.col("Processing Time Hours").mean().alias("Avg Processing Time (Hours)"),
    ]
)
# Join with total tickets per group to get correct denominator
reopen_rca = reopen_stats.join(total_tickets_per_group, on="Assignment Group", how="left").with_columns(
    (pl.col("Total Reopen Count") / pl.col("Total Tickets") * 100).alias("Reopen Percentage (%)")
).sort("Reopen Percentage (%)", descending=True)
print(reopen_rca)

## D. RCA by Risk Level
print("\n=== RCA: Breaches by Risk Level ===")
# Calculate total tickets per risk from the full dataset
total_tickets_per_risk = df.group_by("Risk").agg(
    pl.count().alias("Total Tickets")
)

# Calculate breaches per risk
risk_breaches = df.filter(pl.col("KPI_breach") == 1).group_by("Risk").agg(
    [
        pl.col("KPI_breach").count().alias("Number of Breaches"),
        pl.col("Processing Time Hours").mean().alias("Avg Processing Time (Hours)"),
    ]
)

# Join breaches with total tickets
risk_rca = risk_breaches.join(total_tickets_per_risk, on="Risk", how="left").with_columns(
    (pl.col("Number of Breaches") / pl.col("Total Tickets") * 100).alias("Breach Percentage (%)")
).sort("Breach Percentage (%)", descending=True)
print(risk_rca)


day = "Monday"
total_breaches = df.filter((pl.col("Day") == day) & (pl.col("KPI_breach") == 1)).shape[0]
total_tickets = df.filter(pl.col("Day") == day).shape[0]
print(f"Breach Percentage for {day}: {(total_breaches / total_tickets) * 100:.2f}%")

# === RCA: Breach Percentage by Day ===
print("\n=== RCA: Breach Percentage by Day ===")
if all(col in df.columns for col in ["Day", "KPI_breach"]):
    day_rca = (
        df.group_by("Day")
        .agg([
            pl.col("KPI_breach").sum().alias("Number of Breaches"),
            pl.count().alias("Total Tickets"),
        ])
        .with_columns(
            (pl.col("Number of Breaches") / pl.col("Total Tickets") * 100).alias("Breach Percentage (%)")
        )
        .sort("Day")
    )
    print(day_rca)
else:
    print("Required columns ('Day', 'KPI_breach') not found in the dataset.")

# === Volume of Created Tickets per Day and Percentage of Weekly Total ===
if "Day" in df.columns and "Created" in df.columns:
    # Add a 'Week' column (ISO week number)
    df = df.with_columns(
        pl.col("Created").dt.strftime("%G-%V").alias("Week")  # %G: ISO year, %V: ISO week number
    )
    total_tickets = df.shape[0]
    num_weeks = df.select("Week").unique().height

    # Calculate average tickets per day across all weeks
    day_week_volume = (
        df.group_by(["Week", "Day"])
        .agg([
            pl.count().alias("Tickets Created"),
        ])
        .group_by("Day")
        .agg([
            pl.col("Tickets Created").mean().alias("Avg Tickets Per Day"),
        ])
        .sort("Day")
    )

    # Calculate percentage of weekly total for each day
    avg_weekly_tickets = total_tickets / num_weeks if num_weeks > 0 else 1
    day_week_volume = day_week_volume.with_columns(
        (pl.col("Avg Tickets Per Day") / avg_weekly_tickets * 100).alias("Percentage of Weekly Total (%)")
    )

    print("\n=== Average Volume of Created Tickets per Day (per week) ===")
    print(day_week_volume)
else:
    print("Required columns ('Day', 'Created') not found in the dataset.")














































































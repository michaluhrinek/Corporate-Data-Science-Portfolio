# Import required libraries
import polars as pl
import random
import os
from datetime import datetime, timedelta

# Define state probabilities and other sample data
states_weights = [
    ("Closed", 85),
    ("New", 5),
    ("In Progress", 5),
    ("On Hold", 5)
]

# Define change environments
change_environments = [
    "Access", "Complaint", "Hardware", "Software", "Network", 
    "Failure", "Facilities", "Data"
]

# Define change-specific short descriptions
change_short_descriptions = [
   "System update applied",
    "Configuration setting changed",
    "User permissions modified",
    "Routine maintenance performed",
    "Backup schedule updated",
    "Software version upgraded",
    "Network settings adjusted",
    "Access policy reviewed",
    "Resource allocation changed",
    "Service restarted",
    "Security settings updated",
    "Application deployed",
    "Monitoring rules adjusted",
    "Data retention policy updated",
    "User group membership changed",
    "Scheduled job modified",
    "Device configuration updated",
    "Database maintenance completed",
    "Password policy updated",
    "System resource increased",
    "Service endpoint modified",
    "Application configuration changed",
    "User account updated",
    "Network route adjusted",
    "System role assigned",
    "Alert threshold changed",
    "Data export scheduled",
    "Device added to network",
    "Application access granted",
    "System log settings updated",
    "Resource permissions changed",
    "Service integration updated",
    "Device removed from inventory",
    "Scheduled task created",
    "User profile updated",
    "Application feature enabled",
    "System notification configured",
    "Service dependency changed",
    "Data import completed",
    "User session reset",
    "Application shortcut created",
    "Device firmware updated",
    "System cache cleared",
    "Service port changed",
    "User authentication method updated",
    "Application license assigned",
    "Device monitoring enabled",
    "System backup restored",
    "Service status checked",
    "User password reset",
    "Application log reviewed",
    "Device access restricted"
]

# Define possible services
services = ["Service A", "Service B", "Service C", "Service D", "Service E"]

# Define possible risk levels
risk_levels = ["High", "Medium", "Low"]

# Define possible urgency levels
urgency_levels = ["High", "Medium", "Low"]

# Define possible impact levels
impact_levels = ["High", "Medium", "Low"]

# Define assignment group weights
assignment_group_weights = {
    "Avengers": 0.5,
    "Avengers II": 0.3,
    "Matrix": 0.2
}

# Define assignment groups
assignment_groups = {
    "Avengers": ["Iron Man", "Loki", "Thor", "Captain America", "Hulk"],
    "Avengers II": ["Spiderman", "Doctor Strange", "Shang Chi", "Captain Marvel"],
    "Matrix": ["Neo", "John Cena", "Jack Sparrow", "John Wick", "Batman"]
}

# Priority definitions and mappings
priority_weights = {
    "Critical": 0.10,
    "High": 0.30,
    "Medium": 0.45,
    "Low": 0.15
}

# Change ticket generation parameters
data = []
start_date_2025 = datetime(2025, 1, 1)
end_date_2025 = datetime(2025, 12, 31)
ticket_number = 1  # Start ticket numbering

# Iterate through each day of the year
current_date = start_date_2025
while current_date <= end_date_2025:
    # Generate a baseline of changes for every day
    num_records_today = random.randint(1, 5)  # Guarantee at least 1 change per day, up to 5 changes

    for _ in range(num_records_today):
        created_date = current_date + timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )

        # Get the day of the week from the Created timestamp
        day_of_week = created_date.strftime("%A")

        # Random assignment of attributes
        assignment_group = random.choices(
            population=list(assignment_groups.keys()),
            weights=list(assignment_group_weights.values()),
            k=1
        )[0]
        assigned_member = random.choice(assignment_groups[assignment_group])
        priority = random.choices(
            population=list(priority_weights.keys()),
            weights=list(priority_weights.values()),
            k=1
        )[0]

        state = random.choices(["New", "In Progress", "On Hold", "Closed"], weights=[5, 5, 5, 85], k=1)[0]
        start_date = created_date + timedelta(hours=random.randint(2, 8)) if state in ["In Progress", "Closed"] else None
        closed_date = start_date + timedelta(hours=random.randint(2, 36)) if state == "Closed" else None

        # Assign random service
        service = random.choice(services)

        # Assign random risk level
        risk = random.choice(risk_levels)

        # Assign random urgency level
        urgency = random.choice(urgency_levels)

        # Assign random impact level
        impact = random.choice(impact_levels)

        # Assign random reopen count (between 0 and 5)
        reopen_count = random.randint(0, 5)

        # Append data for the current day
        data.append({
            "Number": f"CHG-{ticket_number:07d}",
            "Short Description": random.choice(change_short_descriptions),
            "Change Environment": random.choice(change_environments),
            "Requested By": assigned_member,
            "Assigned To": assigned_member,
            "Assignment Group": assignment_group,
            "Service": service,  # Include Service column
            "Risk": risk,        # Include Risk column
            "Urgency": urgency,  # Include Urgency column
            "Impact": impact,    # Include Impact column
            "State": state,
            "Priority": priority,
            "Created": created_date,
            "Day": day_of_week,  # Add Day column
            "Start Date": start_date,
            "Closed": closed_date,
            "Reopen Count": reopen_count,  # Include Reopen Count column
        })

        ticket_number += 1

    current_date += timedelta(days=1)

# Convert collected ticket data into a DataFrame
df = pl.DataFrame(data)

# Save dataset to a CSV file
output_file_path = r"synthetic_changes_data_2025.csv"
df.write_csv(output_file_path)

# Summary statistics
print(f"Total Tickets Generated: {ticket_number - 1}")
print(f"Data saved to {output_file_path}")
print(df.head())

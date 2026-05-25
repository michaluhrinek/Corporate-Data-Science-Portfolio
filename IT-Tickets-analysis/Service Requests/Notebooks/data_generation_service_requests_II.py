# Import required libraries
import polars as pl
import random
import os
from datetime import datetime, timedelta

# Define state probabilities and other sample data
states_weights = [
    ("Closed", 75),
    ("New", 15),
    ("In Progress", 7),
    ("On Hold", 3)
]

# Define service request environments
change_environments = ["Access", "Complaint", "Hardware", "Software", "Network", "Failure", "Facilities", "Data"]

# Define service request-specific short descriptions
short_descriptions = [
   "Request new workstation device",
"Request password assistance",
"Request access to a shared resource",
"Request creation of a group communication list",
"Request installation of standard-approved software",
"Request new mobile device setup",
"Request remote access enablement",
"Request additional display equipment",
"Request device hardware upgrade",
"Request creation of a user account",
"Request increase of mailbox storage",
"Request creation of shared mailbox",
"Request access to business application",
"Request printing access on office device",
"Request account details update",
"Request creation of a technical service account",
"Request access to reporting tools",
"Request activation of additional login security",
"Request addition to application access group",
"Request guest network access",
"Request new workstation setup at workplace",
"Request access to collaboration tool",
"Request productivity software licence",
"Request access to remote working environment",
"Request setup of email on user device",
"Request access to financial reporting tools",
"Request new audio equipment for calls",
"Request change of print settings",
"Request access to development resources",
"Request access to test environment data",
"Request upgrade to extended user profile",
"Request access to internal information site",
"Request new virtual environment for testing",
"Request external user account creation",
"Request access to time-management tools",
"Request new project storage area",
"Request change of access rights on shared storage",
"Request access to service management tool",
"Request docking station setup",
"Request change of user role in application",
"Request update of email signature settings",
"Request access to archived information",
"Request creation of new phone line entry",
"Request change of shared mailbox ownership",
"Request setup of automatic absence notification",
"Request configuration of meeting room technology",
"Request access to internal help and knowledge portal",
"Request access to source code repository",
"Request installation of document editing tool",
"Request setup of network storage connection",
"Request temporary elevated permissions on device",
"Request access to secure file transfer service",
"Request update of user contact information",
"Request addition to email group",
"Request removal from email group",
"Request change of default web browser",
"Request setup of email forwarding rule",
"Request new authentication device or token",
"Request replacement of power adapter",
"Request replacement of input device",
"Request access to data analysis tools",
"Request access to incident tracking dashboard",
"Request new conference call access details",
"Request shared calendar setup for team",
"Request access to learning and training portal",
"Request upgrade to latest approved software version",
"Request remote access to internal application",
"Request creation of generic team login",
"Request user profile migration to new device",
"Request access to marketing documents storage",
"Request change of default language settings",
"Request new role assignment in business system",
"Request access to document management tools",
"Request change of time zone settings for account",
"Request activation of network connection at workspace",
"Request access to secure printing features",
"Request enrolment of device into management system",
"Request creation of shared folder for project",
"Request website allowance for business use",
"Request VPN access from additional device",
"Request unblocking of specific email attachment type",
"Request subscription to scheduled report",
"Request creation of shared collaboration space",
"Request configuration of backup for data area",
"Request secure deletion of data from device",
"Request removal of unused virtual environment",
"Request reactivation of existing user account",
"Request update to data retention settings",
"Request adjustment of access permissions",
"Request configuration change for application settings",
"Request update to monitoring or alerting settings",
"Request configuration update for communication tools",
"Request setup of guest access for temporary user",
"Request configuration of high-availability service",
"Request change in routing for service access",
"Request setup of test environment for application",
"Request upgrade of workstation performance",
"Request update of security configuration",
"Request setup of shared document library",
"Request configuration of project-specific tools"
]

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

priority_urgency_impact_mapping = {
    "Critical": {"Urgency": [("High", 0.9), ("Medium", 0.1)], "Impact": [("High", 0.8), ("Medium", 0.2)]},
    "High": {"Urgency": [("High", 0.7), ("Medium", 0.3)], "Impact": [("High", 0.6), ("Medium", 0.3), ("Low", 0.1)]},
    "Medium": {"Urgency": [("Medium", 0.7), ("Low", 0.3)], "Impact": [("Medium", 0.8), ("Low", 0.2)]},
    "Low": {"Urgency": [("Low", 1)], "Impact": [("Low", 1)]},
}

# Group-specific priority distribution
assignment_group_priority_weights = {
    "Avengers": {"Critical": 0.4, "High": 0.3, "Medium": 0.2, "Low": 0.1},
    "Avengers II": {"Critical": 0.2, "High": 0.3, "Medium": 0.4, "Low": 0.1},
    "Matrix": {"Critical": 0.1, "High": 0.2, "Medium": 0.5, "Low": 0.2}
}

# Initialization for data generation
data = []
start_date_2025 = datetime(2025, 1, 1)
end_date_2025 = datetime(2025, 12, 31)
current_date = start_date_2025
ticket_number = 1
total_records_to_generate = 33156

# Estimate average records per day
average_records_per_day = total_records_to_generate // 365

while current_date <= end_date_2025 and ticket_number <= total_records_to_generate:
    # Determine number of service requests for the current day
    num_records_today = random.randint(int(average_records_per_day * 0.8), int(average_records_per_day * 1.2))

    for _ in range(min(num_records_today, total_records_to_generate - ticket_number + 1)):  # Ensure total_changes limit
        # Generate ticket creation timestamp
        created_date = current_date + timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )

        # Randomly assign assignment group and member
        assignment_group = random.choices(
            population=list(assignment_groups.keys()),
            weights=list(assignment_group_weights.values()),
            k=1
        )[0]
        assigned_member = random.choice(assignment_groups[assignment_group])

        # Assign priority
        priority = random.choices(
            population=list(assignment_group_priority_weights[assignment_group].keys()),
            weights=list(assignment_group_priority_weights[assignment_group].values()),
            k=1
        )[0]

        # Select urgency and impact
        urgency = random.choices(
            population=[item[0] for item in priority_urgency_impact_mapping[priority]["Urgency"]],
            weights=[item[1] for item in priority_urgency_impact_mapping[priority]["Urgency"]],
            k=1
        )[0]
        impact = random.choices(
            population=[item[0] for item in priority_urgency_impact_mapping[priority]["Impact"]],
            weights=[item[1] for item in priority_urgency_impact_mapping[priority]["Impact"]],
            k=1
        )[0]

        # Assign state
        state = random.choices(
            population=["New", "In Progress", "On Hold", "Closed"],
            weights=[15, 7, 3, 75],
            k=1
        )[0]

        # Calculate start and closed dates
        if state == "Closed":
            start_date = created_date + timedelta(hours=random.randint(2, 8))
            if priority == "Critical":
                closed_date = start_date + timedelta(hours=random.randint(1, 12))
            elif priority == "High":
                closed_date = start_date + timedelta(hours=random.randint(6, 24))
            elif priority == "Medium":
                closed_date = start_date + timedelta(hours=random.randint(12, 36))
            else:  # Low priority
                closed_date = start_date + timedelta(hours=random.randint(24, 72))
        elif state == "In Progress":
            start_date = created_date + timedelta(hours=random.randint(2, 6))
            closed_date = None
        else:  # New or On Hold
            start_date = None
            closed_date = None

        # Randomly assign Reopen Count
        reopen_count = random.randint(0, 5)  # Random value between 0 and 5

        # Append ticket data
        data.append({
            "Number": f"SR-{ticket_number:07d}",
            "Short Description": random.choice(short_descriptions),
            "Change Environment": random.choice(change_environments),
            "Requested By": assigned_member,
            "Assigned To": assigned_member,
            "Assignment Group": assignment_group,
            "Service": random.choice(["Service A", "Service B", "Service C"]),
            "State": state,
            "Risk": random.choice(["High", "Medium", "Low"]),
            "Priority": priority,
            "Urgency": urgency,
            "Impact": impact,
            "Created": created_date,
            "Start Date": start_date,
            "Closed": closed_date,
            "Reopen Count": reopen_count
        })

        ticket_number += 1

    current_date += timedelta(days=1)

# Generate DataFrame
df = pl.DataFrame(data)

# Add extra columns for enhancements
df = df.with_columns([
    pl.col("Created").dt.strftime("%A").alias("Day"),  # Add day of the week
    pl.col("Created").cast(pl.Datetime),
    pl.col("Start Date").cast(pl.Datetime),
    pl.col("Closed").cast(pl.Datetime)
])

# Save the dataset to CSV file
output_file_path = r"synthetic_service_request_data_2025.csv"
output_dir = os.path.dirname(output_file_path)
if output_dir and not os.path.exists(output_dir):
    os.makedirs(output_dir)

df.write_csv(output_file_path)

# Summary statistics
total_tickets = df.shape[0]
print(f"Total Tickets Generated: {total_tickets}")
print(f"Dataset saved to {output_file_path}")
print(df.head())

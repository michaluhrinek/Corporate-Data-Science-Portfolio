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
    "Request to create a new distribution list for the Marketing team.",
    "Request to access internal SharePoint site for the Finance department.",
    "Update public holiday calendar in corporate Outlook accounts.",
    "Relocation of desktop workstation within the office premises.",
    "Install licensed Microsoft Visio on a department computer.",
    "Provisioning of VPN access for third-party vendor consultants.",
    "Request for extended quota on shared email inbox.",
    "Request to reset password for employee account.",
    "Change access rights on shared folder for team lead.",
    "Install Adobe Creative Suite on workstation for design team.",
    "Request to create test environment for application testing.",
    "User asking for permissions to install additional software.",
    "Configuration update needed for internal voice gateway routing.",
    "Request to add new printer to network for HR department.",
    "Request to configure SSO login for external web resource.",
    "Grant access to restricted database for data analytics intern.",
    "Upgrade workstation RAM for improved video editing performance.",
    "Request to enable remote access to on-site servers.",
    "Request for secure deletion of files on retired desktops.",
    "Re-enable accounts for recent employee returning after leave.",
    "Request to create and configure backup jobs for departmental database.",
    "Extend mailbox retention policy for legal department emails.",
    "Activate mobile application access for workflow approvals.",
    "Request to create container image repository for DevOps team.",
    "Provision external storage for graphics design project.",
    "Request to move group mailbox ownership to new manager.",
    "Update employee badge photo in internal directory.",
    "Enable high-availability configuration on two production servers.",
    "Troubleshoot application access issues related to role change.",
    "Configure alerts for reporting dashboard thresholds.",
    "Request to adjust permissions on shared inbox handling invoices.",
    "Document retention policy modification for compliance purposes.",
    "Request to install Python libraries on student laptops.",
    "Add two new access points to the office Wi-Fi network.",
    "Request for cloud storage account provisioning for upcoming project.",
    "Enable multi-factor authentication for remote developers.",
    "Request to delete unused virtual machines in non-production environment.",
    "Upgrade Oracle database version to meet system requirements.",
    "Request for temporary guest access to internal intranet services.",
    "Reassign ownership of project management tools to new team lead.",
    "Replace hardware for malfunctioning conference room equipment.",
    "Setup repository access for junior developers.",
    "Enable port redirection for database replication tasks.",
    "Provision special access profiles for GDPR compliance audits.",
    "Create custom email signature for company branding.",
    "Upgrade virtual machine specs for training platform.",
    "Backup and restore files deleted by mistake on shared drive.",
    "Create subdomain for new departmental website launch."
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
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
    "Request new laptop for employee onboarding",
    "Request password reset for user account",
    "Request access to shared network drive",
    "Request new email distribution list creation",
    "Request installation of approved software on workstation",
    "Request new mobile phone and SIM card",
    "Request access to VPN for remote work",
    "Request additional monitor for workstation",
    "Request upgrade of laptop memory",
    "Request creation of new Active Directory account",
    "Request extension of mailbox storage quota",
    "Request shared mailbox creation for team",
    "Request access to HR system for new role",
    "Request printing rights on departmental printer",
    "Request change of username after name change",
    "Request creation of service account for application",
    "Request access to reporting dashboard",
    "Request MFA activation for user account",
    "Request addition to security group for application access",
    "Request access to corporate Wi-Fi for guest user",
    "Request setup of new workstation at office desk",
    "Request access to project management tool",
    "Request license assignment for Office suite",
    "Request access to remote desktop environment",
    "Request configuration of email on mobile device",
    "Request access to finance application",
    "Request new headset for VoIP phone",
    "Request change of default printer settings",
    "Request access to development environment",
    "Request access to test environment databases",
    "Request upgrade from standard to power user profile",
    "Request access to internal SharePoint site",
    "Request new virtual machine for project testing",
    "Request new user account for external vendor",
    "Request access to time-tracking system",
    "Request creation of new project folder on file server",
    "Request modification of access rights on shared folder",
    "Request access to ticketing system for new team member",
    "Request laptop docking station setup",
    "Request change of user role in business application",
    "Request reconfiguration of email signature template",
    "Request access to archived email data",
    "Request new phone extension for employee",
    "Request change of ownership for shared mailbox",
    "Request setup of automatic out-of-office reply",
    "Request configuration of Teams/meeting room equipment",
    "Request access to internal knowledge base portal",
    "Request access to code repository",
    "Request installation of PDF editor software",
    "Request configuration of network drive mapping",
    "Request temporary admin rights for software installation",
    "Request access to secure file transfer service",
    "Request update of contact details in IT systems",
    "Request addition to email distribution group",
    "Request removal from email distribution group",
    "Request change of default browser on workstation",
    "Request setup of email forwarding to another mailbox",
    "Request new smart card or token for authentication",
    "Request replacement of broken laptop charger",
    "Request replacement of damaged keyboard",
    "Request access to analytics platform",
    "Request access to incident management dashboard",
    "Request new conference call bridge details",
    "Request configuration of shared calendar for team",
    "Request access to internal training portal",
    "Request software upgrade to latest approved version",
    "Request remote access to on-premise application",
    "Request creation of generic team account",
    "Request profile transfer to new device",
    "Request access to marketing file repository",
    "Request change of default language in applications",
    "Request new role assignment in CRM system",
    "Request access to document management system",
    "Request change of time zone settings for user account",
    "Request new network port activation at desk",
    "Request access to secure printing functionality",
    "Request enrollment in mobile device management",
    "Request shared folder for cross-department project",
    "Request whitelist of business website on web proxy",
    "Request access to company VPN from new device",
    "Request unblocking of email attachment type",
    "Request scheduled report subscription setup",
    "Request new collaboration space in Teams"
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
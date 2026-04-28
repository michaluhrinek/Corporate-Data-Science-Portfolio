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
     "Apply monthly security patches to production servers",
    "Upgrade database server to latest minor version",
    "Deploy new release of core banking application",
    "Implement firewall rule change for new service endpoint",
    "Migrate application from test to production environment",
    "Update SSL/TLS certificates on web servers",
    "Change load balancer configuration for improved failover",
    "Modify VPN access policy for remote employees",
    "Increase disk space allocation on application server",
    "Deploy new version of mobile banking API",
    "Change Active Directory group membership for user access",
    "Reconfigure backup schedule for critical databases",
    "Introduce new logging and monitoring rules for servers",
    "Change network routing for branch office connectivity",
    "Implement new password policy across domain",
    "Update DNS records for application hostname change",
    "Replace legacy file server with new storage system",
    "Implement role-based access control for application",
    "Upgrade operating system on middleware servers",
    "Decommission obsolete virtual machines",
    "Enable multi-factor authentication for VPN users",
    "Deploy hotfix for production application issue",
    "Change email gateway configuration for spam filtering",
    "Implement new proxy configuration for internet access",
    "Adjust CPU and memory resources for virtual servers",
    "Apply configuration changes to intrusion detection system",
    "Deploy updated configuration for network switches",
    "Configure new SFTP connection to external partner",
    "Migrate user mailboxes to new email platform",
    "Change scheduled job timing for batch processing",
    "Implement new retention policy for log data",
    "Enable encryption at rest for database storage",
    "Add new subnet to internal network for project team",
    "Reconfigure application timeout settings",
    "Update API gateway rules for new service endpoints",
    "Change print server configuration for new printers",
    "Adjust monitoring thresholds for critical alerts",
    "Implement new access roles in identity management system",
    "Upgrade virtualization platform to latest version",
    "Modify backup retention period for file shares",
    "Change configuration of web application firewall policies",
    "Deploy new configuration for password self-service portal",
    "Introduce new email disclaimer for outgoing messages",
    "Update network share permissions for project folder",
    "Configure new high-availability cluster for database",
    "Change time synchronization settings for servers",
    "Implement new software deployment package for endpoints",
    "Modify service account permissions for application",
    "Update configuration for single sign-on integration",
    "Change DHCP scope settings for office network",
    "Deploy new version of endpoint management agent",
    "Reconfigure service monitoring checks for new URLs",
    "Implement new change in batch file transfer process"
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
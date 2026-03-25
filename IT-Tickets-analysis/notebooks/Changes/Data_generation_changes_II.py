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
       "Install rsync on twgmmp01.",
    "Grant access to crontab for ta2twga on twgmmp01.zit.commerzbank.com.",
    "Install httpd-tools on twgmmp01.zit.commerzbank.com.",
    "UC4 Agent Installation on gcetcami001.",
    "VUL-NET: Cisco Wireless IOS-XE Software Update for WLC9800 | Jugoslavska, CZ (PRA06).",
    "Case 65943239: Upgrade Ontap version to 9.14.1P12.",
    "Execute systemctl daemon-reload on CSO VM (PROD).",
    "Certificate renewal for Avatar PROD environment 2026 - (VAA-Threat Application).",
    "Certificate renewal Digital Banking on PROD environment 2026.",
    "Online Banking external CB-APP onboarding on Radware On-prem environment.",
    "Restart tkmdbp01 of configuration change took longer than expected.",
    "Updating the IDRAC remote board Firmware and BIOS for sonklb31.",
    "Updating the IDRAC remote board Firmware and BIOS for timffm21.",
    "Updating the IDRAC remote board Firmware and BIOS for secffme2.",
    "Remote board SSL Cert renewal for anysgp15 & anysgp14.",
    "Remote board SSL Cert renewal for ressgpe0 , ressgpe1 , secsgpe0 & secsgpe1.",
    "New IP subnet & access point testing for KL relocation project.",
    "TAPs installation in IMK productive connections for work order #REQ0157356.",
    "ACI switchports configuration for work orders #REQ0155328 #REQ0147118 #REQ0152855.",
    "Firewall configuration changes for disaster recovery validation testing.",
    "Update IDRAC remote board Firmware and BIOS for forffm71.",
    "VUL-NET: Critical Juniper network patch for external office gateways.",
    "VUL-NET: Apply Cisco IOS Software Update for routers at PRA, SHA, and TOK sites.",
    "Enable database backups at sv273046 for production environment.",
    "Resize virtual storage for CoreTxx_PROD database (95,38% full).",
    "Certificate renewal request for high-availability environment 2026.",
    "Request for temporary access rights on Finance application Web UI.",
    "Install Redis cluster monitoring tools in shard servers.",
    "Test external web proxy configurations on development servers.",
    "Update the IDRAC remote board Firmware and BIOS for secklb01.",
    "Initiate scheduled SAN Storage Array node reboot to resolve high uptime issue.",
    "Certificate update for Palo Alto gatekeeping subnet for KL relocation network.",
    "Certificate renewal for cloud-hosted services 2026.",
    "Install system monitoring scripts on AWS-hosted general-purpose non-prod servers.",
    "Provision new storage array in EU data center for increased redundancy.",
    "Replace legacy switches with modern devices in Market Data Environment.",
    "Execution of systemctl daemon-reload to patch Prod-CSO VM resiliency.",
    "Emergency fall-back routing enabled for Redis cluster 6 under high throughput.",
    "Certificate update for Office 365 external access via Global Protect Gateways.",
    "Firewall optimization for edge routing performance post DR testing.",
    "Update from RHEL8.9 to RHEL8.10 on database workloads (non-prod).",
    "SSL certificate renewal for SWS corporate web hosting final access gateways.",
    "Switchport configuration for targeted hosts to enhance authentication mechanisms.",
    "Certificate renewal for Avatar development environment - Cloud Integration Testing Area.",
    "Server BIOS updates across remote virtual VM hosts (RESFFM01, SECFFM01).",
    "Password reset request for disabled accounts in non-prod systems.",
    "Increase VM capacity for ongoing AI processing workload.",
    "Update IDRAC board for core cluster PROD servers.",
    "Restart tkmweb database servers after container update failure response.",
    "Database configuration check for performance improvements in PROD systems.",
    "Firewall rule onboarding for external SaaS applications via Palo Alto setup.",
    "Execute hardening measures for SQL server instances post security audit.",
    "Deploy ACL rules for high-priority Office 365 tenants across European zones.",
    "Enable additional remote IPV6 routing for Japanese production systems.",
    "Patch network appliances for compliance with wireless protocols.",
    "Setup additional SAML authentication nodes in DMZ environment.",
    "Reverse fallback isolation plan post-Palo Alto Prisma failure.",
    "Configuration changes for monitoring processors on Redis prototype servers.",
    "Software patch implementation targeting RHEL8.1 compatibility issues.",
    "Grant access for backup recovery on production machine nodes in DR locations.",
    "Complete SSL foundation checks for project-focused data endpoints.",
    "Enable ADFS custom user provisioning profile upload validation.",
    "Patch remote job runner script dependencies for IMK analytics platform.",
    "Firewall subnet allocation and access provisioning for KL office gateway.",
    "Certificate adjustments for new virtual database pipelines.",
    "Install httpd-tools on edge proxy nodes.",
    "Subnet migration alignment to cater towards hybrid env-discoveries (Prepare Step ongoing).",
    "Expand edge metrics transitioning through Palo FLEX Zeon tiers vs EU roots.",
    "Adjust Volume changes incompatible fixes mid-stage (handling-/handoff migration).",
  
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

urgency_weights = {
    "High": 0.40,
    "Medium": 0.40,
    "Low": 0.20
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

# Change ticket generation parameters
data = []
start_date_2025 = datetime(2025, 1, 1)
end_date_2025 = datetime(2025, 12, 31)
current_date = start_date_2025
ticket_number = 1  # Start ticket number
total_changes = 198  # Total number of changes to generate

while current_date <= end_date_2025 and ticket_number <= total_changes:
    # Determine the day of the week and number of tickets
    day_of_week = current_date.strftime("%A")
    num_records_today = random.randint(*{
        "Monday": (16, 70),
        "Tuesday": (12, 66),
        "Wednesday": (3, 47),
        "Thursday": (4, 36),
        "Friday": (1, 33),
        "Saturday": (20, 60),
        "Sunday": (10, 53)
    }.get(day_of_week, (50, 100)))

    # Generate tickets for the current day
    for _ in range(min(num_records_today, total_changes - ticket_number + 1)):  # Ensure total_changes limit
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

        # Assign priority based on group-specific weights
        priority = random.choices(
            population=list(assignment_group_priority_weights[assignment_group].keys()),
            weights=list(assignment_group_priority_weights[assignment_group].values()),
            k=1
        )[0]

        # Select urgency and impact based on priority
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
            weights=[5, 5, 5, 85],
            k=1
        )[0]

        # Logical calculation for start and closed dates
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

        # Assign reopen count
        reopen_count = random.choices(
            population=[0, 1],
            weights=[0.85, 0.15],
            k=1
        )[0]

        # Append generated ticket data
        data.append({
            "Number": f"CHG-{ticket_number:07d}",
            "Short Description": random.choice(change_short_descriptions),
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
            "Reopen Count": reopen_count  # Reopen count remains
        })

        ticket_number += 1

    current_date += timedelta(days=1)

# Create a Polars DataFrame
df = pl.DataFrame(data)

# Add extra columns for enhancements
df = df.with_columns([
    pl.col("Created").dt.strftime("%A").alias("Day"),  # Add day of the week
    pl.col("Created").cast(pl.Datetime),
    pl.col("Start Date").cast(pl.Datetime),
    pl.col("Closed").cast(pl.Datetime)
])

# Save the dataset to a CSV file
output_file_path = r"synthetic_changes_data.csv"  # Update file path as needed
output_dir = os.path.dirname(output_file_path)
if output_dir and not os.path.exists(output_dir):
    os.makedirs(output_dir)

df.write_csv(output_file_path)

# Summary statistics
total_tickets = df.shape[0]
print(f"Total Tickets: {total_tickets}")
print(f"Dataset saved to {output_file_path}")
print(df.head())
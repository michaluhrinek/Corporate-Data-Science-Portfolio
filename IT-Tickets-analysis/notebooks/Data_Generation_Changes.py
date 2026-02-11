# Change Ticket Data Generation

import polars as pl
import random
import os
from datetime import datetime, timedelta

# Define state probabilities and other sample data
states_weights = [
    ("Closed", 35),
    ("New", 15),
    ("In Progress", 10),
    ("On Hold", 10)
]

# Assignment group definitions
assignment_group_weights = {
    "Avengers": 0.5,
    "Avengers II": 0.3,
    "Matrix": 0.2
}

assignment_groups = {
    "Avengers": ["Iron Man", "Loki", "Thor", "Captain America", "Hulk"],
    "Avengers II": ["Spiderman", "Doctor Strange", "Shang Chi", "Captain Marvel"],
    "Matrix": ["Neo", "John Cena", "Jack Sparrow", "John Wick", "Batman"]
}

# Priority weights
priority_weights = {
    "Critical": 0.10,
    "High": 0.30,
    "Medium": 0.45,
    "Low": 0.15
}

# Urgency and impact mapping based on priority
priority_urgency_impact_mapping = {
    "Critical": {"Urgency": [("High", 0.9), ("Medium", 0.1)], "Impact": [("High", 0.8), ("Medium", 0.2)]},
    "High": {"Urgency": [("High", 0.7), ("Medium", 0.3)], "Impact": [("High", 0.6), ("Medium", 0.3), ("Low", 0.1)]},
    "Medium": {"Urgency": [("Medium", 0.7), ("Low", 0.3)], "Impact": [("Medium", 0.8), ("Low", 0.2)]},
    "Low": {"Urgency": [("Low", 1)], "Impact": [("Low", 1)]},
}

# Change request short descriptions
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

# Initialization
data = []
start_date_2025 = datetime(2025, 1, 1)
end_date_2025 = datetime(2025, 12, 31)
current_date = start_date_2025

# Generate incident and change data
incident_number = 1
change_number = 1
total_changes = 76

while current_date <= end_date_2025:
    # Determine the day of the week and number of tickets
    day_of_week = current_date.strftime("%A")
    num_records_today = random.randint(*{
        "Monday": (90, 170),
        "Tuesday": (100, 180),
        "Wednesday": (80, 160),
        "Thursday": (70, 150),
        "Friday": (60, 120),
        "Saturday": (20, 60),
        "Sunday": (10, 30)
    }.get(day_of_week, (50, 100)))

    # Generate incidents
    for _ in range(num_records_today):
        created_date = current_date + timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )

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

        state = random.choices(
            population=["New", "In Progress", "On Hold", "Closed"],
            weights=[5, 5, 5, 85],
            k=1
        )[0]

        if state == "Closed":
            start_date = created_date + timedelta(hours=random.randint(2, 8))
            closed_date = start_date + timedelta(hours=random.randint(2, 44))
        elif state == "In Progress":
            start_date = created_date + timedelta(hours=random.randint(2, 6))
            closed_date = None
        else:
            start_date = None
            closed_date = None

        breach_count = random.choice([0, 1]) if priority in ["Low", "Medium"] else random.choice([2, 3, 4])

        reopen_count = random.choices([0, 1], weights=[0.85, 0.15], k=1)[0]

        data.append({
            "Type": "Incident",
            "Number": f"INC-{incident_number:07d}",
            "Short Description": random.choice(change_short_descriptions),
            "Assignment Group": assignment_group,
            "Requested By": assigned_member,
            "Priority": priority,
            "Urgency": urgency,
            "Impact": impact,
            "State": state,
            "Created": created_date,
            "Start Date": start_date,
            "Closed": closed_date,
            "Reopen Count": reopen_count,
            "Breach Count": breach_count
        })

        incident_number += 1

    # Generate changes only a few times across the year, distribute evenly
    if change_number <= total_changes:
        num_changes_today = random.randint(0, 3)  # Few changes per day, max 3
        for _ in range(num_changes_today):
            created_date_change = current_date + timedelta(
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )

            data.append({
                "Type": "Change",
                "Number": f"CHG-{change_number:07d}",
                "Short Description": random.choice(change_short_descriptions),
                "Assignment Group": random.choice(list(assignment_groups.keys())),
                "Requested By": random.choice(["Admin", "Team Lead", "Manager"]),
                "Priority": random.choices(
                    population=list(priority_weights.keys()),
                    weights=list(priority_weights.values()),
                    k=1
                )[0],
                "Created": created_date_change,
                "Start Date": created_date_change + timedelta(hours=random.randint(0, 5)),
                "Closed": created_date_change + timedelta(hours=random.randint(5, 48)),
            })

            change_number += 1

    current_date += timedelta(days=1)

# Create a Polars DataFrame
df = pl.DataFrame(data)

# Add extra columns to enhance the data
df = df.with_columns([
    pl.col("Created").dt.strftime("%A").alias("Day"),  # Add day of the week
    pl.col("Created").cast(pl.Datetime),
    pl.col("Start Date").cast(pl.Datetime),
    pl.col("Closed").cast(pl.Datetime)
])

# Save dataset to a CSV file
output_file_path = r"synthetic_changes_data.csv"
output_dir = os.path.dirname(output_file_path)
if output_dir and not os.path.exists(output_dir):
    os.makedirs(output_dir)

df.write_csv(output_file_path)

total_tickets = df.shape[0]
total_changes = df.filter(pl.col("Type") == "Change").shape[0]
total_incidents = df.filter(pl.col("Type") == "Incident").shape[0]

print(f"Total Tickets: {total_tickets}")
print(f"Total Incidents: {total_incidents}")
print(f"Total Changes: {total_changes}")
print(f"Dataset saved to {output_file_path}")
print(df.head())
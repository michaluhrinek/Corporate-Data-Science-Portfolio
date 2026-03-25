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
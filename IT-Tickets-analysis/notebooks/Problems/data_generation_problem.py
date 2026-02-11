# Enhanced IT Problem Ticket Generation with Realistic Distributions

import polars as pl
import random
import os
from datetime import datetime, timedelta

# Define state probabilities and other sample data
states_weights = [
    ("Closed", 80),
    ("New", 10),
    ("In Progress", 5),
    ("On Hold", 5)
]

change_environments = ["Access", "Complaint", "Hardware", "Software", "Network", "Failure", "Facilities", "Data"]

short_descriptions = [
    "VulMgt: High / VMware ESXi Privilege Escalation Vulnerability CVE-2025-30472 PSIRT Nov.2025.",
"VulMgt: Critical / Apache HTTP Server Path Traversal Vulnerability CVE-2025-40513 PSIRT Oct.2025.",
"Users experiencing degraded download speeds when accessing European endpoints during peak hours.",
"Frequent HTTP error 502 bad gateway observed on public-facing APIs.",
"Unexpected reboot of Dell EMC PowerEdge Server SX3301 causing production downtime.",
"Disk space alert: System logs consuming 98% of allocated storage on SV370920:DataStore01.",
"SV240611.ztd.icb.commerzbank.comPROMOSS_P2:MYSQL:ReplicationLag:DeltaTooHigh.",
"Failed database connection for sv281432 due to excessive transaction log growth.",
"Storage volume SV247890 nearing capacity (94% full), affecting batch process schedules.",
"Unable to allocate memory in service container for Redis instances 145323-dbprd01 and 145323-dbprd02.",
"Incident INC0247193: VPN connectivity issues reported in APAC region during DR failover.",
"Connection timeout between SWSHK0019A and RTSHK0018 after DMZ firewall patch.",
"No access to intranet resources due to SSL certificate expiration.",
"Root cause analysis and follow-up to PRB0058244 - Internal proxy overload impacting corporate web traffic.", 
"Tenant restrictions v3 causing unauthorized access to external Office 365 environments.",
"Authentication errors observed after applying policy updates on Cloud Proxy Gateway.",
"CERT Alert: RTSMNL2K21 flagged compromised—segmentation plan initiated.",
"Critical issue: No connectivity to company-hosted Microsoft Teams instances (Germany Office Gateway).",
"Multiple server reboots after Red Hat EL9 update due to kernel module mismatch.",
"Root cause analysis: Network connections disrupted after DR Test between DLN and TBL DC.",
"Internal SharePoint services intermittently unavailable due to high system memory utilization.", 
"Unexpected outage of financial ERP system after deployment of malformed SQL script.",
"Disconnected VM workloads following Datacenter failover actions during change CHG0543871.",
"Partial outage of Secure Web Gateway resulting in restricted access to external hosted applications.",
"Multiple database query timeouts observed on MSDC_TXX_PROD instance following high I/O read spikes.",
"Unreachable application server post firewall upgrade affecting REST API integrations.",
"Communication breakdown between IMK and DCN locations due to routing rule misconfiguration.",
"Google cloud API gateway throttling unauthorized requests—Downtime logged for related components.", 
"Authentication handshake failure detected on TLS-enabled external endpoints.",
"High data latency observed on virtualized analytics server cluster NODE903-TGX-BI1.",
"VulMgt: Fortinet / Critical Vulnerability in FortiOS SSL VPN CVE-2025-50987 / PSIRT Dec.2025.",
"pm05019343 from legacy ticketing system: SLA violation mismanagement documented Apr-2025 breach.",
"Disk utilization warning: SV374586 storage volume at 96.43%, impacting backup ingestion tasks.",
"Remote Desktop connection errors persist for users accessing VNEDS0043Azure gateways.",
"Prepare phase of Ubuntu upgrade failed on cntrprd03 and cntrprd04 due to package dependency conflicts.",
"Unplanned downtime on Azure-hosted MySQL instance during automated patching (PROD environment).",
"Issue with payment gateway APIs intermittently showing 503 error for e-commerce customers.",
"Root cause analysis and resolution plan for service degradation during Kubernetes failover (LND-Cluster3).",
"Major network outage on NLB2 zone affecting cross-datacenter replication and DR readiness.",
"Policy misalignment: Users reporting unauthorized access to restricted financial systems."
]

assignment_group_weights = {
    "Avengers": 0.5,
    "Avengers II": 0.3,
    "Matrix": 0.2
}

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

assignment_groups = {
    "Avengers": ["Iron Man", "Loki", "Thor", "Captain America", "Hulk"],
    "Avengers II": ["Spiderman", "Doctor Strange", "Shang Chi", "Captain Marvel"],
    "Matrix": ["Neo", "John Cena", "Jack Sparrow", "John Wick", "Batman"]
}

priority_urgency_impact_mapping = {
    "Critical": {"Urgency": [("High", 0.9), ("Medium", 0.1)], "Impact": [("High", 0.8), ("Medium", 0.2)]},
    "High": {"Urgency": [("High", 0.7), ("Medium", 0.3)], "Impact": [("High", 0.6), ("Medium", 0.3), ("Low", 0.1)]},
    "Medium": {"Urgency": [("Medium", 0.7), ("Low", 0.3)], "Impact": [("Medium", 0.8), ("Low", 0.2)]},
    "Low": {"Urgency": [("Low", 1)], "Impact": [("Low", 1)]},
}

assignment_group_priority_weights = {
    "Avengers": {"Critical": 0.4, "High": 0.3, "Medium": 0.2, "Low": 0.1},
    "Avengers II": {"Critical": 0.2, "High": 0.3, "Medium": 0.4, "Low": 0.1},
    "Matrix": {"Critical": 0.1, "High": 0.2, "Medium": 0.5, "Low": 0.2}
}

data = []
start_date_2025 = datetime(2025, 1, 1)
end_date_2025 = datetime(2025, 12, 31)
current_date = start_date_2025
ticket_number = 1

while current_date <= end_date_2025:
    # Determine the day of the week and number of tickets
    day_of_week = current_date.strftime("%A")
    num_records_today = random.randint(*{
        "Monday": (10, 30),
        "Tuesday": (20, 30),
        "Wednesday": (12, 25),
        "Thursday": (7, 15),
        "Friday": (9, 13),
        "Saturday": (10, 14),
        "Sunday": (5, 10)
    }.get(day_of_week, (25, 100)))

    for _ in range(num_records_today):
        # Generate session creation timestamp
        created_date = current_date + timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )

        # Randomly assign group and member based on weights
        assignment_group = random.choices(
            population=list(assignment_groups.keys()),
            weights=list(assignment_group_weights.values()),
            k=1
        )[0]
        assigned_member = random.choice(assignment_groups[assignment_group])

        # Assign priority logic based on group-specific weights
        priority = random.choices(
            population=list(assignment_group_priority_weights[assignment_group].keys()),
            weights=list(assignment_group_priority_weights[assignment_group].values()),
            k=1
        )[0]

        # Randomly select urgency and impact based on priority
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

        # Randomly assign state
        state = random.choices(
            population=["New", "In Progress", "On Hold", "Closed"],
            weights=[5, 5, 5, 85],
            k=1
        )[0]

        # Logical calculation for dates
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
        else:
            start_date = None
            closed_date = None

        # Assign Breach Count based on priority
        if priority == "Critical":
            breach_count = random.choice([3, 4, 5])
        elif priority == "High":
            breach_count = random.choice([2, 3])
        elif priority == "Medium":
            breach_count = random.choice([1, 2])
        else:  # Low
            breach_count = random.choice([0, 1])

        # Assign reopen count—5-25% chance of reopening
        reopen_count = random.choices(
            population=[0, 1],
            weights=[0.85, 0.15],  # 85% no reopen, 15% reopen
            k=1
        )[0]

        # Append generated ticket data to the dataset
        data.append({
            "Number": f"CR-{ticket_number}",
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
            "Reopen Count": reopen_count,
            "Breach Count": breach_count
        })

        ticket_number += 1

    current_date += timedelta(days=1)

# Create a Polars DataFrame
df = pl.DataFrame(data)

# Add extra columns to enhance the data
df = df.with_columns([
    pl.col("Created").dt.strftime("%A").alias("Day"),  # Add day of the week
    pl.col("Created").cast(pl.Datetime),
    pl.col("Start Date").cast(pl.Datetime),
    pl.col("Closed").cast(pl.Datetime),
    (pl.col("Reopen Count") == 0).cast(pl.Int64).alias("Reopen Zero Flag")
])

# Save dataset to a CSV file
output_file_path =  r"synthetic_problem_bank_data_weighted.csv"
output_dir = os.path.dirname(output_file_path)
if output_dir and not os.path.exists(output_dir):
    os.makedirs(output_dir)

df.write_csv(output_file_path)

# Summary statistics
total_tickets = df.shape[0]
non_reopened_tickets = df.select(pl.col("Reopen Zero Flag").sum())[0, 0]
reopen_percentage = (non_reopened_tickets / total_tickets) * 100

print(f"Total Tickets: {total_tickets}")
print(f"Tickets Not Reopened (Reopen Count = 0): {non_reopened_tickets}")
print(f"Percentage of Tickets Not Reopened: {reopen_percentage:.2f}%")
print(f"Dataset saved to {output_file_path}")
print(df.head())
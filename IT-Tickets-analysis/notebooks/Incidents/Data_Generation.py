# Enhanced IT Incident Ticket Generation with Realistic Distributions
#import libraries 
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

change_environments = ["Access", "Complaint", "Hardware", "Software", "Network", "Failure", "Facilities", "Data"]

short_descriptions = [
 "Power failure simulation triggered during red team activity.",
"Failed encryption process: Unable to secure sensitive data.",
"Unauthorized access attempt detected on admin portal.",
"Firewall breach: Unauthorized access through open port.",
"Service outage detected with no connection to database.",
"Critical alert: Database server overload detected.",
"Suspicious activity flagged in privileged environment.",
"Phishing email identified by security team.",
"High file transfer identified; possible data exfiltration suspected.",
"DNS query failure: Incorrect configuration detected on the main server.",
"Memory exhaustion detected: Immediate remediation required.",
"Endpoint disconnected: Device is not responding to monitoring server.",
"System resource spike identified on analytics server logs.",
"Failed login attempts detected from multiple locations.",
"Sluggish database response due to backup corruption issues.",
"Firewall misconfiguration allowed unauthorized access.",
"Server reboot flagged during load testing operations.",
"Security patch missing from production system; risk flagged.",
"Repeated FTP connection failures detected for external clients.",
"ARP spoofing detected during endpoint network scans.",
"Encryption key mismatch detected between nodes in production.",
"Critical patch missing scheduled updates on key systems.",
"DDoS mitigation triggered during heavy external activity.",
"Malware protection disabled on user workstation.",
"Unscheduled system reboot interrupted high-priority processing.",
"Memory allocation errors caused stoppage in workload scheduling.",
"Performance slowdowns observed during API monitoring.",
"Login attempt flagged: blacklisted IPs detected.",
"Rogue access flagged on external production server.",
"High volume of API calls flagged; system overload.",
"Unexpected database schema changes caused request failures.",
"Malware alert triggered during active scan.",
"High errors detected due to outdated system protocols.",
"Unauthorized session hijack on application server.",
"Failed packet transmission in monitoring interfaces.",
"Database rollback failed due to corrupted backup imports.",
"Failed robot order execution due to unexpected timeout conditions.",
"Cloud synchronization failure reported after update processing.",
"Suspicious behavior flagged in user login analytics.",
"Keylogger activity detected on privileged employee machine.",
"Remote access termination due to suspicious session triggers.",
"High in-memory data requests overloaded server processing.",
"File permissions misconfigured; access denied on critical assets.",
"Cloud storage exposed publicly due to account misconfiguration.",
"SSL handshake timed out during multi-instance connection attempt.",
"JIRA system flagged as inaccessible due to SAML failure.",
"Critical security incident flagged during ongoing monitoring operations.",
"Spam detection flagged phishing email within response actions.",
"Root server flagged down during workflow trigger scheduling.",
"Failed SSO validation from outdated authentication handshake.",
"Multiple hostname errors flagged due to mismatched entries in logs.",
"System-wide connectivity notice issued: Multi-site impacted change.",
"Cloud instance failed synchronization with on-prem DB cluster.",
"Database server flagged with delays and query timeouts.",
"Multi-factor authentication failure for privileged accounts.",
"System configuration process flagged as misaligned during audit checks.",
"DNS monitoring errors flagged from edge-scanning logs.",
"Critical alarm raised for SLA noncompliance on production server tickets.",
"Repeated failed ping attempts logged for external endpoint.",
"VPN tunnel flag uncovered during traffic multiplexer configuration checks.",
"Performance bottlenecks delayed response from analysis cluster.",
"Support ticket volumes identified as increasing peak trends during morning hours.",
"Workload forecasting triggered after peak hours response logs clustered anomalies.",
"Content management breach flagged in cross-routed traffic diagnostic monitors.",
"Insights prompted resolution sequences stalled during KPI analysis revision cases.",
"Unencrypted email flagged during sensitive admin data processes matrix heading.",
"Preventative trial flagged confidence cases staging priority upticks during clustered metrics snapshot.",
"Data threshold exceeded causing mainframe overload flag upstream details cluster pipeline inline faults matrix overview.",
"Unexpected lockout flagged during Privileged Access re-validation.",
"Request errors logged during cloud synchronization monitoring stages flagged aggregations indicating fallback overload metric stages high-level.",
"Incident flagged requiring multi-stage manual response process-layer specifics detailed high-priority assessment handling escalation batches linked matrix revisions queues overall." 
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
        "Monday": (90, 170),
        "Tuesday": (100, 180),
        "Wednesday": (80, 160),
        "Thursday": (70, 150),
        "Friday": (60, 120),
        "Saturday": (20, 60),
        "Sunday": (10, 30)
    }.get(day_of_week, (50, 100)))

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
output_file_path =  r"synthetic_incident_bank_data_weighted.csv"
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
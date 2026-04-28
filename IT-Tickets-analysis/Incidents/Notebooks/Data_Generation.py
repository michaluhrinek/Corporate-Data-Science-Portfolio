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
 "User unable to log in to corporate VPN",
    "Email client not connecting to mail server",
    "Application response time extremely slow for multiple users",
    "Shared network drive not accessible",
    "Printer not printing documents from any workstation",
    "User account locked after multiple failed login attempts",
    "External website not reachable from corporate network",
    "Database connection error in production application",
    "Incorrect data displayed in reporting dashboard",
    "Newly created user not syncing to all systems",
    "Single user laptop not connecting to Wi-Fi",
    "Frequent disconnections from remote desktop session",
    "Error 500 returned by internal web application",
    "Antivirus alert triggered on user workstation",
    "Batch job failed to complete overnight",
    "File restore from backup failed for requested folder",
    "VoIP phone not registering with call manager",
    "Multiple users experiencing Outlook crashes",
    "Mobile app login failing for all users",
    "Unexpected reboot of application server",
    "High CPU usage on database server impacting performance",
    "Network latency observed between data center and branch office",
    "User unable to access HR portal",
    "Incorrect permissions on shared folder causing access denied",
    "Single sign-on not working for cloud application",
    "Multi-factor authentication code not delivered to user",
    "New software installation failing on endpoint",
    "User’s mailbox not receiving external emails",
    "Queue processing stuck in payment application",
    "Corrupt file detected in document management system",
    "Scheduled report not generated or delivered",
    "User unable to change expired password remotely",
    "Network printer not visible in device list",
    "Unexpected logout from critical application during use",
    "Time synchronization issue causing authentication failures",
    "Error while uploading documents to intranet portal",
    "Intermittent connectivity issues to file server",
    "Unauthorized login attempt alert for admin account",
    "Incorrect display of currency values in front-end",
    "Broken link on intranet home page",
    "Unexpected high memory usage on web server",
    "User profile not loading correctly after login",
    "Old password still granting access to system",
    "Firewall blocking legitimate traffic to partner system",
    "Endpoint disk space critically low warning",
    "Application crash when user attempts specific function",
    "User not receiving password reset email",
    "Network outage in specific office floor",
    "Barcode scanner not transmitting data to system",
    "Time-out errors when accessing CRM system",
    "USB device not recognized on workstation",
    "Incorrect group membership causing access escalation",
    "Corrupted email attachments received internally",
    "SSL certificate error when accessing internal site",
    "Unexpected application log errors after deployment",
    "Data export from system failing with error",
    "Duplicate records appearing in customer database",
    "Incorrect user mapping in identity provider",
    "Delayed message delivery in internal chat system",
    "User unable to open encrypted email",
    "Intermittent packet loss on WAN link",
    "Incorrect language settings applied to user interface",
    "Auto-save not working in productivity application",
    "Endpoint not checking in with management server",
    "User home drive not mapping at login",
    "Access badge system not updating from central database",
    "Printing jobs stuck in queue without error message",
    "Application not launching after latest OS update",
    "Local profile corrupted on shared workstation",
    "Frequent password prompts despite valid authentication"
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
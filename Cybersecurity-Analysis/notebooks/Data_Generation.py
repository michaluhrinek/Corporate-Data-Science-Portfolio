# Import necessary libraries
import sys
import polars as pl
import random
import os
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

# Define state probabilities (weights) and other sample data
states_weights = [
    ("Closed", 85),
    ("New", 5),
    ("In Progress", 5),
    ("On Hold", 5)
]

change_environments = ["Access", "Complaint", "Hardware", "Software", "Network", "Failure", "Facilities", "Data"]

short_descriptions = [
     "Suspicious login attempt from unknown IP address",
    "Multiple failed login attempts detected on user account",
    "Unusual VPN connection outside normal working hours",
    "Endpoint antivirus detected and quarantined malware",
    "Unauthorized installation of unapproved software",
    "Phishing email reported by employee",
    "Malicious attachment blocked by email gateway",
    "Account lockout due to repeated failed authentication",
    "Unusual data download volume from file server",
    "Access request to restricted application reviewed",
    "Privilege escalation attempt on production server",
    "Unauthorized access to shared network drive",
    "Suspicious PowerShell activity detected on workstation",
    "Multiple logins from different countries within short timeframe",
    "Unapproved external USB storage device connected",
    "Firewall detected and blocked port scanning activity",
    "New device connected to corporate Wi-Fi without registration",
    "Suspicious outbound traffic to known malicious domain",
    "Ransomware behavior detected and contained on endpoint",
    "Unsupported legacy protocol usage detected in network traffic",
    "Unencrypted data transfer detected over public network",
    "Unexpected configuration change on security appliance",
    "Unauthorized attempt to disable endpoint protection",
    "Unusual administrative activity on domain controller",
    "Multiple failed VPN authentication attempts from external IP",
    "Brute force attack detected on remote access gateway",
    "Suspicious login attempt using expired credentials",
    "Compromised account password reset and user notified",
    "Unusual access pattern to customer data records",
    "Email account used to send large volume of external messages",
    "Data loss prevention policy violation detected",
    "Blocked attempt to upload sensitive data to cloud storage",
    "Privileged user access review identified anomalies",
    "New privileged account created without proper approval",
    "Security policy violation on mobile device",
    "Unapproved application communicating with external server",
    "Web proxy blocked access to high-risk website",
    "Malicious JavaScript detected on visited webpage",
    "Suspicious authentication token reuse detected",
    "New local administrator account detected on endpoint",
    "Login from decommissioned device detected in logs",
    "Unusual spike in security alerts for single user",
    "Multiple password reset requests from same user",
    "Suspicious file execution blocked by application control",
    "Abnormal outbound DNS requests from single host",
    "Unauthorized attempt to access HR system",
    "Anomalous login pattern for service account",
    "Certificate validation failure on secure connection",
    "Unsupported remote desktop tool detected on endpoint",
    "Unapproved connection to third-party cloud service",
    "Email forwarding rule created without user knowledge",
    "Suspicious modification of registry keys on workstation",
    "Inactive account used for login attempt",
    "Malicious macro detected in office document",
    "Endpoint reported repeated blocked exploit attempts",
    "New network share created without change request",
    "Unauthorized attempt to access security logs",
    "Unusual file encryption activity detected on server",
    "Abnormal API access pattern from external client",
    "External IP added to whitelist without approval",
    "Suspicious authentication attempts to database server",
    "Denied attempt to access privileged management console",
    "Multiple devices reporting same malware signature",
    "Unapproved remote access session initiated",
    "Unusual traffic to anonymization service detected",
    "Attempted login using default system credentials",
    "Network scan originating from internal segment detected"
]

# Generate synthetic data for the year 2025
data = []

# Define date range for the year 2025
start_date_2025 = datetime(2025, 1, 1)
end_date_2025 = datetime(2025, 12, 31)

# Initialize ticket number
ticket_number = 1

# Helper function for generating random timedelta
def random_timedelta(min_hours, max_hours):
    return timedelta(
        hours=random.randint(min_hours, max_hours),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )

# Iterate through each day in 2025 to generate tickets
current_date = start_date_2025

while current_date <= end_date_2025:
    # Generate a random number of records for this day (70-140)
    num_records_today = random.randint(70, 140)

    for _ in range(num_records_today):
        # Generate Created time for the ticket
        created_date = current_date + random_timedelta(0, 23)

        # Assign State randomly based on weighted probabilities
        state = random.choices([state for state, weight in states_weights], weights=[weight for state, weight in states_weights], k=1)[0]

        # Generate logical Start Date and Closed Date
        if state == "Closed":
            start_date = created_date + random_timedelta(1, 8)  # Ensure Start Date is AFTER Created
            closed_date = start_date + random_timedelta(2, 44)  # Ensure Closed Date is AFTER Start Date
        elif state == "In Progress":
            start_date = created_date + random_timedelta(1, 6)  # Ensure Start Date is AFTER Created
            closed_date = None  # Closed does not apply for In Progress
        elif state in ["New", "On Hold"]:
            start_date = None  # Start Date does not apply
            closed_date = None  # Closed does not apply
        else:
            start_date = None  # Default handling
            closed_date = None  # Default handling

        # Add ticket data
        data.append({
            "Number": f"CR-{ticket_number}",
            "Short Description": random.choice(short_descriptions),
            "Change Environment": random.choice(change_environments),
            "Requested By": random.choice(["Jan", "Peter", "Michal", "Martin", "Thor", "Iron Man", "Captain America"]),
            "Assigned To": random.choice(["Jan", "Peter", "Michal", "Martin", "Thor", "Iron Man", "Captain America"]),
            "Assignment Group": random.choice(["Avengers", "Avengers II", "Matrix"]),
            "Service": random.choice(["Service A", "Service B", "Service C"]),
            "State": state,
            "Risk": random.choice(["High", "Medium", "Low"]),
            "Priority": random.choice(["Low", "Medium", "High"]),
            "Urgency": random.choice(["High", "Medium", "Low"]),
            "Impact": random.choice(["High", "Medium", "Low"]),
            "Created": created_date,
            "Start Date": start_date,
            "Closed": closed_date,
            "Reopen Count": random.choice([0, 1])  # Randomly assign 0 or 1 for Reopen Count
        })

        ticket_number += 1

    # Move to the next day
    current_date += timedelta(days=1)

# Create a Polars DataFrame
df = pl.DataFrame(data)

# Add Day of the Week column, good for when were most of the tickets created 
df = df.with_columns([
    pl.col("Created").dt.strftime("%A").alias("Day")  # Extract day of the week
])

# Ensure datetime columns are properly set as datetime objects
df = df.with_columns([
    pl.col("Created").cast(pl.Datetime),
    pl.col("Start Date").cast(pl.Datetime),
    pl.col("Closed").cast(pl.Datetime)
])


# Add a column to flag tickets where Reopen Count is 0
df= df.with_columns([
    (pl.col("Reopen Count") == 0).cast(pl.Int64).alias("Reopen Zero Flag")
])

# Calculate percentage of tickets not reopened
total_tickets = df.shape[0]  # Total number of tickets
non_reopened_tickets = df.select(pl.col("Reopen Zero Flag").sum())[0, 0]  # Sum of Reopen Zero Flags
reopen_percentage = (non_reopened_tickets / total_tickets) * 100

# Print summary statistics
print(f"Total Tickets: {total_tickets}")
print(f"Tickets Not Reopened (Reopen Count = 0): {non_reopened_tickets}")
print(f"Percentage of Tickets Not Reopened: {reopen_percentage:.2f}%")

# Save the dataset to a CSV file
output_file_path = r"synthetic_cybersecurity_bank_data.csv"  #replace x with your own filepath 
output_dir = os.path.dirname(output_file_path)
if output_dir and not os.path.exists(output_dir):
    os.makedirs(output_dir)

df.write_csv(output_file_path)

# Print results
print("Synthetic bank data generated and saved successfully.")
print(f"DataFrame shape: {df.shape}")
print(df.head())
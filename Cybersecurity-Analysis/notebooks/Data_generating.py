# Import necessary libraries
import polars as pl
import random
import os
from datetime import datetime, timedelta

# Define state probabilities (weights) and other sample data
states_weights = [
    ("Closed", 85),
    ("New", 5),
    ("In Progress", 5),
    ("On Hold", 5)
]

change_environments = ["Access", "Complaint", "Hardware", "Software", "Network", "Failure", "Facilities", "Data"]

short_descriptions = [
    "Failed Healthcheck - ID: 111-222-333-444-555 Host: ",
    "Failed Workflow - ID: 0000",
    "User login failed: Account locked due to excessive login attempts.",
    "Service outage detected - No connection to database.",
    "Suspicious activity detected on account: User A.",
    "Network issue: Unable to connect to external API.",
    "Critical alert: Database server overload detected.",
    "Security patch applied: Monitoring for any issues.",
    "Data breach notification sent to affected users.",
    "Performance report: Sluggish response times on application.",
    "Authentication error: Multi-factor authentication failed.",
    "Unauthorized access attempt detected: IP flagged as suspicious.",
    "Firewall breach: Unauthorized access through open port.",
    "Malware alert: Suspicious executable flagged during scan.",
    "Phishing email flagged: User report received for fake login attempt.",
    "DDoS attack detected: High traffic spotted on critical service.",
    "System configuration error: Permissions incorrectly set.",
    "Failed encryption process: Unable to secure sensitive data.",
    "Red team simulation detected: Penetration testing execution.",
    "Unpatched vulnerability flagged: CVE report mismatch detected.",
    "Social engineering attempt flagged: Fake support request identified.",
    "VPN connection failure: Unable to securely tunnel data.",
    "Expired certificates detected: TLS handshake improper.",
    "Data exfiltration alert: Large outbound transfer from server.",
    "Suspicious behavior: Multiple failed login attempts detected.",
    "Critical system alert: Root access attempted on production server.",
    "Cloud misconfiguration alert: Public exposure of sensitive data.",
    "Backup failure: Unable to restore files from recovery system.",
    "Ransomware attack detected: Encrypted files observed on endpoint.",
    "Database schema corruption: Unable to read or query data tables.",
    "Security patch missing: Update not applied on critical server.",
    "Dark web monitoring alert: Credentials detected for sale online.",
    "Failed packet inspection: Firewall rules misconfigured.",
    "Unauthorized device connected: MAC address not whitelisted.",
    "ARP spoofing detected: Network traffic rerouted.",
    "DNS attack detected: Unusual query patterns observed.",
    "Network congestion: High bandwidth usage flagged.",
    "Endpoint offline: Device not syncing with central server.",
    "Suspicious login activity detected: High volume of logins from Device B.",
    "Malware detected on endpoint: Quarantine initiated.",
    "Antivirus disabled on workstation: Protection compromised.",
    "Unscheduled software change: Application version rolled back.",
    "Cloud instance misconfiguration: Public access enabled.",
    "Failed cloud synchronization: Files cannot be uploaded.",
    "Suspicious API calls detected: Abnormal volume of requests identified.",
    "Cloud storage accessed by untrusted device.",
    "User permission escalation detected on cloud platform.",
    "Failed SSO login: Invalid credentials provided.",
    "Privileged account login attempt: Microsoft Admin flagged.",
    "Expired password reset request: User notified.",
    "Locked account: Excessive password retry attempts.",
    "Access request denied: Policy mismatch.",
    "Email flagged as phishing: Sensitive keywords detected.",
    "Ransomware execution blocked by endpoint protection.",
    "Keylogger activity detected on user's workstation.",
    "Malicious macro executed within Office file.",
    "Failed malware removal: Corrupted file system detected.",
    "SOC analyst triggered investigation for suspicious server activity.",
    "Breach alert: Privileged credentials exposed.",
    "Login attempt from blacklisted IP address blocked.",
    "DDoS attack mitigation active: Rate-limiting initiated.",
    "Critical security incident logged: Immediate remediation required.",
    "SQL injection attempt: Unauthorized queries flagged.",
    "Web application timeout: Performance degradation observed.",
    "Cross-site scripting (XSS) detected on customer portal.",
    "Web server certificate expired: Issue flagged for priority teams.",
    "Unauthorized user session hijacked on browser.",
    "Data download from personal device flagged for review.",
    "Unencrypted sensitive file shared externally.",
    "File integrity check failed: Data corruption suspected.",
    "Data exfiltration alert: High outbound traffic flagged.",
    "Unscheduled file deletion detected on shared drive.",
    "Failed security training attempt recorded in training portal.",
    "Backup server unreachable: Error code 502.",
    "Network scanning tool triggered security alert.",
    "Database transaction rollback error flagged for audit.",
    "Server reboot required: Kernel update incomplete.",
    "Unusual system reboot detected on DevOps environment.",
    "Memory exhaustion detected: Application terminated unexpectedly.",
    "USB device blocked: Removable media protection active.",
    "Power failure simulation triggered during red team activity.",
    "Internal network inaccessible: Ping requests time out."
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
            start_date = created_date + random_timedelta(2, 8)
            closed_date = start_date + random_timedelta(2, 44)
        elif state == "In Progress":
            start_date = created_date + random_timedelta(2, 6)
            closed_date = None
        elif state in ["New", "On Hold"]:
            start_date = None
            closed_date = None
        else:
            start_date = None
            closed_date = None

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
output_file_path = r"C:\Users\HA2UHRI\Downloads\synthetic_cybersecurity_bank_data.csv"
output_dir = os.path.dirname(output_file_path)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

df.write_csv(output_file_path)

# Print results
print("Synthetic bank data generated and saved successfully.")
print(f"DataFrame shape: {df.shape}")
print(df.head())
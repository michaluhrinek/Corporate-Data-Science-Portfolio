import polars as pl
import random
from datetime import datetime, timedelta


# Function to randomly adjust the Created time for more realistic timestamps
def randomize_time(base_date):
    random_hour = random.randint(0, 23)  # Random hour of the day
    random_minute = random.randint(0, 59)  # Random minute
    random_second = random.randint(0, 59)  # Random second
    return base_date + timedelta(hours=random_hour, minutes=random_minute, seconds=random_second)


# Function to generate Start and Closed dates that follow logical order
def generate_dates(created_date, state):
    # Ensure Start Date > Created Date and Closed Date > Start Date
    if state == "Closed":
        # Random Start Date strictly after Created Date (2-8 hours)
        start_date = created_date + timedelta(
            hours=random.randint(2, 8), minutes=random.randint(0, 59), seconds=random.randint(0, 59)
        )
        # Random Closed Date strictly after Start Date (2-44 hours)
        closed_date = start_date + timedelta(
            hours=random.randint(2, 44), minutes=random.randint(0, 59), seconds=random.randint(0, 59)
        )
        return start_date, closed_date

    elif state == "In Progress":
        # Start Date strictly after Created Date
        start_date = created_date + timedelta(
            hours=random.randint(2, 6), minutes=random.randint(0, 59), seconds=random.randint(0, 59)
        )
        return start_date, None

    elif state in ["New", "On Hold"]:
        # Neither Start nor Closed exist
        return None, None

    else:
        return None, None


# Define categories for the Change Environment
change_environments = [
    "Access", "Complaint", "Hardware", "Software", "Network", "Failure", "Facilities", "Data"
]

# State weights for generating realistic ticket states
states_weights_2025 = [
    ("Closed", 0.85),      # 85% Closed
    ("New", 0.05),         # 5% New
    ("In Progress", 0.05), # 5% In Progress
    ("On Hold", 0.05)      # 5% On Hold
]

# Extended list of short descriptions
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

# Function to fetch a state based on weighted probabilities
def get_state():
    return random.choices(
        [state for state, _ in states_weights_2025],
        weights=[weight for _, weight in states_weights_2025],
        k=1
    )[0]


# Generate synthetic data for the year 2025
data = []

# Define date range for the year 2025
start_date_2025 = datetime(2025, 1, 1)
end_date_2025 = datetime(2025, 12, 31)

# Iterate through each day in 2025 to generate tickets
current_date = start_date_2025
ticket_number = 1  # Initialize ticket counter

while current_date <= end_date_2025:
    # Generate a random number of records for this day (70-140)
    num_records_today = random.randint(70, 140)

    for _ in range(num_records_today):
        # Randomize the Created time for the ticket
        created_date = randomize_time(current_date)

        # Assign State
        state = get_state()

        # Generate Start Date and Closed Date based on state
        start_date, closed_date = generate_dates(created_date, state)

        # Add a ticket record to the dataset
        data.append({
            "Number": f"CR-{ticket_number}",
            "Short description": random.choice(short_descriptions),
            "Change Environment": random.choice(change_environments),
            "Requested by": random.choice(["Jan", "Peter", "Michal", "Martin", "Thor", "Iron Man", "Captain America", "Black Panther", "John Wick", "Hulk"]),
            "Assigned to": random.choice(["Jan", "Peter", "Michal", "Martin", "Thor", "Iron Man", "Captain America", "Black Panther", "John Wick", "Hulk"]),
            "Assignment group": random.choice(["Avengers", "Avengers II", "Matrix"]),
            "Service": random.choice(["Service A", "Service B", "Service C"]),
            "State": state,
            "Risk": random.choice(["High", "Medium", "Low"]),
            "Priority": random.choice(["Low", "Medium", "High"]),
            "Urgency": random.choice(["High", "Medium", "Low"]),
            "Impact": random.choice(["High", "Medium", "Low"]),
            "Created": created_date,
            "Start Date": start_date,
            "Closed": closed_date
        })

        ticket_number += 1  # Increment the ticket counter

    # Move to the next day
    current_date += timedelta(days=1)

# Create a Polars DataFrame
df = pl.DataFrame(data)

# Format datetime columns
formatted_df = df.with_columns([
    pl.col("Created").dt.strftime("%d/%m/%Y %H:%M:%S").alias("Created"),
    pl.col("Start Date").dt.strftime("%d/%m/%Y %H:%M:%S").alias("Start Date"),
    pl.col("Closed").dt.strftime("%d/%m/%Y %H:%M:%S").alias("Closed"),
])

# Add Day of the Week column based on 'Created'
formatted_df = formatted_df.with_columns([
    formatted_df["Created"].str.strptime(pl.Date, "%d/%m/%Y %H:%M:%S").dt.strftime("%A").alias("Day")
])

#preparing columns names for other file because there my code has different names 
final_df = formatted_df.rename({
    "Start Date": "Actual start",
    "Created": "Created",
    "Number": "Number",
    "Priority": "Priority",
    "Assignment group": "Assignment group",
    "State": "State",
    "Short description": "Short description",
    "Risk": "Risk score",
    "Opened": "Opened",
    "Requested by": "Requested by",
    "Urgency": "Urgency",
    "Day":"Day"
})

final_df = final_df.with_columns(
    pl.col("Closed").alias("Actual end")  # Duplicate 'Closed' as 'Actual end'
)

# Save to a CSV file for later use
output_file_path = r"C:\Users\Downloads\synthetic_cybersecurity_data_with_days.csv"
final_df.write_csv(output_file_path)

print("Synthetic data generated and saved successfully with Day column.")
print(f"Generated DataFrame shape: {final_df.shape}")
print(final_df.head())

#Synthetic Data Generation for Payments Volume Dataset (2025)
#import libraries and set up environment
import sys
sys.stdout.reconfigure(encoding='utf-8')

import polars as pl
import random
from datetime import datetime, timedelta

# ─── TEAMS & MEMBERS ───────────────────────────────────────────────────────────
teams = {
    "Avengers": ["Thor", "Iron Man", "Hulk", "Doctor Strange"],
    "DC":       ["Batman", "Aquaman", "Punisher", "Dr. X"],
    "People":   ["Mark", "The Rock", "Jackie Chan", "Kevin Hart", "Dwayne Johnson", "Scarlett Johansson"],
}
team_weights = [0.40, 0.35, 0.25]   # Avengers handle most complex work

# ─── PROCESS → SYSTEM MAPPING ──────────────────────────────────────────────────
# Reflects real banking: Stargate = cross-border, STP CAT = domestic clearing, SOLEMOS = rates/manual
process_system_map = {
    "International Transfer": [("Stargate",  1.00)],
    "SEPA Payment":           [("Stargate",  0.65), ("STP CAT", 0.35)],
    "Domestic Payment":       [("STP CAT",   1.00)],
    "Basic Payment":          [("STP CAT",   1.00)],
    "Rates":                  [("SOLEMOS",   1.00)],
    "Edit Q":                 [("SOLEMOS",   0.80), ("STP CAT", 0.20)],
}

# ─── TEAM → PROCESS AFFINITY ───────────────────────────────────────────────────
# Avengers = complex cross-border, DC = domestic/bulk, People = manual/operational
team_process_weights = {
    "Avengers": {
        "International Transfer": 0.35,
        "SEPA Payment":           0.30,
        "Rates":                  0.20,
        "Edit Q":                 0.10,
        "Domestic Payment":       0.03,
        "Basic Payment":          0.02,
    },
    "DC": {
        "Domestic Payment":       0.35,
        "Basic Payment":          0.30,
        "SEPA Payment":           0.20,
        "Edit Q":                 0.10,
        "International Transfer": 0.03,
        "Rates":                  0.02,
    },
    "People": {
        "Edit Q":                 0.35,
        "Basic Payment":          0.30,
        "Domestic Payment":       0.20,
        "Rates":                  0.10,
        "SEPA Payment":           0.04,
        "International Transfer": 0.01,
    },
}

# ─── PRIORITY WEIGHTS BY PROCESS ───────────────────────────────────────────────
priority_weights_by_process = {
    "International Transfer": {"Critical": 0.25, "High": 0.45, "Medium": 0.20, "Low": 0.10},
    "SEPA Payment":           {"Critical": 0.15, "High": 0.35, "Medium": 0.40, "Low": 0.10},
    "Domestic Payment":       {"Critical": 0.05, "High": 0.20, "Medium": 0.50, "Low": 0.25},
    "Basic Payment":          {"Critical": 0.05, "High": 0.15, "Medium": 0.50, "Low": 0.30},
    "Rates":                  {"Critical": 0.30, "High": 0.40, "Medium": 0.25, "Low": 0.05},
    "Edit Q":                 {"Critical": 0.05, "High": 0.20, "Medium": 0.55, "Low": 0.20},
}

# ─── PRIORITY → URGENCY & IMPACT ───────────────────────────────────────────────
priority_urgency_impact = {
    "Critical": {
        "Urgency": [("High", 0.90), ("Medium", 0.10)],
        "Impact":  [("High", 0.85), ("Medium", 0.15)],
    },
    "High": {
        "Urgency": [("High", 0.70), ("Medium", 0.30)],
        "Impact":  [("High", 0.60), ("Medium", 0.35), ("Low", 0.05)],
    },
    "Medium": {
        "Urgency": [("Medium", 0.70), ("Low", 0.30)],
        "Impact":  [("Medium", 0.80), ("Low", 0.20)],
    },
    "Low": {
        "Urgency": [("Low", 1.0)],
        "Impact":  [("Low", 1.0)],
    },
}

# ─── VOLUME RANGES (number of transactions per ticket) ─────────────────────────
volume_ranges = {
    "International Transfer": (1,      50),
    "SEPA Payment":           (500, 100_000),
    "Domestic Payment":       (100,  20_000),
    "Basic Payment":          (50,    5_000),
    "Rates":                  (1,        10),
    "Edit Q":                 (1,       250),
}

# ─── RESOLUTION TIME IN HOURS BY PRIORITY ──────────────────────────────────────
resolution_hours = {
    "Critical": (0.1,  4),
    "High":     (2,   17),
    "Medium":   (6,   36),
    "Low":      (16,  96),
}

# ─── DAILY TICKET VOLUMES ──────────────────────────────────────────────────────
daily_volume = {
    "Monday":    (80, 210),   # High - backlog from weekend
    "Tuesday":   (120, 207),
    "Wednesday": (110, 175),
    "Thursday":  (100, 300),
    "Friday":    (75,  135),   # Drops toward end of week
    "Saturday":  (20,   200),
    "Sunday":    (10,   120),
}

# ─── HELPER ────────────────────────────────────────────────────────────────────
def weighted_choice(options_weights):
    options = [o for o, _ in options_weights]
    weights = [w for _, w in options_weights]
    return random.choices(options, weights=weights, k=1)[0]

# ─── GENERATE DATA ─────────────────────────────────────────────────────────────
data = []
ticket_number = 1
current = datetime(2025, 1, 1)
end = datetime(2025, 12, 31)

# Business hours weighted: low overnight, peak 8am-6pm
hour_weights = [1]*8 + [6]*10 + [2]*6   # indices 0-23

while current <= end:
    day_name = current.strftime("%A")
    num_tickets = random.randint(*daily_volume[day_name])

    for _ in range(num_tickets):
        # Team and member
        team   = random.choices(list(teams.keys()), weights=team_weights, k=1)[0]
        member = random.choice(teams[team])

        # Process based on team specialty
        pw      = team_process_weights[team]
        process = random.choices(list(pw.keys()), weights=list(pw.values()), k=1)[0]

        # System based on process
        system = weighted_choice(process_system_map[process])

        # Priority based on process realism
        ppw      = priority_weights_by_process[process]
        priority = random.choices(list(ppw.keys()), weights=list(ppw.values()), k=1)[0]

        # Urgency and Impact correlated to priority
        urgency = weighted_choice(priority_urgency_impact[priority]["Urgency"])
        impact  = weighted_choice(priority_urgency_impact[priority]["Impact"])

        # State distribution
        state = random.choices(
            ["Closed", "In Progress", "New", "On Hold"],
            weights=[0.88, 0.06, 0.04, 0.02],
            k=1
        )[0]

        # Created timestamp - biased toward business hours
        hour    = random.choices(range(24), weights=hour_weights, k=1)[0]
        created = current.replace(
            hour=hour,
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )

        # Dates: Actual Start → Actual End → Closed
        if state == "Closed":
            actual_start = created + timedelta(minutes=random.randint(10, 90))
            work_hrs     = random.uniform(*resolution_hours[priority])
            actual_end   = actual_start + timedelta(hours=work_hrs)
            closed       = actual_end + timedelta(minutes=random.randint(15, 90))
        elif state == "In Progress":
            actual_start = created + timedelta(minutes=random.randint(10, 60))
            actual_end   = None
            closed       = None
        else:   # New / On Hold
            actual_start = None
            actual_end   = None
            closed       = None

        # Volume of transactions affected
        volume = random.randint(*volume_ranges[process])

        data.append({
            "Number":            f"INC-2025-{ticket_number:05d}",
            "Type of Payment":   process,
            "Process":           process,
            "System":            system,
            "Volume":            volume,
            "Assignment Group":  team,
            "Assigned To":       member,
            "State":             state,
            "Priority":          priority,
            "Urgency":           urgency,
            "Impact":            impact,
            "Day":               day_name,
            "Created":           created,
            "Actual Start":      actual_start,
            "Actual End":        actual_end,
            "Closed":            closed,
        })

        ticket_number += 1

    current += timedelta(days=1)

# ─── BUILD DATAFRAME ───────────────────────────────────────────────────────────
df = pl.DataFrame(data, schema_overrides={
    "Created":      pl.Datetime,
    "Actual Start": pl.Datetime,
    "Actual End":   pl.Datetime,
    "Closed":       pl.Datetime,
})

# ─── SAVE CSV ──────────────────────────────────────────────────────────────────
output_path = r"C:\Users\X\Downloads\payments\payments_volume_2025.csv"          #/change the X and path as needed based on your filepath to your file 
df.write_csv(output_path)


# ─── SUMMARY ───────────────────────────────────────────────────────────────────
print(f"\nTotal Tickets Generated : {df.shape[0]:,}")
print(f"Date Range              : 2025-01-01  to  2025-12-31")

print(f"\n--- Tickets by Team ---")
print(df.group_by("Assignment Group").agg(pl.col("Number").count().alias("Tickets")).sort("Tickets", descending=True))

print(f"\n--- Tickets by Process ---")
print(df.group_by("Process").agg(pl.col("Number").count().alias("Tickets")).sort("Tickets", descending=True))

print(f"\n--- Tickets by System ---")
print(df.group_by("System").agg(pl.col("Number").count().alias("Tickets")).sort("Tickets", descending=True))

print(f"\n--- Total Transaction Volume by Process ---")
print(df.group_by("Process").agg(pl.col("Volume").sum().alias("Total Volume")).sort("Total Volume", descending=True))

print(f"\n--- Priority Distribution ---")
print(df.group_by("Priority").agg(pl.col("Number").count().alias("Count")).sort("Count", descending=True))

print(f"\nDataset saved to: {output_path}")
print(f"\n--- Preview (first 5 rows) ---")
print(df.head(5))

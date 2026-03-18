# ─── PAYMENTS ERRORS DATA GENERATION ─────────────────────────────────────────
import sys
sys.stdout.reconfigure(encoding='utf-8')

import polars as pl
import random
from datetime import datetime, timedelta
import calendar

# ─── TEAMS & MEMBERS ───────────────────────────────────────────────────────────
teams = {
    "Avengers": ["Thor", "Iron Man", "Hulk", "Doctor Strange"],
    "DC":       ["Batman", "Aquaman", "Punisher", "Dr. X"],
    "People":   ["Mark", "The Rock", "Jackie Chan", "Kevin Hart", "Dwayne Johnson", "Scarlett Johansson"],
}

# ─── PROCESS → SYSTEM MAPPING ──────────────────────────────────────────────────
process_system_map = {
    "International Transfer": [("Stargate",  1.00)],
    "SEPA Payment":           [("Stargate",  0.65), ("STP CAT", 0.35)],
    "Domestic Payment":       [("STP CAT",   1.00)],
    "Basic Payment":          [("STP CAT",   1.00)],
    "Rates":                  [("SOLEMOS",   1.00)],
    "Edit Q":                 [("SOLEMOS",   0.80), ("STP CAT", 0.20)],
}

# ─── TEAM → PROCESS AFFINITY ───────────────────────────────────────────────────
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

# ─── ERROR SHORT DESCRIPTIONS ──────────────────────────────────────────────────
short_descriptions = {
    "International Transfer": [
        "Wrong beneficiary IBAN entered - payment sent to incorrect account",
        "Incorrect BIC code used - wire transfer routed to wrong bank",
        "Wrong currency selected - USD payment sent instead of EUR",
        "Duplicate international wire submitted - double payment issued",
        "Incorrect amount entered - overpayment of 10x original value",
        "Wrong value date set - payment settled one day early",
        "Missing payment reference - correspondent bank unable to apply funds",
        "Incorrect correspondent bank selected for USD settlement",
        "Payment submitted without required compliance pre-approval",
        "Wrong account debited - fee charged to incorrect cost centre",
        "SWIFT message sent with incorrect sender reference",
        "Payment dispatched to sanctioned entity - compliance breach",
    ],
    "SEPA Payment": [
        "Wrong IBAN entered in bulk SEPA file - batch partially rejected",
        "SEPA file submitted with incorrect execution date",
        "Duplicate SEPA batch uploaded - double payments issued to beneficiaries",
        "Wrong debtor account used in SEPA Direct Debit collection",
        "SEPA payment amount keyed incorrectly - underpayment to supplier",
        "Mandate reference missing from SEPA Direct Debit submission",
        "SEPA recall issued too late - funds already credited and withdrawn",
        "Wrong creditor name in SEPA file causing beneficiary mismatch",
        "SEPA batch submitted after cut-off - delayed by one business day",
        "Incorrect end-to-end reference causing reconciliation failure",
        "SEPA payment sent to closed account - return not processed timely",
        "Wrong remittance information causing invoice matching failure",
    ],
    "Domestic Payment": [
        "Wrong sort code entered - domestic payment routed to wrong bank",
        "Incorrect account number used - funds credited to wrong customer",
        "Standing order set up with wrong payment amount",
        "Domestic payment submitted twice - duplicate detected post-settlement",
        "Wrong payment date configured - standing order triggered early",
        "Payment sent without required second authorisation",
        "Incorrect payee reference causing failure to match invoice",
        "Domestic transfer sent to dormant account - return not monitored",
        "Wrong currency applied to domestic GBP payment",
        "Payment limit exceeded due to manual override without approval",
        "Batch domestic file contained incorrect beneficiary account details",
        "Reversal not processed after customer cancellation request",
    ],
    "Basic Payment": [
        "Wrong account debited for basic payment instruction",
        "Incorrect amount entered - customer overcharged",
        "Payment posted to wrong GL account - reconciliation discrepancy",
        "Basic payment processed on wrong value date",
        "Duplicate payment entry not caught before submission",
        "Payment instruction processed without customer authorisation",
        "Wrong fee applied to basic payment transaction",
        "Payment not reversed after customer dispute was resolved",
        "Incorrect currency conversion applied to basic payment",
        "Transaction limit breach not flagged during processing",
        "Payment applied to wrong customer account after name match failure",
        "Basic payment keyed with transposed digits in account number",
    ],
    "Rates": [
        "Wrong FX rate applied to customer transaction - financial loss",
        "Stale rate used after feed failure - not escalated in time",
        "Incorrect rate override entered manually by operator",
        "FX rate applied before market open - incorrect indicative rate used",
        "Wrong currency pair rate applied - EUR/GBP used instead of EUR/USD",
        "Rate tolerance breach not escalated to treasury desk",
        "Manual rate entry typo caused overcharge to client",
        "Fallback rate not updated after primary feed outage",
        "Incorrect interest rate applied to overnight settlement",
        "Rate effective date set incorrectly - wrong rate applied to batch",
        "Cross-rate calculation error not caught before payment dispatch",
        "FX hedge rate misapplied to wrong transaction batch",
    ],
    "Edit Q": [
        "Edit Queue item approved without verifying beneficiary details",
        "Wrong payment details amended in Edit Q - error compounded",
        "Edit Queue item released without required dual authorisation",
        "Incorrect amount corrected to wrong value during manual review",
        "Payment in Edit Q actioned by unauthorised operator",
        "Edit Q item closed without resolution - payment lost in queue",
        "Wrong IBAN updated during manual correction in Edit Queue",
        "Edit Queue SLA breached - payment delayed beyond agreed window",
        "Operator amended wrong field in Edit Queue - further error introduced",
        "Edit Q item duplicated after system timeout during save",
        "Payment released from Edit Q to wrong processing queue",
        "Manual override applied in Edit Q without supervisor sign-off",
    ],
}

# ─── PRIORITY WEIGHTS FOR ERRORS ───────────────────────────────────────────────
priority_weights_by_process = {
    "International Transfer": {"Critical": 0.30, "High": 0.50, "Medium": 0.15, "Low": 0.05},
    "SEPA Payment":           {"Critical": 0.20, "High": 0.45, "Medium": 0.30, "Low": 0.05},
    "Domestic Payment":       {"Critical": 0.10, "High": 0.35, "Medium": 0.45, "Low": 0.10},
    "Basic Payment":          {"Critical": 0.10, "High": 0.30, "Medium": 0.45, "Low": 0.15},
    "Rates":                  {"Critical": 0.35, "High": 0.45, "Medium": 0.15, "Low": 0.05},
    "Edit Q":                 {"Critical": 0.10, "High": 0.35, "Medium": 0.45, "Low": 0.10},
}

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

# ─── RESOLUTION TIME IN HOURS BY PRIORITY ──────────────────────────────────────
resolution_hours = {
    "Critical": (0.2,  3),
    "High":     (2,   6),
    "Medium":   (6,   24),
    "Low":      (16,  48),
}

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def weighted_choice(options_weights):
    options = [o for o, _ in options_weights]
    weights = [w for _, w in options_weights]
    return random.choices(options, weights=weights, k=1)[0]

def random_datetime_in_day(day: datetime) -> datetime:
    hour_weights = [1]*8 + [6]*10 + [2]*6
    hour = random.choices(range(24), weights=hour_weights, k=1)[0]
    return day.replace(hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59))

# ─── GENERATE DATA ─────────────────────────────────────────────────────────────
data = []
ticket_number = 1

for month in range(1, 13):
    # Each team gets its own independent random error count for this month (30–550)
    team_monthly_errors = {team: random.randint(30, 550) for team in teams}

    days_in_month = calendar.monthrange(2025, month)[1]
    month_days    = [datetime(2025, month, d) for d in range(1, days_in_month + 1)]

    # Weekdays get 5x more errors than weekends (realistic bank environment)
    day_weights = [
        5 if datetime(2025, month, d).weekday() < 5 else 1
        for d in range(1, days_in_month + 1)
    ]

    for team, total_errors in team_monthly_errors.items():
        assigned_days = random.choices(month_days, weights=day_weights, k=total_errors)

        for day in assigned_days:
            member   = random.choice(teams[team])
            pw       = team_process_weights[team]
            process  = random.choices(list(pw.keys()), weights=list(pw.values()), k=1)[0]
            system   = weighted_choice(process_system_map[process])

            ppw      = priority_weights_by_process[process]
            priority = random.choices(list(ppw.keys()), weights=list(ppw.values()), k=1)[0]
            urgency  = weighted_choice(priority_urgency_impact[priority]["Urgency"])
            impact   = weighted_choice(priority_urgency_impact[priority]["Impact"])

            state = random.choices(
                ["Closed", "In Progress", "New", "On Hold"],
                weights=[0.90, 0.05, 0.03, 0.02],
                k=1
            )[0]

            created = random_datetime_in_day(day)

            if state == "Closed":
                actual_start = created + timedelta(minutes=random.randint(10, 90))
                actual_end   = actual_start + timedelta(hours=random.uniform(*resolution_hours[priority]))
                closed       = actual_end + timedelta(minutes=random.randint(15, 90))
            elif state == "In Progress":
                actual_start = created + timedelta(minutes=random.randint(10, 60))
                actual_end   = None
                closed       = None
            else:
                actual_start = None
                actual_end   = None
                closed       = None

            data.append({
                "Number":            f"ERR-2025-{ticket_number:05d}",
                "Short Description": random.choice(short_descriptions[process]),
                "Process":           process,
                "System":            system,
                "Assignment Group":  team,
                "Assigned To":       member,
                "State":             state,
                "Priority":          priority,
                "Urgency":           urgency,
                "Impact":            impact,
                "Day":               day.strftime("%A"),
                "Created":           created,
                "Actual Start":      actual_start,
                "Actual End":        actual_end,
                "Closed":            closed,
            })

            ticket_number += 1

# ─── BUILD DATAFRAME ───────────────────────────────────────────────────────────
df = pl.DataFrame(data, schema_overrides={
    "Created":      pl.Datetime,
    "Actual Start": pl.Datetime,
    "Actual End":   pl.Datetime,
    "Closed":       pl.Datetime,
})

# ─── SAVE CSV ──────────────────────────────────────────────────────────────────
output_path = r"C:\Users\X\Downloads\payments\payments_errors_2025.csv"     #/change the X and path as needed based on your filepath to your file 
df.write_csv(output_path)

# ─── SUMMARY ───────────────────────────────────────────────────────────────────



print(f"\nTotal Errors Generated  : {df.shape[0]:,}")
print(f"Date Range              : 2025-01-01  to  2025-12-31")

print(f"\n--- Errors by Team ---")
print(df.group_by("Assignment Group").agg(pl.col("Number").count().alias("Errors")).sort("Errors", descending=True))

print(f"\n--- Errors by Process ---")
print(df.group_by("Process").agg(pl.col("Number").count().alias("Errors")).sort("Errors", descending=True))

print(f"\n--- Errors by System ---")
print(df.group_by("System").agg(pl.col("Number").count().alias("Errors")).sort("Errors", descending=True))

print(f"\n--- Errors by Priority ---")
print(df.group_by("Priority").agg(pl.col("Number").count().alias("Count")).sort("Count", descending=True))

print(f"\n--- Monthly Errors per Team ---")
print(
    df.with_columns(pl.col("Created").dt.month().alias("Month"))
    .group_by(["Month", "Assignment Group"])
    .agg(pl.col("Number").count().alias("Errors"))
    .sort(["Month", "Assignment Group"])
)

print(f"\nDataset saved to: {output_path}")
print(f"\n--- Preview (first 5 rows) ---")
print(df.head(5))

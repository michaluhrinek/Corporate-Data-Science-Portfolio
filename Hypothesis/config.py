"""
Configuration for Project 1 – Hypothesis Testing

Edit the values below to use real ECB data, synthetic data,
or your own CSV file.
"""

# ── DATA SOURCE ───────────────────────────────────────────────────────────────
USE_REAL_DATA = True
# True  → download EUR/USD rates from the ECB Data Portal
# False → generate synthetic exchange rate data

INPUT_FILE = None
# Path to your own CSV file. If set, this overrides both options above.
# Example: INPUT_FILE = "data/my_data.csv"

# ── DATA SCHEMA (only used when INPUT_FILE is set) ────────────────────────────
DATE_COLUMN = "date"
VALUE_COLUMN = "value"

# ── ANALYSIS PARAMETERS ───────────────────────────────────────────────────────
SPLIT_DATE = "2024-01-01"
# The boundary between "period A" and "period B"

ALPHA = 0.05
# Significance level. p-values below this are considered "statistically significant"

# ── FILE PATHS ────────────────────────────────────────────────────────────────
RAW_DATA_PATH = "data/raw_data.csv"
CLEAN_DATA_PATH = "data/clean_data.csv"
OUTPUT_DIR = "outputs"

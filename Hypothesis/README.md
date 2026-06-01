# Project 1 – Hypothesis Testing

**Question:** Did EUR/USD volatility change between two periods?

## What you'll learn

- How to fetch real economic data from the European Central Bank
- The two-sample t-test (compare averages between two groups)
- F-test for variance (compare volatility between two groups)
- How to interpret p-values and effect sizes
- Visualizing distributions for hypothesis testing

## What this project does

1. Downloads daily EUR/USD exchange rates from the ECB Data Portal
2. Splits the data into two periods (you choose where to split)
3. Tests whether the average rate is different between periods (t-test)
4. Tests whether the volatility is different between periods (F-test)
5. Produces a chart and a written report with the result

## How to run

```bash
pip install -r requirements.txt
python run_all.py
```

If the ECB download fails (no internet, API change), the project automatically falls back to synthetic data so you can still run the analysis.

## Using your own data

Edit `config.py`:

```python
USE_REAL_DATA = False           # use synthetic instead
INPUT_FILE = "data/my_data.csv" # OR put your own CSV here
DATE_COLUMN = "date"
VALUE_COLUMN = "value"
SPLIT_DATE = "2024-01-01"
```

Your CSV needs two columns: a date and a numeric value. That's it.

## Output

After running, check `outputs/`:
- `distribution_comparison.png` – visual comparison of the two periods
- `report.md` – written summary of the statistical test and what it means

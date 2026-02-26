#NLP Transformers  - analyze tickets based on short description by using pretrained model.
"""
NLP Incident Analyzer — Exact Phrase Counter
=================================================================
Run from terminal:
    python NLP_Test.py

Flow:
  1. Load ALL records with Polars (no deduplication, no limits)
  2. Show tokenization example (how the model sees text internally)
  3. Count every exact Short Description phrase across all tickets
  4. Report top N most repeated phrases with exact occurrence counts
     e.g.  "Failed login attempt"     : 15,000 times
           "PC not starting"          : 10,000 times
           "Cannot connect to VPN"    :  8,500 times

Requirements:
    pip install polars sentence-transformers torch
"""
# Import libraries
import os                              # for working with file paths and folders
import polars as pl                    # for loading and reading CSV files fast
from transformers import AutoTokenizer # for loading the pretrained NLP tokenizer
from collections import Counter        # for counting how many times each phrase appears

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # folder where this script lives
CSV_PATH   = r"C:\Users\User\Downloads\synthetic_data.csv" # path to the input CSV file
TOP_N      = 3                                          # how many top phrases to show

# LOAD ALL DATA
print("\n[1/3] Loading data with Polars...")
df           = pl.read_csv(CSV_PATH, n_rows=None)            # read every row from the CSV
descriptions = df["Short Description"].to_list()             # grab the Short Description column as a list
total        = len(descriptions)                             # count total number of tickets
print(f"  Total tickets loaded : {total:,}")                 # print how many tickets were loaded
print(f"  No deduplication — all {total:,} records counted") # confirm no rows were skipped

# LOAD TOKENIZER
print("\n[2/3] Loading tokenizer...")
tokenizer_hf = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2") # download pretrained tokenizer

# COUNT EXACT PHRASES
print("\n[3/3] Counting every exact Short Description phrase...")
phrase_counter = Counter(descriptions)             # count occurrences of each unique phrase
top_phrases    = phrase_counter.most_common(TOP_N) # get the TOP_N most repeated phrases
print(f"\n  Total unique phrases found : {len(phrase_counter):,}") # how many different phrases exist
print(f"  Counting across all {total:,} tickets\n")                # reminder of total ticket count
print(f"  TOP {TOP_N} MOST REPEATED SHORT DESCRIPTIONS")

summary_rows = [] # empty list to collect results for saving to CSV later

for rank, (phrase, count) in enumerate(top_phrases, 1): # loop through each top phrase
    pct = count / total * 100       # calculate what percentage of tickets have this phrase
    bar = "#" * int(pct)            # build a simple visual bar based on percentage
    print(f"\n  #{rank}")                                               # print rank number
    print(f"  Phrase  : {phrase}")                                     # print the phrase text
    print(f"  Count   : {count:,} times")                              # print how many times it appears
    print(f"  Share   : {pct:.1f}% of all {total:,} tickets  [{bar}]") # print percentage share
    summary_rows.append({"Rank": rank, "Phrase": phrase, "Count": count, "Pct": round(pct, 2)}) # save row for CSV

# FULL RANKING
print("\n" + "=" * 60)
print(f"  FULL RANKING — all {len(phrase_counter):,} unique phrases") # heading for full list
print("=" * 60)
print(f"  {'Rank':<6} {'Count':>8}   Phrase") # column headers
print(f"  {'-'*6} {'-'*8}   {'-'*40}")        # separator line

for i, (phrase, count) in enumerate(phrase_counter.most_common(), 1): # loop through all phrases ranked
    pct = count / total * 100                                           # calculate percentage for each
    print(f"  {i:<6} {count:>8,}   ({pct:.1f}%)  {phrase}")           # print rank, count, percent, phrase

# SAVE OUTPUTS
summary_df = pl.DataFrame(summary_rows)                                    # convert top results to a dataframe
summary_df.write_csv(os.path.join(SCRIPT_DIR, "top_phrases.csv"))          # save top phrases to CSV file

all_rows = [
    {"Rank": i, "Phrase": phrase, "Count": count, "Pct": round(count / total * 100, 2)}
    for i, (phrase, count) in enumerate(phrase_counter.most_common(), 1)   # build a row for every unique phrase
]
pl.DataFrame(all_rows).write_csv(os.path.join(SCRIPT_DIR, "all_phrases_ranked.csv")) # save full list to CSV file

print("  DONE")
print(f"  Top {TOP_N} summary     -> top_phrases.csv")       # confirm where top results were saved
print("  Full ranked list    -> all_phrases_ranked.csv")     # confirm where full list was saved


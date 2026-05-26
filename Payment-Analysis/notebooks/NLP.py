import sys
import os
import warnings
import logging
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
warnings.filterwarnings("ignore")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
logging.getLogger("transformers").setLevel(logging.ERROR)

import polars as pl
from transformers import AutoTokenizer

# ─── CONFIG ────────────────────────────────────────────────────────────────────
CSV_PATH = r"payments_errors_2025.csv"   
TOP_N    = 10   # how many top error reasons to show

# ─── LOAD DATA ─────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("   NLP ANALYZER — PAYMENTS ERROR SHORT DESCRIPTIONS")
print("=" * 60)

print("\n[1/3] Loading payments_errors_2025.csv ...")
df           = pl.read_csv(CSV_PATH, null_values=[""])
descriptions = df["Short Description"].drop_nulls().to_list()
total        = len(descriptions)
print(f"  Total error records loaded : {total:,}")

# ─── TOKENIZATION EXAMPLE ──────────────────────────────────────────────────────
print("\n[2/3] Tokenization example (how the model reads text)...")
print("  Model : sentence-transformers/all-MiniLM-L6-v2")

tokenizer  = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
sample     = descriptions[0]
tokens     = tokenizer.tokenize(sample)
token_ids  = tokenizer.encode(sample)

print(f"\n  Original  : {sample}")
print(f"  Tokens    : {tokens}")
print(f"  Token IDs : {token_ids}")

# ─── COUNT EXACT PHRASES ───────────────────────────────────────────────────────
print(f"\n[3/3] Counting most common error reasons ...")

counter     = Counter(descriptions)
top_phrases = counter.most_common(TOP_N)

print(f"\n  Total unique error phrases : {len(counter):,}")
print(f"  Counted across {total:,} total error records\n")

print("=" * 60)
print(f"  TOP {TOP_N} MOST COMMON ERROR REASONS")
print("=" * 60)

for rank, (phrase, count) in enumerate(top_phrases, 1):
    pct = count / total * 100
    bar = "#" * int(pct * 2)
    print(f"\n  #{rank}")
    print(f"  Reason  : {phrase}")
    print(f"  Count   : {count:,} times")
    print(f"  Share   : {pct:.1f}%  [{bar}]")

# ─── FULL RANKING ──────────────────────────────────────────────────────────────
print(f"\n{'=' * 60}")
print(f"  FULL RANKING — all {len(counter):,} unique error phrases")
print(f"{'=' * 60}")
print(f"  {'Rank':<6} {'Count':>7}   Phrase")
print(f"  {'-'*6} {'-'*7}   {'-'*45}")

for i, (phrase, count) in enumerate(counter.most_common(), 1):
    pct = count / total * 100
    print(f"  {i:<6} {count:>7,}   ({pct:.1f}%)  {phrase}")

# ─── SAVE OUTPUTS ──────────────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))

top_df = pl.DataFrame([
    {"Rank": i, "Phrase": p, "Count": c, "Pct": round(c / total * 100, 2)}
    for i, (p, c) in enumerate(top_phrases, 1)
])
top_df.write_csv(os.path.join(script_dir, "top_error_phrases.csv"))

full_df = pl.DataFrame([
    {"Rank": i, "Phrase": p, "Count": c, "Pct": round(c / total * 100, 2)}
    for i, (p, c) in enumerate(counter.most_common(), 1)
])
full_df.write_csv(os.path.join(script_dir, "all_error_phrases_ranked.csv"))

print(f"\n{'=' * 60}")
print(f"  DONE")
print(f"  Top {TOP_N} summary  -> top_error_phrases.csv")
print(f"  Full ranked list -> all_error_phrases_ranked.csv")
print(f"{'=' * 60}\n")

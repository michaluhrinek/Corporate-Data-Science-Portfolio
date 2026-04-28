#NLP Transformers  - analyze tickets based on short description by using pretrained model. 
"""
NLP Incident Analyzer — (Pure Transformer, No Training)
=================================================================
Flow:
  1. Load all data with Polars
  2. Tokenize descriptions
  3. Generate sentence embeddings via transformer (all-MiniLM-L6-v2)
  4. Compute cosine similarity between all embeddings  - how close are the meanings of different descriptions?
  5. Group semantically similar descriptions - descriptions with similarity above threshold are considered the same theme
  6. Report top 3 most common incident themes - count how many tickets fall into each theme group, and show example descriptions

Requirements:
    pip install polars sentence-transformers torch
"""
#import libraries and set up environment
import os  #for file paths and environment variables
import sys #for stdout encoding
import io #for stdout encoding
import warnings #to suppress warnings from transformers
import logging #to suppress logging from transformers and sentence-transformers

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace") # Ensure UTF-8 output in environments with encoding issues (e.g., Windows console)
warnings.filterwarnings("ignore")
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Disable parallelism in tokenizers to avoid warnings about too many parallel threads
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)  # Suppress info/warning logs from sentence-transformers library
logging.getLogger("transformers").setLevel(logging.ERROR) # Suppress info/warning logs from transformers library

import polars as pl
import numpy as np
from sentence_transformers import SentenceTransformer  #used for test preprocessing and embeddings
from collections import defaultdict   #count tickets occurrences per group for the final theme analysis

# CONFIG  #is to ensure the code works regardless of where it is executed. This method makes your script portable and avoids errors related to file paths.
# ------------------------------------------------------------------------------------
SCRIPT_DIR       = os.path.dirname(os.path.abspath(__file__)) # Get the directory of the current script
CSV_PATH         = os.path.join(SCRIPT_DIR, "synthetic_incident_bank_data_weighted.csv") # Path to the input CSV file (adjust if your file is located elsewhere)


#configuration 
SIMILARITY_THRESHOLD = 0.60   # 0.0 = nothing matches, 1.0 = identical
                               # 0.60 means "same meaning, different words"
                               # raise to 0.90+ for stricter grouping
TOP_N = 3                      # how many top themes to report, in your case 3


#LOAD ALL DATA
# ─────---------------------------------------------------------------------
print("\n" + "=" * 60)
print("  NLP INCIDENT ANALYZER — PURE TRANSFORMER, NO TRAINING")
print("=" * 60)

print("\n[1/5] Loading data with Polars...")
df = pl.read_csv(CSV_PATH)  #load data into dataframe using polars
descriptions: list[str] = df["Short Description"].to_list()  # Extract the "Short Description" column as a list of strings  
print(f"Total tickets loaded : {len(descriptions):,}")  #length of the descriptions list, which is the total number of tickets in the dataset

# Work on unique descriptions only — efficient, avoids re-processing duplicates
unique_desc: list[str] = list(dict.fromkeys(descriptions))  # preserves order, deduplicates
print(f"Unique descriptions  : {len(unique_desc):,}")  #filter the same descriptions and only keep unique ones, this is important because many tickets may have the same short description, and we only want to process each unique description once to save time and resources when generating embeddings and computing similarities.


#TOKENIZATION (happens inside the model automatically)
# -------------------------------------------------------------------------------
print("\n[2/5] Loading transformer model...")
print("Model : sentence-transformers/all-MiniLM-L6-v2")
print("→ Tokenization happens inside the model pipeline")
print("Each description is split into subword tokens,")
print("each token gets a numeric ID from the vocabulary.")
#tokenization  - splitting text into subword tokens. 
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Show tokenization for one example so you can see what it does-----------------------
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

sample = unique_desc[0]
tokens = tokenizer.tokenize(sample)
token_ids = tokenizer.encode(sample)

print(f"\n Example tokenization:")
print(f"Original: {sample}")
print(f"Tokens: {tokens}")
print(f"Token IDs: {token_ids}")


# GENERATE EMBEDDINGS FOR ALL UNIQUE DESCRIPTIONS
# ---------------------------------------------------------------------------------
print(f"\n[3/5] Generating embeddings for {len(unique_desc):,} unique descriptions...")
print("Each description → 384-number meaning vector")
print("Running transformer inference (no training, model is frozen)...")

embeddings: np.ndarray = model.encode(      #Each ticket description is converted into a dense numerical vector (e.g., 384 features per embedding)
    unique_desc,
    batch_size=64,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=True   # Normalizes every embedding vector to a unit length (norm = 1).
)

print(f"\n Embedding matrix shape : {embeddings.shape}")
print(f"→ {embeddings.shape[0]} descriptions × {embeddings.shape[1]} features")

# COSINE SIMILARITY GROUPING
# Group descriptions whose meaning vectors are close together
#----------------------------------------------------------------------------------------
print(f"\n[4/5] Grouping semantically similar descriptions...")
print(f"Similarity threshold : {SIMILARITY_THRESHOLD}")
print(f"(descriptions above this score are considered the same theme)")

# Because embeddings are normalized, dot product = cosine similarity
# similarity matrix shape: (n_unique, n_unique)
similarity_matrix: np.ndarray = np.dot(embeddings, embeddings.T)

# Greedy grouping:
# - Pick the first unassigned description as a "group leader"
# - Assign all descriptions similar to it into that group
# - Move to the next unassigned description

assigned = [False] * len(unique_desc)
groups: dict[int, list[str]] = {}   # group_leader_index → list of similar descriptions

for i in range(len(unique_desc)):
    if assigned[i]:
        continue
    # Start a new group with description i as leader
    groups[i] = [unique_desc[i]]
    assigned[i] = True
    # Find all unassigned descriptions similar enough to join this group
    for j in range(i + 1, len(unique_desc)):
        if not assigned[j] and similarity_matrix[i][j] >= SIMILARITY_THRESHOLD:
            groups[i].append(unique_desc[j])
            assigned[j] = True

print(f"Unique semantic groups found : {len(groups)}")


#COUNT TICKETS PER GROUP AND REPORT TOP 3
#------------------------------------------------------------------------------------
print(f"\n[5/5] Counting tickets per semantic group...")

# Count how many tickets from the FULL dataset fall into each group
# A ticket belongs to the group whose leader it matched
desc_to_group: dict[str, int] = {}
for leader_idx, members in groups.items():
    for member in members:
        desc_to_group[member] = leader_idx

# Count all tickets (not just unique) per group
group_ticket_counts: dict[int, int] = defaultdict(int)
for desc in descriptions:
    group_idx = desc_to_group.get(desc, -1)
    group_ticket_counts[group_idx] += 1

# Sort groups by ticket count descending
top_groups = sorted(group_ticket_counts.items(), key=lambda x: -x[1])[:TOP_N]
total = len(descriptions)

print(f"\n{'=' * 60}")
print(f"  TOP {TOP_N} INCIDENT THEMES  (pure transformer, no training)")
print(f"{'=' * 60}")

summary_rows = []
for rank, (group_idx, count) in enumerate(top_groups, 1):
    pct = count / total * 100
    members = groups.get(group_idx, [])
    leader_desc = unique_desc[group_idx]

    # Find the centroid description — most similar to the group average
    if len(members) > 1:
        member_indices = [unique_desc.index(m) for m in members]
        member_embeddings = embeddings[member_indices]
        centroid = member_embeddings.mean(axis=0)
        centroid /= np.linalg.norm(centroid)
        similarities_to_centroid = member_embeddings @ centroid
        best_idx = member_indices[np.argmax(similarities_to_centroid)]
        theme_headline = unique_desc[best_idx]
    else:
        theme_headline = leader_desc

    print(f"\n  #{rank}  THEME: {theme_headline}")
    print(f" Tickets in group: {count:,} ({pct:.1f}% of all tickets)")
    print(f" Descriptions in: {len(members)} unique variants")
    print(f" All variants:")
    for m in members[:5]:   # show up to 5
        sim = similarity_matrix[group_idx][unique_desc.index(m)]
        print(f" [{sim:.3f}] {m}")

    summary_rows.append({
        "Rank": rank,
        "Theme": theme_headline,
        "Ticket_Count": count,
        "Percentage": round(pct, 2),
        "Unique_Variants": len(members),
        "Variant_1": members[0] if len(members) > 0 else "",
        "Variant_2": members[1] if len(members) > 1 else "",
        "Variant_3": members[2] if len(members) > 2 else "",
    })


# SAVE OUTPUTS
# ---------------------------------------------------------------------------------------
summary_df = pl.DataFrame(summary_rows)
out_path = os.path.join(SCRIPT_DIR, "top3_themes_option1.csv")
summary_df.write_csv(out_path)

# Full dataset with group label appended
group_labels = [
    unique_desc[desc_to_group[d]] if d in desc_to_group else "Unassigned"
    for d in descriptions
]
df_out = df.with_columns(pl.Series("Semantic_Theme", group_labels))
full_out = os.path.join(SCRIPT_DIR, "incidents_option1_themes.csv")
df_out.write_csv(full_out)

print(f"\n{'=' * 60}")
print(f"  DONE")
print(f"  Top 3 summary  → top3_themes_option1.csv")
print(f"  Full dataset   → incidents_option1_themes.csv")

print(f"{'=' * 60}\n")
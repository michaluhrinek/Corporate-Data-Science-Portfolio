# classification of the tickets based on the type of payment, process, system, priority, urgency, impact and state#i
#import libraries and set up environment
import sys
import os
import warnings
sys.stdout.reconfigure(encoding='utf-8')
warnings.filterwarnings("ignore")

import polars as pl
import numpy as np
from sklearn.ensemble         import RandomForestClassifier
from sklearn.linear_model     import LogisticRegression
from sklearn.model_selection  import train_test_split
from sklearn.preprocessing    import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics          import classification_report, accuracy_score
from scipy.sparse             import hstack, csr_matrix
import joblib

# ─── LOAD DATA ─────────────────────────────────────────────────────────────────
CSV_PATH = r"payments_errors_2025.csv"   
print("\n[1/5] Loading payments_errors_2025.csv ...")
df = pl.read_csv(CSV_PATH, null_values=[""]).drop_nulls(subset=["Short Description", "Process"])

print(f"  Records loaded : {df.shape[0]:,}")
print(f"  Features used  : Short Description, System, Priority, Urgency, Impact, State")
print(f"  Target         : Process (what type of payment error is this?)")

# ─── FEATURE ENGINEERING ─-------------------------------------------------------------
print("\n[2/5] Preparing features ...")

# Target
le_target = LabelEncoder()
y       = le_target.fit_transform(df["Process"].to_list())
classes = le_target.classes_
print(f"  Target classes : {list(classes)}")

# Text feature — Short Description via TF-IDF
texts  = df["Short Description"].to_list()
tfidf  = TfidfVectorizer(ngram_range=(1, 2), max_features=300)
X_text = tfidf.fit_transform(texts)

# Categorical features — System, Priority, Urgency, Impact, State
cat_cols  = ["System", "Priority", "Urgency", "Impact", "State"]
encoders  = {}
cat_parts = []

for col in cat_cols:
    le      = LabelEncoder()
    encoded = le.fit_transform(df[col].to_list())
    encoders[col] = le
    cat_parts.append(csr_matrix(encoded.reshape(-1, 1)))

X_cat = hstack(cat_parts)
X     = hstack([X_text, X_cat])

print(f"  TF-IDF features   : {X_text.shape[1]}")
print(f"  Categorical cols  : {len(cat_cols)}")
print(f"  Total features    : {X.shape[1]}")

# ─── TRAIN / TEST SPLIT ────────────────────────────────────────────────────────
print("\n[3/5] Splitting data (80% train / 20% test) ...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
print(f"  Train samples : {X_train.shape[0]:,}")
print(f"  Test  samples : {X_test.shape[0]:,}")

# ─── TRAIN MODELS ──────────────────────────────────────────────────────────────
print("\n[4/5] Training models ...")

models = {
    "Random Forest":       RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
    "Logistic Regression": LogisticRegression(max_iter=500, random_state=42),
}

results = {}
for name, model in models.items():
    print(f"\n  Training {name} ...")
    model.fit(X_train, y_train)
    y_pred   = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    results[name] = {"model": model, "accuracy": accuracy, "y_pred": y_pred}
    print(f"  Accuracy : {accuracy * 100:.2f}%")

# ─── RESULTS ───────────────────────────────────────────────────────────────────
print("\n[5/5] Classification Results ...")

best_name  = max(results, key=lambda k: results[k]["accuracy"])
best_model = results[best_name]["model"]
best_pred  = results[best_name]["y_pred"]

print(f"\n{'=' * 65}")
print(f"  BEST MODEL : {best_name}  ({results[best_name]['accuracy']*100:.2f}% accuracy)")
print(f"{'=' * 65}")

print(f"\n--- Classification Report (per Process type) ---")
print(classification_report(y_test, best_pred, target_names=classes, zero_division=0))

print(f"--- Model Comparison ---")
for name, res in sorted(results.items(), key=lambda x: x[1]["accuracy"], reverse=True):
    bar = "#" * int(res["accuracy"] * 50)
    print(f"  {name:<22} : {res['accuracy']*100:.2f}%  [{bar}]")

# ─── FEATURE IMPORTANCE (Random Forest) ────────────────────────────────────────
if "Random Forest" in results:
    rf          = results["Random Forest"]["model"]
    importances = rf.feature_importances_
    all_names   = list(tfidf.get_feature_names_out()) + cat_cols
    top_idx     = np.argsort(importances)[::-1][:15]

    print(f"\n--- Top 15 Most Predictive Features (Random Forest) ---")
    print(f"  {'Feature':<45} Importance")
    print(f"  {'-'*45} ----------")
    for i in top_idx:
        fname = all_names[i] if i < len(all_names) else f"feature_{i}"
        print(f"  {fname:<45} {importances[i]:.4f}")

# ─── SAVE MODEL ────────────────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "ticket_classifier.pkl")

joblib.dump({
    "model":     best_model,
    "tfidf":     tfidf,
    "encoders":  encoders,
    "le_target": le_target,
    "cat_cols":  cat_cols,
}, model_path)
print(f"\n  Model saved -> ticket_classifier.pkl")

# ─── PREDICTION DEMO ───────────────────────────────────────────────────────────
print(f"\n{'=' * 65}")
print(f"  PREDICTION DEMO — classify a new ticket")
print(f"{'=' * 65}")

demo_tickets = [
    {
        "Short Description": "Wrong IBAN entered in bulk SEPA file - batch partially rejected",
        "System": "Stargate", "Priority": "High", "Urgency": "High", "Impact": "High", "State": "Closed"
    },
    {
        "Short Description": "Wrong sort code entered - domestic payment routed to wrong bank",
        "System": "STP CAT", "Priority": "Medium", "Urgency": "Medium", "Impact": "Medium", "State": "Closed"
    },
    {
        "Short Description": "Wrong FX rate applied to customer transaction - financial loss",
        "System": "SOLEMOS", "Priority": "Critical", "Urgency": "High", "Impact": "High", "State": "In Progress"
    },
]

for i, ticket in enumerate(demo_tickets, 1):
    x_text     = tfidf.transform([ticket["Short Description"]])
    x_cat      = hstack([csr_matrix([[encoders[col].transform([ticket[col]])[0]]]) for col in cat_cols])
    x_combined = hstack([x_text, x_cat])
    pred_idx   = best_model.predict(x_combined)[0]
    pred_label = le_target.inverse_transform([pred_idx])[0]
    confidence = best_model.predict_proba(x_combined)[0][pred_idx] * 100

    print(f"\n  Ticket #{i}")
    print(f"  Input      : {ticket['Short Description'][:65]}")
    print(f"  System     : {ticket['System']}  |  Priority: {ticket['Priority']}")
    print(f"  Predicted  : {pred_label}")
    print(f"  Confidence : {confidence:.1f}%")

print(f"\n{'=' * 65}")
print(f"  DONE — run: python ML_ticket_classification.py")
print(f"{'=' * 65}\n")
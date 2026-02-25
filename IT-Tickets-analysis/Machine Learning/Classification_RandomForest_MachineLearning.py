#Classification using Random Forest Classifier

# Import required libraries
import polars as pl
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# Load data
df = pl.read_csv("synthetic_incident_bank_data_weighted.csv")
datetime_columns = ["Closed", "Start Date"]

# Parse datetime columns
for col in datetime_columns: 
    if col in df.columns:
        df = df.with_columns(
            pl.col(col).str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S.%f", strict=False).alias(col)
        )
        
# Calculate Resolution Time
df = df.with_columns(
    (df["Closed"] - df["Start Date"]).dt.total_hours().alias("Resolution Time")
)

# Drop rows with missing "Resolution Time"
df = df.filter(pl.col("Resolution Time").is_not_null())

# Encode categorical columns (which columns we will use for prediction)
categorical_columns = ["Change Environment", "Assignment Group", "Priority", "Urgency", "Impact"]
mappings = {}  # Store mappings for reverse use during prediction and decoding
for col in categorical_columns:
    unique_values = sorted(df.get_column(col).unique().to_list())  # Ensure sorted order
    mapping = {value: idx for idx, value in enumerate(unique_values)}  # Map values to integer encoding
    mappings[col] = mapping  # Save the mapping
    reverse_mapping = {idx: value for value, idx in mapping.items()}  # Reverse mapping for decoding
    mappings[f"{col}_reverse"] = reverse_mapping  # Save reverse mapping
    df = df.with_columns(pl.col(col).replace(mapping).alias(f"{col}_encoded"))


# Prepare Features and Target for Priority Prediction
X = df.select(
    ["Resolution Time", "Breach Count", "Reopen Count", "Change Environment_encoded", 
     "Assignment Group_encoded", "Urgency_encoded", "Impact_encoded"]
).to_numpy()

y_priority = df.select("Priority_encoded").to_numpy().flatten()  # Multi-class target

# Split data for training and testing
X_train, X_test, y_train, y_test = train_test_split(X, y_priority, test_size=0.2, random_state=42)

# ----------------------------- RANDOM FOREST CLASSIFIER -----------------------------------------
rf_clf = RandomForestClassifier(n_estimators=100, random_state=42) #we input 100 decision trees in our model, 100 is a standard, because having more would cost us time for compuutation and money, but for basic models and good accuracy, 100 is enough
rf_clf.fit(X_train, y_train)

# Make predictions
y_pred_rf = rf_clf.predict(X_test)

# Evaluate Random Forest performance
print("\nRandom Forest - Priority Prediction")
print(f"Accuracy: {accuracy_score(y_test, y_pred_rf):.2f}")
print("Classification Report:")
print(classification_report(y_test, y_pred_rf))

# ----------------------------- Prediction for New Data -----------------------------------------
# Example Input: New Ticket Details
resolution_time = 2  #  hours processing time
reopen_count = 1
urgency = "Low"
assignment_group = "Avengers"
impact = "Medium"

# Get mappings for categorical features
urgency_mapping = mappings["Urgency"]
assignment_group_mapping = mappings["Assignment Group"]
impact_mapping = mappings["Impact"]
priority_reverse_mapping = mappings["Priority_reverse"]  # Reverse mapping for decoding predictions

# Convert user input into encoded features
urgency_encoded = urgency_mapping.get(urgency, -1)  # Use -1 for unknown values
assignment_group_encoded = assignment_group_mapping.get(assignment_group, -1)
impact_encoded = impact_mapping.get(impact, -1)

# Define features for prediction
new_ticket_features = [resolution_time, 0, reopen_count, 0, assignment_group_encoded, urgency_encoded, impact_encoded]

# Ensure 2D shape for prediction
new_ticket_features = [new_ticket_features]

# Predict priority for the new ticket
predicted_priority = rf_clf.predict(new_ticket_features)[0]

# Decode predicted priority back to the original label
predicted_priority_label = priority_reverse_mapping.get(int(predicted_priority), "Unknown")

# Debugging: Print additional debugging information
print(f"Encoded Predicted Priority: {predicted_priority} (Type: {type(predicted_priority)})")
print(f"Reverse Mapping: {priority_reverse_mapping} (Keys Type: {[type(k) for k in priority_reverse_mapping.keys()]})")

# Output the result
print("\nPrediction for New Ticket - Priority:")
print(f"Resolution Time: {resolution_time} hours, Urgency: {urgency}, Reopen Count: {reopen_count}, Assignment Group: {assignment_group}, Impact: {impact}")
print(f"Predicted Priority: {predicted_priority_label}")
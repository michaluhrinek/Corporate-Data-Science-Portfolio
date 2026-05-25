# Machine Learning Regression Model for Incident Resolution Time Prediction

import polars as pl
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# -------------------------------------------
# Load the dataset
# -------------------------------------------
df = pl.read_csv("synthetic_incident_bank_data_weighted.csv")
print("\nDataset loaded successfully!")

# -------------------------------------------
# Cleaning and Preprocessing
# -------------------------------------------

# 1) Parse datetime columns
datetime_columns = ["Closed", "Start Date"]
for col in datetime_columns:
    if col in df.columns:
        df = df.with_columns(
            pl.col(col).str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S.%f", strict=False).alias(col)
        )

print("\nParsed `Closed` and `Start Date` columns:")
print(df.select(["Closed", "Start Date"]).head(10))

# 2) Calculate Resolution Time (in hours)
df = df.with_columns(
    ((pl.col("Closed") - pl.col("Start Date")).dt.total_hours()).alias("Resolution Time")
)

print("\nVerified `Resolution Time` column:")
print(df.select(["Closed", "Start Date", "Resolution Time"]).head(10))

# 3) Encode categorical columns on the FULL df
categorical_columns = ["Change Environment", "Assignment Group", "Priority", "Urgency", "Impact"]

# store mappings so we can reuse them for prediction
mappings = {}

for col in categorical_columns:
    unique_values = df.get_column(col).unique().to_list()
    mapping = {value: idx for idx, value in enumerate(unique_values)}
    mappings[col] = mapping  # keep mapping for later use (prediction)

    df = df.with_columns(
        pl.col(col).replace(mapping).alias(col + "_encoded")
    )

print("\nVerified categorical column encodings:")
print(df.select([col + "_encoded" for col in categorical_columns]).head(10))

# 4) Drop rows with missing Resolution Time AFTER encoding
df_cleaned = df.filter(pl.col("Resolution Time").is_not_null())

# -------------------------------------------
# Define Features (X) and Target (y)
# -------------------------------------------

feature_cols = [
    "Breach Count",
    "Reopen Count",
    "Change Environment_encoded",
    "Assignment Group_encoded",
    "Priority_encoded",
    "Urgency_encoded",
    "Impact_encoded"
]

X = df_cleaned.select(feature_cols).to_numpy()
y = df_cleaned.select(["Resolution Time"]).to_numpy().flatten()

print(f"\nFeature matrix shape (X): {X.shape}")
print(f"Target vector shape (y): {y.shape}")

# -------------------------------------------
# Train / Test Split
# -------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("\nTraining and Testing Splits:")
print(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
print(f"X_test shape: {X_test.shape}, y_test shape: {y_test.shape}")

# -------------------------------------------
# Train Model
# -------------------------------------------
regressor = RandomForestRegressor(n_estimators=100, random_state=42)
regressor.fit(X_train, y_train)

# -------------------------------------------
# Evaluate Model
# -------------------------------------------
y_pred = regressor.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("\nModel Evaluation Metrics:")
print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"Mean Squared Error (MSE): {mse:.2f}")

print("\nPredicted vs Actual Values (Sample Comparison):")
for i in range(10):
    print(f"Predicted: {y_pred[i]:.2f}, Actual: {y_test[i]:.2f}")


# -------------------------------------------

# Example Input: New Ticket Details
priority = "Low"
urgency = "Medium"
reopen_count = 0
assignment_group = "Avengers"
change_environment = "Network"   # example
impact = "Medium"                # example
breach_count = 0                 # example

# Use the SAME mappings we used during training
priority_encoded = mappings["Priority"].get(priority, -1)
urgency_encoded = mappings["Urgency"].get(urgency, -1)
assignment_group_encoded = mappings["Assignment Group"].get(assignment_group, -1)
change_environment_encoded = mappings["Change Environment"].get(change_environment, -1)
impact_encoded = mappings["Impact"].get(impact, -1)

# Build feature vector in the SAME ORDER as feature_cols
new_ticket_features = [
    breach_count,               # "Breach Count"
    reopen_count,               # "Reopen Count"
    change_environment_encoded, # "Change Environment_encoded"
    assignment_group_encoded,   # "Assignment Group_encoded"
    priority_encoded,           # "Priority_encoded"
    urgency_encoded,            # "Urgency_encoded"
    impact_encoded              # "Impact_encoded"
]

# Model expects 2D array
new_ticket_features = [new_ticket_features]

predicted_time = regressor.predict(new_ticket_features)[0]

print("\nPrediction for New Ticket:")
print(
    f"Priority: {priority}, Urgency: {urgency}, Reopen Count: {reopen_count}, "
    f"Assignment Group: {assignment_group}, Change Environment: {change_environment}, Impact: {impact}"
)
print(f"Predicted resolution time: {predicted_time:.2f} hours")

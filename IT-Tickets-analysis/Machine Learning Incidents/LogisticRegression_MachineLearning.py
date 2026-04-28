#Logistic Regression Model for Incident Resolution Time Prediction
#import libraries
import polars as pl
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

#load data 
df = pl.read_csv("synthetic_incident_bank_data_weighted.csv")
datetime_columns = ["Closed", "Start Date"]
for col in datetime_columns: 
    if col in df.columns:
        df = df.with_columns(
            pl.col(col).str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S.%f", strict=False).alias(col)
        )
#calculate "Resolution Time"
df = df.with_columns(
    ((df["Closed"] - df["Start Date"]).dt.total_hours()).alias("Resolution Time")
)   
#Encode categorical columns
categorical_columns = ["Change Environment", "Assignment Group", "Priority", "Urgency", "Impact"]
for col in categorical_columns:
    unique_values = df.get_column(col).unique().to_list()
    mapping = {value: idx for idx, value in enumerate(unique_values)}
    df = df.with_columns(
        pl.col(col).replace(mapping).alias(col + "_encoded")   # here we are creating values like Priority_encoded, Urgency_encoded, etc. which are numeric representations of the original categorical columns 
    )
    
#Drop rows with missing `Resolution Time`
df = df.filter(pl.col("Resolution Time").is_not_null())

#Define the target  - SLA Breached Prediction (1 if breached, 0 if not)
SLA_TRESHOLD = 24 #hours 
df = df.with_columns(
    (pl.col("Resolution Time") > SLA_TRESHOLD).cast(pl.Int64).alias("SLA_Breached")
)
#priority column is already encoded as priority_encoded, we can use it as target for priority prediction
#Prepare features and target for SLA Breached Prediction
X = df.select(
    ["Breach Count", "Reopen Count", "Change Environment_encoded", "Assignment Group_encoded",
     "Urgency_encoded", "Impact_encoded"]).to_numpy()

y_breach = df.select("SLA_Breached").to_numpy().flatten()  #binary target for SLA breach prediction
y_priority = df.select("Priority_encoded").to_numpy().flatten() #multi-class target

#.flatten() is a NumPy method that converts a multi-dimensional array into a 1D array (single, linear array).
#This is needed for cases where algorithms or functions require data in a flat, 1D format rather than 2D.
'''Original Array: #example of a 2D array with shape (4, 1)
[[1]
 [0]
 [1]
 [1]]
Shape: (4, 1)
 # example of the same data after flattening, resulting in a 1D array with shape (4,)
Flattened Array:
[1 0 1 1]
Shape: (4,)
'''

# Split Data for SLA Breach Prediction -------------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y_breach, test_size=0.2, random_state=42)

# Logistic Regression Model
log_reg = LogisticRegression(random_state=42)
log_reg.fit(X_train, y_train)
y_pred_lr = log_reg.predict(X_test)

# Evaluation
print("\nLogistic Regression - SLA Breach Prediction")
print(f"Accuracy: {accuracy_score(y_test, y_pred_lr):.2f}")
print(classification_report(y_test, y_pred_lr))

#--------------------------Prediction part with new data ---------------------------------------------------------------------------------------
# Example Input: New Ticket Details
priority = "Medium"
urgency = "Low"
reopen_count = 6
assignment_group = "Avengers"

# Mapping Categorical Features (Same as used during preprocessing)
priority_mapping = {value: idx for idx, value in enumerate(df.get_column("Priority").unique().to_list())}
urgency_mapping = {value: idx for idx, value in enumerate(df.get_column("Urgency").unique().to_list())}
assignment_group_mapping = {value: idx for idx, value in enumerate(df.get_column("Assignment Group").unique().to_list())}

# Convert User Input into Numeric Values
priority_encoded = priority_mapping.get(priority, -1)  # Use -1 for unknown/invalid values
urgency_encoded = urgency_mapping.get(urgency, -1)
assignment_group_encoded = assignment_group_mapping.get(assignment_group, -1)

# Define Features for Prediction
# Here, we use the same feature setup used during training: ["Breach Count", "Reopen Count", "Change Environment_encoded", "Assignment Group_encoded", "Urgency_encoded", "Impact_encoded"]
new_ticket_features = [0, reopen_count, 0, assignment_group_encoded, urgency_encoded, 0]  # Change other values accordingly

# Reshape Features for Prediction
# Logistic Regression expects 2D input (batch of samples); reshape the single sample as required
new_ticket_features = [new_ticket_features]  # Place the feature list inside another list to ensure 2D input

# Predict SLA Breach Status
predicted_breach = log_reg.predict(new_ticket_features)[0]  # Predict and extract the single value

# Print the Result
breach_status = "Yes" if predicted_breach == 1 else "No"
print("\nPrediction for New Ticket - SLA Breach Status:")
print(f"Priority: {priority}, Urgency: {urgency}, Reopen Count: {reopen_count}, Assignment Group: {assignment_group}")
print(f"Predicted SLA Breach: {breach_status}")
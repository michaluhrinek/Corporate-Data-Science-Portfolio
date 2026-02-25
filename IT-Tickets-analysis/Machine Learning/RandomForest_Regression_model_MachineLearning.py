#Machine Learning Regression Model for Incident Resolution Time Prediction
#import libraries 
import polars as pl
from sklearn.model_selection import train_test_split #train test split import 
from sklearn.ensemble import RandomForestRegressor #import model 
from sklearn.metrics import mean_absolute_error, mean_squared_error #import evaluation metrics
# Load the dataset
df = pl.read_csv("synthetic_incident_bank_data_weighted.csv")
print("\nDataset loaded successfully!")


#Cleaning and Preprocessing
#Parse datetime columns 
datetime_columns = ["Closed", "Start Date"]
for col in datetime_columns:
    if col in df.columns:
        df = df.with_columns(
            pl.col(col).str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S.%f", strict=False).alias(col)
        )

# Verify parsed datetime columns
print("\nParsed `Closed` and `Start Date` columns:")
print(df.select(["Closed", "Start Date"]).head(10))


#Calculate `Resolution Time
df = df.with_columns(
    ((df["Closed"] - df["Start Date"]).dt.total_hours()).alias("Resolution Time")
)

print("\nVerified `Resolution Time` column:")
print(df.select(["Closed", "Start Date", "Resolution Time"]).head(10))

#Drop rows with missing `Resolution Time` 
df_cleaned = df.filter(pl.col("Resolution Time").is_not_null())

# Encode categorical columns ---------------------------------------------------------------------------
categorical_columns = ["Change Environment", "Assignment Group", "Priority", "Urgency", "Impact"]

# Encode categorical columns using replacements
for col in categorical_columns:
    unique_values = df.get_column(col).unique().to_list()
    mapping = {value: idx for idx, value in enumerate(unique_values)}

    # Replace categories with numeric codes
    df = df.with_columns(
        pl.col(col).replace(mapping).alias(col + "_encoded")  # Add encoded column
    )

print("\nVerified categorical column encodings:")
print(df.select([col + "_encoded" for col in categorical_columns]).head(10))


#Define Features (`X`) and Target (`y`)-----------------------------------------------------------------
X = df_cleaned.select(
    ["Breach Count", "Reopen Count", "Change Environment_encoded", "Assignment Group_encoded", "Priority_encoded", "Urgency_encoded", "Impact_encoded"]
).to_numpy()

y = df_cleaned.select(["Resolution Time"]).to_numpy().flatten()

print(f"\nFeature matrix shape (X): {X.shape}")
print(f"Target vector shape (y): {y.shape}")


#Split Data Into Training and Testing Sets----------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)  #test is 20%, training is 80% and random_state is set for reproducibility is default on 42 
print("\nTraining and Testing Splits:")
print(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
print(f"X_test shape: {X_test.shape}, y_test shape: {y_test.shape}")

# Initialize the Random Forest regressor----------------------------------------------------------------
regressor = RandomForestRegressor(n_estimators=100, random_state=42)  #n_estimators is the number of trees in the forest, and random_state is set for reproducibility

# Train the regressor
regressor.fit(X_train, y_train)

# Make predictions
y_pred = regressor.predict(X_test)

# Evaluate model performance
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("\nModel Evaluation Metrics:")
print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"Mean Squared Error (MSE): {mse:.2f}")

# Predicted vs Actual Values
print("\nPredicted vs Actual Values (Sample Comparison):")
for i in range(10):
    print(f"Predicted: {y_pred[i]:.2f}, Actual: {y_test[i]:.2f}")
#-------------------------------------------------------------Prediction Part with our data input--------------------------------------------------------
### Step 5: Predict Resolution Time for a New Ticket ###

# Example Input: New Ticket Details
priority = "Low"
urgency = "Medium"
reopen_count = 0
assignment_group = "Avengers"

# Mapping Categorical Features (Same as used during preprocessing)
priority_mapping = {value: idx for idx, value in enumerate(df.get_column("Priority").unique().to_list())}
urgency_mapping = {value: idx for idx, value in enumerate(df.get_column("Urgency").unique().to_list())}
assignment_group_mapping = {value: idx for idx, value in enumerate(df.get_column("Assignment Group").unique().to_list())}

#Convert User Input into Numeric Values
priority_encoded = priority_mapping.get(priority, -1)  # Use -1 for unknown values
urgency_encoded = urgency_mapping.get(urgency, -1)
assignment_group_encoded = assignment_group_mapping.get(assignment_group, -1)

# Define Features for Prediction
new_ticket_features = [0, reopen_count, 0, assignment_group_encoded, priority_encoded, urgency_encoded, 0]

# Reshape Features for Prediction
new_ticket_features = [new_ticket_features]  # Add outer list for 2D input shape

# Predict Resolution Time
predicted_time = regressor.predict(new_ticket_features)[0]  # Predict and extract the single value

# Print the Result
print("\nPrediction for New Ticket:")
print(f"Priority: {priority}, Urgency: {urgency}, Reopen Count: {reopen_count}, Assignment Group: {assignment_group}")
print(f"Predicted resolution time: {predicted_time:.2f} hours")
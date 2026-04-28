#linear regression for resolution time prediction
# Import required libraries

import polars as pl
from sklearn.model_selection import train_test_split    #function to split the dataset into training and testing sets
from sklearn.linear_model import LinearRegression  #linear regression model for regression problems
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score #evaluation metrics for regression

#loading data 
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

# Drop rows with missing values in "Resolution Time"
df = df.filter(pl.col("Resolution Time").is_not_null())

# Encode all categorical columns into numerical representations--------------------------------------------------
categorical_columns = ["Change Environment", "Assignment Group", "Priority", "Urgency", "Impact"]
for col in categorical_columns:
    unique_values = sorted(df.get_column(col).unique().to_list())  # Ensure consistent sorted order
    mapping = {value: idx for idx, value in enumerate(unique_values)}  # Numeric encoding
    df = df.with_columns(pl.col(col).replace(mapping).alias(f"{col}_encoded"))  # Add encoded columns

# Select features (X) and target (y)-----------------------------------------------------------------------------
X = df.select([
    "Breach Count", "Reopen Count", "Change Environment_encoded", 
    "Assignment Group_encoded", "Priority_encoded", "Urgency_encoded", "Impact_encoded"
]).to_numpy()  # Convert to NumPy array

y = df.select("Resolution Time").to_numpy().flatten()  # Target variable (continuous numeric)

# Split data into training and testing sets----------------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Training data: X_train = {X_train.shape}, y_train = {y_train.shape}")
print(f"Testing data: X_test = {X_test.shape}, y_test = {y_test.shape}")

# Train Linear Regression model-------------------------------------------------------------------------------
lr_model = LinearRegression()  #call the model 
lr_model.fit(X_train, y_train) #fit the model with data 

#print coefficients and intercept
print("\model Coeficients:")
for idx, col in enumerate(["Breach Count", "Reopen Count", "Change Environment_encoded", 
    "Assignment Group_encoded", "Priority_encoded", "Urgency_encoded", "Impact_encoded"]):
    print(f"{col}: {lr_model.coef_[idx]:.4f}")
print(f"Intercept: {lr_model.intercept_:.4f}")

#Evaluate model performance
# Predict on the test set
y_pred = lr_model.predict(X_test)

# Calculate evaluation metrics
mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\nModel Evaluation Metrics:")
print(f"Mean Squared Error (MSE): {mse:.2f}")
print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"R² Score: {r2:.2f}")

#make a prediction based on my new input data 
# Example Input: New Ticket Features
new_ticket_features = [
    2,         # Breach Count
    1,         # Reopen Count
    0,         # Change Environment_encoded
    1,         # Assignment Group_encoded
    2,         # Priority_encoded (Assume Example Priority)
    1,         # Urgency_encoded
    1          # Impact_encoded
]

# Ensure the input is a 2D array (as required by sklearn)
new_ticket_features = [new_ticket_features]

# Predict resolution time for the new ticket
predicted_processing_time = lr_model.predict(new_ticket_features)[0]

print("\nPrediction for New Ticket:")
print(f"Predicted Processing Time: {predicted_processing_time:.2f} hours")
#Decision Tree model for prediction of Processing Time (Regression) 
#import libraries 
import polars as pl #for working with files 
from sklearn.model_selection import train_test_split  #train test split import 
from sklearn.tree import DecisionTreeRegressor  #model import 
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score  #evaluation metrics import

# Load the dataset
df = pl.read_csv("synthetic_incident_bank_data_weighted.csv")

# Parse datetime columns
datetime_columns = ["Closed", "Start Date"]
for col in datetime_columns:
    if col in df.columns:
        df = df.with_columns(
            pl.col(col).str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S%.f", strict=False).alias(col)
        )

# Calculate the target column: "Resolution Time"
df = df.with_columns(
    (df["Closed"] - df["Start Date"]).dt.total_hours().alias("Resolution Time")
)

# Drop rows with missing values in "Resolution Time"
df = df.filter(pl.col("Resolution Time").is_not_null())

# Encode categorical columns------------------------------------------------------------------------
categorical_columns = ["Change Environment", "Assignment Group", "Priority", "Urgency", "Impact"]
for col in categorical_columns:
    unique_values = sorted(df.get_column(col).unique().to_list())  # Ensure sorted order
    mapping = {value: idx for idx, value in enumerate(unique_values)}  # Numeric encoding
    df = df.with_columns(pl.col(col).replace(mapping).alias(f"{col}_encoded"))  # Add encoded columns


# Define features (X) and target variable (y)------------------------------------------------
X = df.select([
    "Breach Count", "Reopen Count", "Change Environment_encoded", 
    "Assignment Group_encoded", "Priority_encoded", "Urgency_encoded", "Impact_encoded"
]).to_numpy()

y = df.select("Resolution Time").to_numpy().flatten()  # Continuous target variable


# Split data into training and testing sets---------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the Decision Tree Regressor Model ----------------------------------------------
dt_model = DecisionTreeRegressor(random_state=42)  #42 is default for number leafs in the tree or branches in our case 
dt_model.fit(X_train, y_train)

# Evaluate the model--------------------------------------------------------------------
y_pred = dt_model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\nModel Evaluation Metrics:")
print(f"Mean Squared Error (MSE): {mse:.2f}")
print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"R² Score: {r2:.2f}")

# Prediction for new ticket - for your input data 
new_ticket_features = [2, 1, 0, 1, 2, 1, 1]  # Example features
new_ticket_features = [new_ticket_features]  # Reshape to 2D
predicted_processing_time = dt_model.predict(new_ticket_features)[0]

print("\nPrediction for New Ticket:")
print(f"Predicted Processing Time: {predicted_processing_time:.2f} hours")
#Anmomaly detection using one-class SVM model 

#import libraries 
import polars as pl  # For efficient data handling
from sklearn.preprocessing import StandardScaler  # For scaling features
from sklearn.svm import OneClassSVM  # For anomaly detection
import matplotlib.pyplot as plt  # For visualization

# Load the dataset
df = pl.read_csv("synthetic_incident_bank_data_weighted.csv")

# Parse datetime columns to calculate Resolution Time
datetime_columns = ["Closed", "Start Date"]
for col in datetime_columns:
    if col in df.columns:
        df = df.with_columns(
            pl.col(col).str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S%.f", strict=False).alias(col)
        )

# Calculate the target column: "Resolution Time" in hours
df = df.with_columns(
    (df["Closed"] - df["Start Date"]).dt.total_hours().alias("Resolution Time")
)

# Drop rows with missing values in "Resolution Time"
df = df.filter(pl.col("Resolution Time").is_not_null())

# Encode the categorical column: Impact ----------------------------------------------------------------------------
impact_mapping = {value: idx for idx, value in enumerate(sorted(df.get_column("Impact").unique().to_list()))}
df = df.with_columns(pl.col("Impact").replace(impact_mapping).alias("Impact_encoded"))  #as we will only use one item for our model we will only encode that one item

#Prepare feature for training 
# Select features for anomaly detection
features = df.select(["Reopen Count", "Impact_encoded", "Resolution Time"]).to_numpy()

# Scale features using StandardScaler
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

#Train the model one-class SVM 
# Initialize One-Class SVM
oc_svm = OneClassSVM(kernel="rbf", gamma=0.1, nu=0.05)  
# Train the One-Class SVM on scaled features
oc_svm.fit(scaled_features)

# Predict anomalies (-1 for anomalies, 1 for normal points)
predictions = oc_svm.predict(scaled_features)
df = df.with_columns(pl.Series("Anomaly", predictions))

#Detect and Analyze Anomalies 
# Filter for anomalous tickets (where Anomaly = -1)
anomalies = df.filter(pl.col("Anomaly") == -1)
#1 means normal data point (not anomalous)
#-1 means anomalous data point (flagged as an outlier)

# Count the number of anomaly tickets
num_anomalies = anomalies.height
print(f"\nNumber of anomalous tickets detected: {num_anomalies}")

# Display the patterns in anomalous tickets
print("\nAnomalous Tickets:")
print(anomalies.select(["Reopen Count", "Impact", "Resolution Time"]).head(10))

#Visualize the anomalies using a scatter plot
# Visualize anomalies
plt.figure(figsize=(8, 6))
plt.scatter(scaled_features[:, 0], scaled_features[:, 2], c=predictions, cmap="coolwarm", edgecolors="k")
plt.xlabel("Reopen Count (Scaled)")
plt.ylabel("Resolution Time (Scaled)")
plt.title("Anomaly Detection: Reopen Count vs Resolution Time")
plt.colorbar(label="Anomaly (-1 = Outlier, 1 = Normal)")
plt.show()

# Model Evaluation --------------------------------------------------------------------------------------------
# Calculate general anomaly metrics
total_tickets = df.height
num_anomalies = df.filter(pl.col("Anomaly") == -1).height
num_normal_tickets = df.filter(pl.col("Anomaly") == 1).height
anomaly_proportion = num_anomalies / total_tickets

# Print summary of ticket evaluation
print("\nTicket Evaluation Summary:")
print(f"Total tickets: {total_tickets}")
print(f"Total normal tickets: {num_normal_tickets}")
print(f"Total anomaly tickets detected: {num_anomalies}")
print(f"Proportion of anomaly tickets: {anomaly_proportion:.2%}")

# Visualization to evaluate anomaly separation
print("\nVisualizing anomalies...")
plt.figure(figsize=(8, 6))
plt.scatter(
    scaled_features[:, 0],  # Reopen Count (scaled)
    scaled_features[:, 2],  # Resolution Time (scaled)
    c=predictions,          # Anomaly labels (-1: anomaly, 1: normal)
    cmap="coolwarm",        # Coolwarm for clear separation
    edgecolors="k"
)
plt.xlabel("Reopen Count (Scaled)")
plt.ylabel("Resolution Time (Scaled)")
plt.title("Anomaly Detection Evaluation: Reopen Count vs Resolution Time")
plt.colorbar(label="Anomaly (-1 = Outlier, 1 = Normal)")
plt.show()

# Summary statistics for anomalies
print("\nAnomaly Statistics:")
anomaly_stats = df.filter(pl.col("Anomaly") == -1).select(["Reopen Count", "Impact", "Resolution Time"]).describe()
print(anomaly_stats)

# Summary statistics for normal tickets
print("\nNormal Ticket Statistics:")
normal_ticket_stats = df.filter(pl.col("Anomaly") == 1).select(["Reopen Count", "Impact", "Resolution Time"]).describe()
print(normal_ticket_stats)

# Sensitivity analysis: Train One-Class SVM with multiple nu values
print("\nSensitivity Analysis with Different Nu Values:")
results = []  # To store sensitivity results
nu_values = [0.01, 0.05, 0.10, 0.20]

for nu in nu_values:
    # Train One-Class SVM with current nu value
    oc_svm_tuned = OneClassSVM(kernel="rbf", gamma=0.1, nu=nu)  # Adjust nu (sensitivity)
    oc_svm_tuned.fit(scaled_features)
    
    # Predict anomalies with tuned model
    predictions_tuned = oc_svm_tuned.predict(scaled_features)
    
    # Analyze the anomalies for the current nu
    num_anomalies_tuned = (predictions_tuned == -1).sum()
    proportion_tuned = num_anomalies_tuned / len(predictions_tuned)
    
    # Append results for printing all together
    results.append({"nu": nu, "anomalies": num_anomalies_tuned, "proportion": proportion_tuned})

# Consolidated print block for all `nu` results
print("Sensitivity Analysis Results:")
print("Nu Value | Anomaly Count | Proportion of Anomalies")
print("----------------------------------------------")
for result in results:
    print(f"{result['nu']:.2f}     | {result['anomalies']}          | {result['proportion']:.2%}")

# Optionally: Visualize anomalies per nu value
for result in results:
    nu = result['nu']
    oc_svm_tuned = OneClassSVM(kernel="rbf", gamma=0.1, nu=nu)
    oc_svm_tuned.fit(scaled_features)
    predictions_tuned = oc_svm_tuned.predict(scaled_features)
    
    plt.figure(figsize=(8, 6))
    plt.scatter(
        scaled_features[:, 0], scaled_features[:, 2],
        c=predictions_tuned, cmap="viridis", edgecolors="k"
    )
    plt.xlabel("Reopen Count (Scaled)")
    plt.ylabel("Resolution Time (Scaled)")
    plt.title(f"Anomaly Detection with Nu={nu}")
    plt.colorbar(label="Anomaly (-1 = Outlier, 1 = Normal)")
    plt.show()

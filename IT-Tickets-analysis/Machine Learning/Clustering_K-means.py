#Clustering - K-means clustering for grouping similar tickets together, most common types of tickets, based on patterns

#import libraries
import polars as pl #for working with data 
from sklearn.cluster import KMeans  # K-Means clustering
from sklearn.preprocessing import StandardScaler  #for feature scaling 
import matplotlib.pyplot as plt #for visualization 

#load the data 
df = pl.read_csv("synthetic_incident_bank_data_weighted.csv")

df = df.drop_nulls()  #drop missing data, null values 

#encode categorical columns into numeric representation ---------------------------------------------------------------------------------------
categorical_columns = ["Change Environment", "Assignment Group", "Priority", "Urgency", "Impact"]
for col in categorical_columns:
    unique_values = sorted(df.get_column(col).unique().to_list())  #ensure consistent sorted order 
    mapping = {value: idx for idx, value in enumerate(unique_values)} #numberic encoding 
    df = df.with_columns(pl.col(col).replace(mapping).alias(f"{col}_encoded")) #create new encoded columns

#select features for clustering
features = df.select (["Change Environment_encoded", "Assignment Group_encoded", "Priority_encoded", "Urgency_encoded", "Impact_encoded"]).to_numpy()

#scale the features (K0Means) for feature magnitudes --------------------------------------------------------------------
from sklearn.preprocessing import StandardScaler  #no signle feature dominates the clustering process due to differences in magnitude
scaler  = StandardScaler()                          #basically you dont have 1 and 500 but 1, 1.5 example. 
scaled_features = scaler.fit_transform(features)

#apply K-means clustering-------------------------------------------------------------------------------------------------------------
# Determine the optimal number of clusters using the Elbow Method
inertia = []  # List to store inertia values (sum of squared distances within clusters)
K = range(1, 11)  # Test for 1 to 10 clusters  #this is the default, you can adjust the range based on your dataset size and expected number of clusters

for k in K:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(scaled_features)
    inertia.append(kmeans.inertia_)  # Inertia measures how tightly data points are packed into clusters

# Plot the elbow curve
plt.figure(figsize=(10, 6))
plt.plot(K, inertia, marker='o')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Inertia (Sum of Squared Distances)')
plt.title('Elbow Method to Determine Optimal Number of Clusters')
plt.show()

#Apply the K-Means with Optimal Clusters : 
# Apply K-Means with the chosen number of clusters
optimal_k = 4  # Replace with the number of clusters you identified from the elbow method
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
cluster_labels = kmeans.fit_predict(scaled_features)  # Assign cluster labels to each data point

#Analyze and interpret clusters:
# Add cluster labels to the original dataframe
df = df.with_columns(pl.Series("Cluster", cluster_labels))

# Analyze the clusters
print("\nCluster analysis:")
for cluster in range(optimal_k): #it goes thought all 4 clusters in our case as optimal_k is 4
    print(f"\nCluster {cluster}:")
    cluster_data = df.filter(pl.col("Cluster") == cluster)  #filters dataset that belongs to the current cluster 
    print(cluster_data.group_by("Cluster").agg(  #compute aggregate statistics for that cluster #this is useful to get characteristics of each cluster, like average breach count, median priority and urgency, and how many tickets are in that cluster
        [
            pl.mean("Breach Count").alias("Mean Breach Count"),
            pl.median("Priority_encoded").alias("Median Priority"),
            pl.median("Urgency_encoded").alias("Median Urgency"),
            pl.count("Cluster").alias("Ticket Count"),
        ]
    ))
#Visualize clusters (-----------------------------------------------------------------------------------------
import matplotlib.pyplot as plt

# Example visualization: Priority vs Urgency colored by clusters
plt.figure(figsize=(8, 6))
plt.scatter(
    scaled_features[:, 2],  # Priority_encoded
    scaled_features[:, 3],  # Urgency_encoded
    c=cluster_labels,  # Color points by their cluster
    cmap='viridis'
)
plt.xlabel('Priority (Scaled)')
plt.ylabel('Urgency (Scaled)')
plt.title('K-Means Clustering: Priority vs Urgency')
plt.colorbar(label='Cluster')
plt.show()

#print the amount of tickets in each cluster : 
for cluster_id in sorted(df.get_column("Cluster").unique().to_list()):
    count = df.filter(pl.col("Cluster") == cluster_id)
    print(f"Cluster {cluster_id}: {count.height} tickets")

# Find the cluster with the most tickets
most_common_cluster_df = df.group_by("Cluster").agg(pl.count("Cluster").alias("Cluster_Count"))
most_common_cluster = most_common_cluster_df.sort("Cluster_Count", descending=True).select("Cluster")[0, 0]
print(f"\nMost common cluster: Cluster {most_common_cluster}")
print(f"\n Most common parameters are: ")
most_common_cluster_data = df.filter(pl.col("Cluster") == most_common_cluster)
print(most_common_cluster_data.select(["Change Environment", "Assignment Group", "Priority", "Urgency", "Impact", "Breach Count"]).head(10))

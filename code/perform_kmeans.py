import numpy as np
from sklearn.cluster import KMeans

def perform_kmeans(descriptors, n_clusters=200):
    if descriptors is None:
        print("No descriptors available for KMeans clustering.")
        return None

    print(f"Performing KMeans clustering with {n_clusters} clusters...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    kmeans.fit(descriptors)
    return kmeans

if __name__ == "__main__":
    # Example usage (would be handled in `run_setup.py`)
    descriptors = np.load("descriptors.npy")
    kmeans_model = perform_kmeans(descriptors)

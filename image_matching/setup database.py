import argparse
import glob
import cv2
import numpy as np
from tqdm import tqdm
from sklearn.cluster import KMeans
import os

# Set LOKY_MAX_CPU_COUNT to avoid warning about cores
os.environ['LOKY_MAX_CPU_COUNT'] = '1'

# Function to parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(
        description="Calculate and save BoW vectors for a set of images."
    )
    parser.add_argument("image_dir", type=str, help="Directory containing images for processing.")
    return parser.parse_args()

# Function to calculate BoW vector using KMeans
def calculate_bow_vector(descriptors, kmeans):
    bow_vector = np.zeros(kmeans.n_clusters, dtype=float)
    if descriptors is not None:
        clusters = kmeans.predict(descriptors)
        np.add.at(bow_vector, clusters, 1)
    return bow_vector

def main():
    # Parse the image directory argument
    args = parse_args()

    # Initialize ORB detector
    orb = cv2.ORB_create()

    # Collect descriptors from all images
    image_paths = glob.glob(f"{args.image_dir}/*.png")
    if not image_paths:
        print("No images found in the specified directory.")
        return

    all_descriptors = []
    print("Extracting descriptors from images...")
    for image_path in tqdm(image_paths, desc="Processing Images"):
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            continue
        _, descriptors = orb.detectAndCompute(image, None)
        if descriptors is not None:
            all_descriptors.append(descriptors)

    if not all_descriptors:
        print("No valid descriptors found in the dataset.")
        return

    all_descriptors = np.vstack(all_descriptors)

    # Perform KMeans clustering to build the vocabulary
    n_clusters = 200  # You can change this directly in the script
    print(f"Performing KMeans clustering with {n_clusters} clusters...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    kmeans.fit(all_descriptors)

    # Save the KMeans model to the current directory
    kmeans_output = "kmeans_model.npy"
    np.save(kmeans_output, kmeans)
    print(f"KMeans model saved to '{kmeans_output}'.")

    # Calculate and save BoW vectors for each image
    print("Calculating BoW vectors for each image...")
    bow_vectors = [
        calculate_bow_vector(orb.detectAndCompute(cv2.imread(img, cv2.IMREAD_GRAYSCALE), None)[1], kmeans)
        for img in tqdm(image_paths, desc="Calculating BoW")
    ]

    # Save BoW vectors and image names in the current directory
    bow_output = "bow_vectors.npy"
    np.save(bow_output, bow_vectors)
    np.save("image_names.npy", image_paths)
    print(f"BoW vectors saved to '{bow_output}'.")

if __name__ == "__main__":
    main()

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
    parser.add_argument("dataset_dir", type=str, help="Dataset folder containing the 'frames' folder with images.")
    parser.add_argument("--clusters", type=int, default=200, help="Number of clusters for KMeans (default: 200).")
    return parser.parse_args()

# Function to calculate BoW vector using KMeans
def calculate_bow_vector(descriptors, kmeans):
    bow_vector = np.zeros(kmeans.n_clusters, dtype=float)
    if descriptors is not None:
        clusters = kmeans.predict(descriptors)
        np.add.at(bow_vector, clusters, 1)
    return bow_vector

def main():
    # Parse command-line arguments
    args = parse_args()

    # Define the image directory inside the specified dataset folder
    image_dir = os.path.join(args.dataset_dir, 'frames')

    # Check if the frames directory exists
    if not os.path.exists(image_dir):
        print(f"'frames' folder not found in the dataset directory: {image_dir}")
        return

    # Initialize ORB detector
    orb = cv2.ORB_create()

    # Collect descriptors from all images in the 'frames' folder (supporting PNG and JPG)
    png_images = glob.glob(f"{image_dir}/*.png")
    jpg_images = glob.glob(f"{image_dir}/*.jpg")
    image_paths = png_images + jpg_images  # Combine PNG and JPG image lists

    if not image_paths:
        print("No images found in the 'frames' directory.")
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

    # Perform KMeans clustering with the specified number of clusters
    n_clusters = args.clusters
    print(f"Performing KMeans clustering with {n_clusters} clusters...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    kmeans.fit(all_descriptors)

    # Define the output paths for the .npy files inside the dataset folder
    kmeans_output = os.path.join(args.dataset_dir, "kmeans_model.npy")
    bow_output = os.path.join(args.dataset_dir, "bow_vectors.npy")
    image_names_output = os.path.join(args.dataset_dir, "image_names.npy")

    # Save the KMeans model to the dataset directory
    np.save(kmeans_output, kmeans)
    print(f"KMeans model saved to '{kmeans_output}'.")

    # Calculate and save BoW vectors for each image
    print("Calculating BoW vectors for each image...")
    bow_vectors = [
        calculate_bow_vector(orb.detectAndCompute(cv2.imread(img, cv2.IMREAD_GRAYSCALE), None)[1], kmeans)
        for img in tqdm(image_paths, desc="Calculating BoW")
    ]

    # Save BoW vectors and image names (store relative paths)
    relative_image_paths = [os.path.relpath(img, image_dir) for img in image_paths]
    np.save(bow_output, bow_vectors)
    np.save(image_names_output, relative_image_paths)
    print(f"BoW vectors saved to '{bow_output}'.")
    print(f"Image names (relative paths) saved to '{image_names_output}'.")

if __name__ == "__main__":
    main()

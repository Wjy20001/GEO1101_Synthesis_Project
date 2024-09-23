import argparse
import cv2
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances

# Function to parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(
        description="Match a sample image to a set of BoW vectors."
    )
    parser.add_argument("sample_image", type=str, help="Path to the sample image for matching.")
    parser.add_argument("--show_image", action="store_true", help="Show the sample and best match images.")
    return parser.parse_args()

# Function to calculate BoW vector for a set of descriptors using KMeans clustering
def calculate_bow_vector(descriptors, kmeans):
    bow_vector = np.zeros(kmeans.n_clusters, dtype=float)
    if descriptors is not None:
        clusters = kmeans.predict(descriptors)
        np.add.at(bow_vector, clusters, 1)
    return bow_vector

# Function to resize image for display
def resize_image(image, width=300, height=500):
    return cv2.resize(image, (width, height))

def main():
    args = parse_args()

    # Load the pre-saved KMeans model, BoW vectors, and image names
    print("Loading KMeans model, BoW vectors, and image names...")
    kmeans = np.load("kmeans_model.npy", allow_pickle=True).item()
    bow_vectors = np.load("bow_vectors.npy")
    image_names = np.load("image_names.npy", allow_pickle=True)

    # Calculate BoW vector for the sample image
    print(f"Processing sample image: {args.sample_image}")
    orb = cv2.ORB_create()
    sample_image = cv2.imread(args.sample_image, cv2.IMREAD_GRAYSCALE)
    _, sample_descriptors = orb.detectAndCompute(sample_image, None)

    if sample_descriptors is None:
        print(f"No descriptors found in the sample image.")
        return

    sample_bow_vector = calculate_bow_vector(sample_descriptors, kmeans)

    # Find the closest image based on BoW vector distance (Euclidean distance)
    print("Finding the closest image based on BoW vector...")
    distances = np.linalg.norm(bow_vectors - sample_bow_vector, axis=1)
    best_match_index = np.argmin(distances)

    print(f"The closest image to the sample is: {image_names[best_match_index]}")
    print(f"Distance: {distances[best_match_index]}")

    # If show_image flag is used, display both the sample and best match images
    if args.show_image:
        # Show the sample image
        sample_image_display = cv2.imread(args.sample_image)
        resized_sample = resize_image(sample_image_display)
        cv2.imshow('Sample Image', resized_sample)

        # Show the best match image
        best_match_image = cv2.imread(image_names[best_match_index])
        resized_best_match = resize_image(best_match_image)
        cv2.imshow('Best Match Image', resized_best_match)

        # Wait until a key is pressed, then close the windows
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

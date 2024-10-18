import os
import cv2
import numpy as np
import pickle
from scipy.spatial.distance import euclidean, cosine
import matplotlib.pyplot as plt


# Function to extract SIFT descriptors and keypoints from an image
def extract_sift_descriptors(image_path, sift):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print(f"Image not found: {image_path}")
        return None, None
    keypoints, descriptors = sift.detectAndCompute(image, None)
    return keypoints, descriptors


# Function to create a histogram of visual words for an image
def create_histogram(descriptors, kmeans):
    cluster_labels = kmeans.predict(descriptors)
    histogram, _ = np.histogram(cluster_labels, bins=np.arange(kmeans.n_clusters + 1))
    histogram = histogram / np.sum(histogram)  # Normalize the histogram
    return histogram


# Function to match histograms
def match_images(hist1, hist2):
    return cosine(hist1, hist2)


# Function to display histograms for debugging
def display_histograms(query_histogram, best_matches, ref_histograms):
    # Plot the histogram of the query image
    plt.figure(figsize=(15, 5))
    plt.subplot(1, len(best_matches) + 1, 1)
    plt.bar(np.arange(len(query_histogram)), query_histogram)
    plt.title("Query Histogram")

    # Plot the histograms of the matched reference images
    for i, (_, ref_image_path) in enumerate(best_matches):
        plt.subplot(1, len(best_matches) + 1, i + 2)
        plt.bar(np.arange(len(ref_histograms[i])), ref_histograms[i])
        plt.title(f"Match {i + 1} Histogram")

    plt.show()


# Function to display the query image and reference images with keypoints
def display_results(query_image_path, query_keypoints, best_matches, sift, query_histogram, ref_histograms):
    # Load the query image
    query_image = cv2.imread(query_image_path)

    # Draw keypoints on the query image
    query_image_with_keypoints = cv2.drawKeypoints(query_image, query_keypoints, None, color=(0, 255, 0))

    # Convert BGR to RGB for display
    query_image_with_keypoints = cv2.cvtColor(query_image_with_keypoints, cv2.COLOR_BGR2RGB)

    # Set up the display for query and reference images
    plt.figure(figsize=(15, 5))
    plt.subplot(1, len(best_matches) + 1, 1)
    plt.imshow(query_image_with_keypoints)
    plt.title("Query Image with Keypoints")
    plt.axis('off')

    # Load and display each of the top N matched reference images with keypoints
    for i, (dist, ref_image_path) in enumerate(best_matches):
        ref_image = cv2.imread(ref_image_path)

        # Extract keypoints for the reference image
        ref_keypoints, _ = extract_sift_descriptors(ref_image_path, sift)

        # Draw keypoints on the reference image
        ref_image_with_keypoints = cv2.drawKeypoints(ref_image, ref_keypoints, None, color=(0, 255, 0))
        ref_image_with_keypoints = cv2.cvtColor(ref_image_with_keypoints, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB

        # Display reference image with keypoints
        plt.subplot(1, len(best_matches) + 1, i + 2)
        plt.imshow(ref_image_with_keypoints)
        plt.title(f"Match {i + 1}\nDist: {dist:.2f}")
        plt.axis('off')

    # Show the images with keypoints
    plt.show()

    # Display the histograms of the query and reference images
    display_histograms(query_histogram, best_matches, ref_histograms)


# Load preprocessed reference data and match query images
def match_query_images(query_image_paths, reference_data_file, top_n_matches=5):
    sift = cv2.SIFT_create(
        nfeatures=15000,  # Increase the number of keypoints
        contrastThreshold=0.03,  # Detect more keypoints in low-contrast areas
        edgeThreshold=5,  # Lower to detect more edge keypoints
        sigma=1.2  # Slightly increase Gaussian smoothing for noise reduction
    )

    # Load the saved reference data
    with open(reference_data_file, 'rb') as f:
        ref_image_paths, ref_histograms, kmeans = pickle.load(f)

    # Process the query images
    for query_image_path in query_image_paths:
        print(f"\nProcessing query image: {query_image_path}")
        query_keypoints, query_descriptors = extract_sift_descriptors(query_image_path, sift)

        if query_descriptors is None:
            print(f"No descriptors found for query image: {query_image_path}")
            continue

        # Create a histogram for the query image
        query_histogram = create_histogram(query_descriptors, kmeans)

        # Compare query histogram to reference histograms
        distances = []
        matched_ref_histograms = []
        matched_ref_descriptors = []
        best_matches = []

        # Compute histograms for all reference images
        for i, ref_hist in enumerate(ref_histograms):
            dist = match_images(query_histogram, ref_hist)
            distances.append((dist, ref_image_paths[i]))

        # Sort distances and get top N matches
        distances.sort(key=lambda x: x[0])
        best_matches = distances[:top_n_matches]

        # Recalculate histograms for the matched references
        for dist, ref_image_path in best_matches:
            ref_keypoints, ref_descriptors = extract_sift_descriptors(ref_image_path, sift)
            ref_histogram = create_histogram(ref_descriptors, kmeans)  # Recalculate the histogram
            matched_ref_histograms.append(ref_histogram)

        # Print top N matches in the terminal
        for rank, (dist, ref_image) in enumerate(best_matches, start=1):
            print(f"Top {rank} match: {ref_image} with distance {dist}")

        # Display the results (query image with keypoints + top N matches with keypoints)
        display_results(query_image_path, query_keypoints, best_matches, sift, query_histogram, matched_ref_histograms)


# Paths to your query folder and reference data file
query_folder = r'D:\geomatics\geo1101\imagematching4sift\data\front\user_images\square_images'
reference_data_file = r'D:\geomatics\geo1101\imagematching4sift\data\front\cache\reference_data.pkl'

# Manually specify the query images
selected_query_images = [
    os.path.join(query_folder, 'p000126_front.jpg'),
    os.path.join(query_folder, 'image001_front.jpg'),
    os.path.join(query_folder, 'image002_front.jpg'),
    os.path.join(query_folder, 'image003_front.jpg')
]

# Match the query images against the preprocessed reference data and display the results
match_query_images(selected_query_images, reference_data_file, top_n_matches=5)

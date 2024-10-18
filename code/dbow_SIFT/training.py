import os
import cv2
import numpy as np
import pickle
from sklearn.cluster import KMeans


# Function to extract SIFT descriptors from an image
def extract_sift_descriptors(image_path, sift):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print(f"Image not found: {image_path}")
        return None
    keypoints, descriptors = sift.detectAndCompute(image, None)
    return descriptors


# Function to build a Bag of Words (BoW) model using k-means clustering
def build_bow_model(descriptors_list, num_clusters=50):
    all_descriptors = np.vstack(descriptors_list)
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(all_descriptors)
    return kmeans


# Function to create a histogram of visual words for an image
def create_histogram(descriptors, kmeans):
    cluster_labels = kmeans.predict(descriptors)
    histogram, _ = np.histogram(cluster_labels, bins=np.arange(kmeans.n_clusters + 1))
    return histogram


# Function to preprocess reference images for a given dataset (e.g., front, left, right, top) and save to a file
def preprocess_reference_images(reference_folder, dataset, ground_truth, cache_folder, num_clusters=50):
    sift = cv2.SIFT_create(
        nfeatures=15000,  # Increase the number of keypoints
        contrastThreshold=0.03,  # Detect more keypoints in low-contrast areas
        edgeThreshold=5,  # Lower to detect more edge keypoints
        sigma=1.2  # Slightly increase Gaussian smoothing for noise reduction
    )

    # Create cache folder if it doesn't exist
    os.makedirs(cache_folder, exist_ok=True)

    # Load reference images from the specific dataset folder and extract descriptors
    ref_image_paths = [os.path.join(reference_folder, dataset, ground_truth, img) for img in
                       os.listdir(os.path.join(reference_folder, dataset, ground_truth))]
    ref_descriptors_list = []

    for image_path in ref_image_paths:
        descriptors = extract_sift_descriptors(image_path, sift)
        if descriptors is not None:
            ref_descriptors_list.append(descriptors)

    # Build the BoW model using the reference images
    kmeans = build_bow_model(ref_descriptors_list, num_clusters=num_clusters)

    # Create histograms for reference images
    ref_histograms = []
    for descriptors in ref_descriptors_list:
        histogram = create_histogram(descriptors, kmeans)
        ref_histograms.append(histogram)

    # Save histograms and kmeans model to a file in the cache folder
    output_file = os.path.join(reference_folder, dataset, cache_folder, 'reference_data.pkl')
    with open(output_file, 'wb') as f:
        pickle.dump((ref_image_paths, ref_histograms, kmeans), f)

    print(f"{dataset.capitalize()} reference images processed and saved to {output_file}")


# Paths to the reference folder (ground truth) and cache folder
reference_folder = r'D:\geomatics\geo1101\imagematching4sift\data'


# Datasets to train (front, left, right, top)
datasets = ['front']

ground_truth = 'ground_truth'
cache_folder = 'cache'


# Train on each dataset and save the results to the cache folder
for dataset in datasets:
    preprocess_reference_images(reference_folder, dataset, ground_truth, cache_folder, num_clusters=50)

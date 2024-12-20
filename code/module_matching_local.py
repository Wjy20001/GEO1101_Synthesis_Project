import os
import numpy as np
import pickle
from scipy.spatial.distance import cosine
import torch
import torchvision.models as models
import torchvision.transforms as transforms
import pandas as pd
from sklearn.cluster import DBSCAN
# from const import USER_IMAGE_PATH, CACHE_PATH, GROUND_TRUTH_COORDINATES_PATH, WALL_COORDINATES_PATH
from PIL import Image
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='torchvision')


# Extract image features using the VGG16 model
def extract_vgg16_features(image_path, model, transform):
    img = Image.open(image_path).convert('RGB')
    img = transform(img)
    img = img.unsqueeze(0)  # Add batch dimension

    # Extract features
    with torch.no_grad():
        features = model(img)
    
    features = features.flatten().numpy()  # Convert PyTorch tensor to numpy array and flatten
    return features

# Function to extract coordinates from CSV based on matching image name
def extract_coordinates_from_match(ref_image_path, csv_path):
    # Load the CSV file
    coordinates_df = pd.read_csv(csv_path)

    # Extract the base part of the image name (remove _front, _left suffixes)
    base_name = os.path.basename(ref_image_path).split('_')[0] + '.jpg'
    
    # Find the corresponding image coordinates
    row = coordinates_df[coordinates_df['Image'] == base_name]
    
    if row.empty:
        print(f"Coordinates not found for image: {base_name}")
        return (0.0, 0.0)  # Return (0.0, 0.0) if coordinates are not found
    
    # Extract X, Y coordinates
    x = row['X'].values[0]
    y = row['Y'].values[0]
    return (x, y)

# Perform DBSCAN clustering and return the coordinates of the largest cluster's center
def apply_dbscan_and_find_center(all_coords, eps=2, min_samples=3):
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(all_coords)

    # Find the largest cluster (excluding outliers, i.e., label -1)
    unique_labels = set(labels)
    largest_cluster_center = (0.0, 0.0)
    largest_cluster_size = 0
    
    for label in unique_labels:
        if label == -1:
            continue  # Skip outliers
        label_coords = [all_coords[i] for i in range(len(all_coords)) if labels[i] == label]
        
        # If this cluster is the largest, calculate its center and update
        if len(label_coords) > largest_cluster_size:
            largest_cluster_size = len(label_coords)
            label_coords = np.array(label_coords)
            largest_cluster_center = np.mean(label_coords, axis=0)
    # print(f'largest DBSCAN cluster center =\t{largest_cluster_center}')
    return tuple(largest_cluster_center)

# Load preprocessed reference data and match query images
def match_query_images_and_get_center(query_image_paths, reference_data_file, csv_path, top_n_matches=6, min_DBSCAN_samples=3):
    # Load the VGG16 model
    model = models.vgg16(pretrained=True)
    model = torch.nn.Sequential(*list(model.children())[:-1])  # Remove the classification layer
    model.eval()

    # Define image transformation
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    all_coords = []  # To store all matched image coordinates
    
    # Process each query image
    for query_image_path in query_image_paths:
        # print(f"Processing query image: {query_image_path}")

        # Extract VGG16 features for the query image
        query_features = extract_vgg16_features(query_image_path, model, transform)

        # Load saved reference data
        with open(reference_data_file, 'rb') as f:
            ref_image_paths, ref_vgg16_features = pickle.load(f)

        # Compare query image with reference images' VGG16 feature vectors
        distances = []
        for i, ref_features in enumerate(ref_vgg16_features):
            distance = cosine(query_features, ref_features)
            distances.append((distance, ref_image_paths[i]))

        # Sort and get the top N matches
        distances.sort(key=lambda x: x[0])
        best_matches = distances[:top_n_matches]

        # Extract coordinates for each matched image
        for _, ref_image_path in best_matches:
            coord = extract_coordinates_from_match(ref_image_path, csv_path)
            all_coords.append(coord)

    # Perform DBSCAN clustering on all matched image coordinates and return the center of the largest cluster
    # print('-' * 20)
    # print(f'Starting DBSCAN with {len(all_coords)} coordinates')
    largest_cluster_center = apply_dbscan_and_find_center(all_coords, min_samples=min_DBSCAN_samples)
    
    return largest_cluster_center


if __name__ == "__main__":
    # Use paths defined in const.py
    reference_data_file = os.path.join("data", "training", 'reference_vgg16_data.pkl')
    csv_path = os.path.join("data", "csvs", "slam_camera_coordinates_merged.csv")

    user_image_folder = os.path.join("data", "user_images")
    # Specify the query images
    selected_query_images = [os.path.join(user_image_folder, 'room_val005.jpg'),
                            os.path.join(user_image_folder, 'room_val006.jpg'),
                            os.path.join(user_image_folder, 'room_val007.jpg')]

    # Match query images and get the center of the largest cluster
    center_coords = match_query_images_and_get_center(selected_query_images, reference_data_file, csv_path, top_n_matches=6)
    
    # Print the result
    print(type(center_coords))
    print(f"Center of the largest cluster: {center_coords}")

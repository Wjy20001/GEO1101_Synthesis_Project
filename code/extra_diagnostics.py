import os
import glob
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import module_matching_local as mm

import pickle
from scipy.spatial.distance import cosine
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from sklearn.cluster import DBSCAN
import ast
# from const import USER_IMAGE_PATH, CACHE_PATH, GROUND_TRUTH_COORDINATES_PATH, WALL_COORDINATES_PATH
from PIL import Image
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='torchvision')

import matplotlib.pyplot as plt
from convertcoordinate import convert_coordinates as cc

import geopandas as gpd
from shapely.geometry import Point

def get_accuracy_and_time_from_df(df_path):
    """Extracts accuracy and average computation time from a CSV file."""
    df = pd.read_csv(df_path)
    accuracy = (df['true_room'] == df['found_room']).mean() * 100
    avg_time = df['calculation_time'].mean()
    return accuracy, avg_time

def collect_data(diagnostics_folder):
    """Collects accuracy and computation time for each file and groups by 'cs'."""
    grouped_data = defaultdict(lambda: {"N_values": [], "accuracies": [], "comp_times": []})
    all_N_values = set()

    for csv_file in glob.glob(os.path.join(diagnostics_folder, '*.csv')):
        accuracy, avg_time = get_accuracy_and_time_from_df(csv_file)
        match = re.search(r'N=(\d+)_cs=(\d+)', os.path.basename(csv_file))
        
        if match:
            N, cs = int(match.group(1)), match.group(2)
            all_N_values.add(N)
            grouped_data[cs]["N_values"].append(N)
            grouped_data[cs]["accuracies"].append(accuracy)
            grouped_data[cs]["comp_times"].append(avg_time)

    # Align each 'cs' group with the full set of N values
    all_N_values = sorted(all_N_values)
    for cs, data in grouped_data.items():
        accuracies_aligned, comp_times_aligned = [], []
        for N in all_N_values:
            if N in data["N_values"]:
                index = data["N_values"].index(N)
                accuracies_aligned.append(data["accuracies"][index])
                comp_times_aligned.append(data["comp_times"][index])
            else:
                accuracies_aligned.append(np.nan)
                comp_times_aligned.append(np.nan)
        data.update({"N_values": all_N_values, "accuracies": accuracies_aligned, "comp_times": comp_times_aligned})

    return grouped_data, all_N_values

def plot_grouped_data(grouped_data, all_N_values, diagnostics_folder, ylabel, title, metric_key, filename, accu=False):
    """Plots grouped data with different 'cs' values in a single plot."""
    fig, ax = plt.subplots()
    width = 0.15
    x = np.arange(len(all_N_values))
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    for i, (cs, data) in enumerate(sorted(grouped_data.items())):
        ax.bar(x + i * width, data[metric_key], width, label=f'{cs}', color=colors[i % len(colors)])

    ax.set_xlabel('N best matches')
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if accu:
        ax.set_yticks(range(50, 101, 5))
        ax.set_ylim(50, 100)
    else:
        ax.set_yticks(np.linspace(0,5,11))
        ax.set_ylim(0, 5)

    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(all_N_values, rotation=0, ha='right')
    ax.grid()
    ax.legend(title = 'cluster size', loc='lower right')

    plt.savefig(os.path.join(diagnostics_folder, filename))
    plt.show()


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
        query_features = mm.extract_vgg16_features(query_image_path, model, transform)

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
            coord = mm.extract_coordinates_from_match(ref_image_path, csv_path)
            all_coords.append(coord)

    # Perform DBSCAN clustering on all matched image coordinates and return the center of the largest cluster
    print('-' * 20)
    print(f'Starting DBSCAN with {len(all_coords)} coordinates')
    largest_cluster_center = mm.apply_dbscan_and_find_center(all_coords, min_samples=min_DBSCAN_samples)
    
    return all_coords, largest_cluster_center


def get_mismatched_coordinates_and_dbscan_center(df_path):
    df = pd.read_csv(df_path)

    validate: pd.Series = df['true_room'] == df['found_room']
    correct_match_count: int = validate.sum()
    df_length: int = len(df)
    matched_percentage: float = validate.mean() * 100
    mismatches = df[~validate]

    reference_data_file = os.path.join("API", "data", 'model.pkl')
    csv_path = os.path.join("API", "data", "slam_coordinates.csv")

    user_image_folder = os.path.join("data", "user_images")


    # Initialize the new columns with empty lists
    mismatches['matched_coordinates'] = None
    mismatches['cluster_center'] = None

    # Loop over each row in the DataFrame
    for idx, img_liststring in mismatches['user_image_name'].items():
        # Convert the string to an actual list
        img_list = ast.literal_eval(img_liststring)
        
        # Specify the query images
        selected_query_images = [os.path.join(user_image_folder, image) for image in img_list]

        # Match query images and get the center of the largest cluster
        all_matched_coordinates, cluster_center = match_query_images_and_get_center(
            selected_query_images, 
            reference_data_file, 
            csv_path, 
            top_n_matches=6, 
            min_DBSCAN_samples=2
        )

        mismatches.at[idx, 'matched_coordinates'] = all_matched_coordinates
        mismatches.at[idx, 'cluster_center'] = cluster_center

    return mismatches
    

def plot_mismatched_coords(df, geojson_path):
    # Load the floorplan polygons
    floorplan = gpd.read_file(geojson_path)
    
    for idx, row in df.iterrows():
        matched_coordinates = row['matched_coordinates']
        cluster_center = row['cluster_center']
        
        # Ensure that matched_coordinates and cluster_center are not empty
        if matched_coordinates and cluster_center:
            # Create a new plot for each row
            plt.figure(figsize=(8, 8))
            
            # Plot the floorplan polygons
            floorplan.plot(ax=plt.gca(), color='lightgrey', edgecolor='black', alpha=0.5)
            
            # Plot matched coordinates in blue
            matched_x = []
            matched_y = []
            for coord in matched_coordinates:
                #append CRS converted x and y to list above
                matched_x.append(cc(coord)[0])
                matched_y.append(cc(coord)[1])

            plt.scatter(matched_x, matched_y, color='blue', label='Matched Coordinates')
            
            cluster_center = cc(cluster_center)
            
            # Plot cluster center in orange
            plt.scatter(cluster_center[0], cluster_center[1], color='orange', label='Cluster Center', marker='x', s=100)
            
            # Add title and labels
            plt.title(f"Test user position {idx} - Coordinate Clustering")
            plt.xlabel("Latitude")
            plt.ylabel("Longitude")
            plt.legend()
            plt.grid()
            # Display the plot
            plt.savefig(os.path.join("data","diagnostics", f"mismatch_cluster_plot_position{idx}.png"))
            plt.show()

    

if __name__ == "__main__":
    diagnostics_folder = os.path.join('data', 'diagnostics')

    # grouped_data, all_N_values = collect_data(diagnostics_folder)

    right_csv = os.path.join(diagnostics_folder, "diagnostics_multi_N=6_cs=2.csv")
    floorplan_path = os.path.join("API", "data", "floorplan.geojson")
    mismatched_df = get_mismatched_coordinates_and_dbscan_center(right_csv)


    plot_mismatched_coords(mismatched_df, floorplan_path)

    # # Plot Accuracy
    # plot_grouped_data(
    #     grouped_data, all_N_values, diagnostics_folder,
    #     ylabel="Accuracy (%)", title="Accuracy",
    #     metric_key="accuracies", filename="accuracy_plot.png", accu=True
    # )

    # # Plot Computation Time
    # plot_grouped_data(
    #     grouped_data, all_N_values, diagnostics_folder,
    #     ylabel="Average Computation Time (s)", title="Computation Time",
    #     metric_key="comp_times", filename="comp_time_plot.png"
    # )

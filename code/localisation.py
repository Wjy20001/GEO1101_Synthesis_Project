import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from const import IMAGE_NAMES_CACHE_PATH
from image import find_matched_images, match_user_image
from preview import preview
from scipy.spatial import KDTree
from training import training

program_dir = os.getcwd()  # Get the current working directory


# Function to get wall coordinates and lines connecting points
def get_wall_lines():
    path_BK_wall_csv = os.path.join(
        program_dir, "data", "csvs", "BK_wall_coordinates.csv"
    )
    bk_wall_df = pd.read_csv(path_BK_wall_csv)  # Read wall coordinate data

    points = bk_wall_df[["x", "y"]].values  # Extract x, y coordinates

    # Step 2: Find the nearest neighbors for each point using KDTree
    tree = KDTree(points)  # Build a KDTree for efficient neighbor searching
    distances, indices = tree.query(
        points, k=4
    )  # Query for the closest 3 neighbors

    # Step 3: Draw lines connecting each point to its closest neighbors
    threshold = 2  # in meters, only connect points within this distance
    lines = []
    for i, dists in enumerate(distances):
        for j in range(
            1, len(dists)
        ):  # Start from the 1st nearest neighbor (skip the point itself)
            if (
                dists[j] < threshold
            ):  # Only add lines for distances below the threshold
                nn = indices[i, j]  # Get the index of the nearest neighbor
                line = [
                    points[i],
                    points[nn],
                ]  # Create a line between the two points
                lines.append(line)

    return lines  # Return the list of lines


# Function to create a scatter plot with matched points and wall lines
def scatterplot(points: list[list[float, float, float]]):
    plt.figure(figsize=(8, 8))  # Set the plot size

    lines: list = get_wall_lines()  # Get wall lines to draw

    # Draw the wall lines in blue
    for line in lines:
        plt.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], "b-")

    # Step 5: Plot the matched points (assuming 'X', 'Y' coordinates in `points`)
    for point in points:
        plt.plot(
            point[0], point[1], "ro", markersize=3
        )  # Plot matched points as red dots

    # Configure plot labels and grid
    plt.title("BK Hall Floor plan with Matched Points")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    plt.show()


# Function to compute a central point (localization)
def localisation(points: list) -> list[float, float, float]:
    point = np.mean(points)  # Compute the mean of the points (for now)
    return point  # Return the average point


# Class to handle image data and extract coordinates based on image name
class ImageData:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path  # Path to the CSV file
        # Read CSV file, using header and skipping spaces in headers
        self.image_df = pd.read_csv(csv_path, header=0, skipinitialspace=True)

    # Function to find the XYZ coordinates and pose (heading, roll, pitch) based on the image name
    def name2coord(self, img_name: str) -> tuple[float, float, float]:
        # Find the row where the image name matches, using part of the name
        row = self.image_df[
            self.image_df["Image"].str.contains(img_name.split("_")[0])
        ]
        # Extract the XYZ coordinates
        xyz = (row["X"], row["Y"], row["Z"])
        pose = (
            row["Heading"],
            row["Roll"],
            row["Pitch"],
        )  # Pose can be used if needed
        return xyz  # Return the XYZ coordinates


# Main function to run the image matching and plotting
def main():
    user_image_dir = os.path.join(
        os.getcwd(), "data", "user_images"
    )  # Directory of user images
    # List of image paths
    user_images = [
        os.path.join(user_image_dir, filename)
        for filename in [
            "validation_001.jpg",
            "validation_002.jpg",
            "validation_003.jpg",
        ]
    ]
    images = [
        cv2.imread(image) for image in user_images
    ]  # Read the images using OpenCV
    db = training()  # Run training to get a database (feature extraction)
    print("db: ", db)
    if db is None:
        print("Database not found")
        return  # Exit if the database is not found

    cwd = os.getcwd()  # Get current working directory
    image_names = np.load(
        IMAGE_NAMES_CACHE_PATH
    )  # Load cached image names for matching
    best_matched_images = []  # List to store best-matched image names
    # Loop through the user images and find the best match for each
    for i, image in enumerate(images):
        matched_image_name, _ = find_matched_images(
            image, db, image_names, 1
        )[
            0
        ]  # Find the best match
        best_matched_images.append(
            matched_image_name
        )  # Append the matched image name
    # Load image data from the CSV containing camera coordinates
    img_data = ImageData(
        os.path.join(
            os.getcwd(), "data", "csvs", "slam_camera_coordinates.csv"
        )
    )
    print("matched images", best_matched_images)
    points = []
    # For each matched image, get the corresponding coordinates
    for img in best_matched_images:
        coord = img_data.name2coord(img)  # Get coordinates for each image
        points.append(coord)  # Append to the list of points

    scatterplot(points)  # Plot the matched points on the floor plan


# Entry point for the script
if __name__ == "__main__":
    main()  # Call the main function to execute the program

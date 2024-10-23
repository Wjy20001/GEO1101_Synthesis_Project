import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from const import GROUND_TRUTH_PATH, WALL_COORDINATES_PATH
from image import ImageMatcher
from sklearn.cluster import DBSCAN
from scipy.spatial import KDTree

def points_to_lines(points: list[tuple[float, float]]) -> list:
    tree = KDTree(points)  # Build a KDTree for efficient neighbor searching
    distances, indices = tree.query(
        points, k=4
    )  # Query for the closest 3 neighbors

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

# Function to create a scatter plot with matched points and wall lines, including DBSCAN clusters and outliers
def scatterplot_with_dbscan(
    base_points: list[tuple[float, float]], 
    matched_points: list[tuple[float, float]],
    labels: np.ndarray
):
    plt.figure(figsize=(8, 8))  # Set the plot size

    lines: list = points_to_lines(base_points)  # Get the wall lines

    # Draw the wall lines in blue
    for line in lines:
        plt.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], "b-")

    # Plot the clustered points (using DBSCAN labels)
    for i, point in enumerate(matched_points):
        if labels[i] == -1:
            # Plot outliers in red ('ro' means red circle markers)
            plt.plot(point[0], point[1], "ro", markersize=5, label="Outlier" if i == 0 else "")
        else:
            # Plot clustered points in green ('go' means green circle markers)
            plt.plot(point[0], point[1], "go", markersize=5, label="Cluster" if i == 0 else "")

    # Configure plot labels and grid
    plt.title("BK Hall Floor plan with DBSCAN clusters and outliers")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    plt.show()

# Function to perform DBSCAN clustering
def apply_dbscan(points: list[tuple[float, float]], eps=2, min_samples=2) -> np.ndarray:
    """
    Apply DBSCAN clustering to the matched points.

    Parameters:
    -----------
    points : list of tuples
        List of (x, y) coordinates.
    eps : float, optional
        The maximum distance between two points for one to be considered as in the neighborhood of the other.
    min_samples : int, optional
        The number of points in a neighborhood to be considered as a core point.

    Returns:
    --------
    labels : np.ndarray
        Array of cluster labels. -1 represents outliers.
    """
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(points)
    return labels

# Class to handle image data and extract coordinates based on image name
class ImageData:
    def __init__(
        self,
        csv_path: str,
        image_col: str = "Image",
        x_col: str = "X",
        y_col: str = "Y",
        z_col: str = "Z",
        heading_col: str = "Heading",
        roll_col: str = "Roll",
        pitch_col: str = "Pitch",
    ):
        self.csv_path = csv_path
        self.image_df = pd.read_csv(csv_path, header=0, skipinitialspace=True)
        self.image_col = image_col
        self.x_col = x_col
        self.y_col = y_col
        self.z_col = z_col
        self.heading_col = heading_col
        self.roll_col = roll_col
        self.pitch_col = pitch_col

    # Function to find the XYZ coordinates and pose (heading, roll, pitch) based on the image name
    def name2coord(self, img_name: str) -> tuple[float, float, float]:
        row = self.image_df[self.image_df[self.image_col].str.contains(img_name.split("_")[0])]
        xyz = (
            row[self.x_col].values[0],
            row[self.y_col].values[0],
            row[self.z_col].values[0],
        )
        return xyz

# Entry point for the script
if __name__ == "__main__":
    user_image_dir = os.path.join(os.getcwd(), "data", "user_images")
    user_images = [
        os.path.join(user_image_dir, filename)
        for filename in [
            "validation_002.jpg",
            "validation_012.png",
            "validation_022.jpg",
            "validation_032.jpg",
            "validation_042.jpg",
        ]
    ]

    image_matcher = ImageMatcher()
    img_data = ImageData(GROUND_TRUTH_PATH)

    wall_coordinates = pd.read_csv(WALL_COORDINATES_PATH)

    # Process each user image
    for image_path in user_images:
        matched_images = image_matcher.find_matched_images(image_path, 6)

        # Get coordinates for the matched images
        matched_coords = [img_data.name2coord(matched[0])[:2] for matched in matched_images]

        # Apply DBSCAN clustering
        labels = apply_dbscan(matched_coords)

        # Visualize with scatterplot including clusters and outliers
        scatterplot_with_dbscan(
            [tuple(x) for x in wall_coordinates[["x", "y"]].values],  # Base points (walls)
            matched_coords,  # Points to cluster
            labels  # DBSCAN labels
        )

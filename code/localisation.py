import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from const import GROUND_TRUTH_PATH, WALL_COORDINATES_PATH
from image import ImageMatcher
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


# Function to create a scatter plot with matched points and wall lines
def scatterplot(
    base_points: list[tuple[float, float]],
    hightlight_points: list[tuple[float, float]],
):
    plt.figure(figsize=(8, 8))  # Set the plot size

    lines: list = points_to_lines(base_points)  # Get the wall lines

    # Draw the wall lines in blue
    for line in lines:
        plt.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], "b-")

    # Step 5: Plot the matched points (assuming 'X', 'Y' coordinates in `points`)
    for point in hightlight_points:
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
def localisation(
    points: list[tuple[float, float, float]]
) -> tuple[float, float, float]:
    point: tuple[float, float, float] = tuple(
        np.mean(np.array(points), axis=0)
    )  # Compute the mean of the points (for now)
    return point  # Return the average point


# Class to handle image data and extract coordinates based on image name
class ImageData:
    csv_path: str  # Path to the CSV file
    image_df: pd.DataFrame  # DataFrame to store image data
    image_col: str  # Column name for the image name
    x_col: str  # Column name for the X coordinate
    y_col: str  # Column name for the Y coordinate
    z_col: str  # col name for the Z coordinate
    heading_col: str  # col name for the heading
    roll_col: str  # col name for the roll
    pitch_col: str  # col name for the pitch

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
        self.csv_path = csv_path  # Path to the CSV file
        # Read CSV file, using header and skipping spaces in headers
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
        # Find the row where the image name matches, using part of the name
        row = self.image_df[
            self.image_df[self.image_col].str.contains(img_name.split("_")[0])
        ]
        # Extract the XYZ coordinates
        xyz = (
            row[self.x_col].values[0],
            row[self.y_col].values[0],
            row[self.z_col].values[0],
        )
        _ = (
            row[self.heading_col].values[0],
            row[self.roll_col].values[0],
            row[self.pitch_col].values[0],
        )  # Pose can be used if needed
        return xyz  # Return the XYZ coordinates


# Entry point for the script
if __name__ == "__main__":
    user_image_dir = os.path.join(
        os.getcwd(), "data", "user_images"
    )  # Directory of user images

    # List of image paths
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
    matched_images_names = [
        image_matcher.find_matched_images(image_path, 1)[0][0]
        for image_path in user_images
    ]

    img_data = ImageData(GROUND_TRUTH_PATH)

    localised_coordinates = [
        img_data.name2coord(img) for img in matched_images_names
    ]

    wall_coordinates = pd.read_csv(WALL_COORDINATES_PATH)

    scatterplot(
        [tuple(x) for x in wall_coordinates[["x", "y"]].values],
        [coord[:2] for coord in localised_coordinates],
    )

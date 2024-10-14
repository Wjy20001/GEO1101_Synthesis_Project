import os

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

from API.const import API_FOLDER_PATH, GROUND_TRUTH_PATH
from API.image import ImageMatcher


class ImageData:
    """
    Class to handle image data and extract coordinates based on image names from a CSV file.

    Attributes:
    -----------
    csv_path : str
        Path to the CSV file containing image metadata.
    image_df : pd.DataFrame
        DataFrame containing image metadata loaded from the CSV file.
    image_col : str
        Column name in the CSV for the image names.
    x_col, y_col, z_col : str
        Column names in the CSV for X, Y, Z coordinates.
    heading_col, roll_col, pitch_col : str
        Column names for heading, roll, and pitch of the image.

    Methods:
    --------
    name2coord(img_name: str) -> tuple[float, float, float]:
        Returns the XYZ coordinates corresponding to the given image name.
    """

    def __init__(
        self,
        csv_path: str,
        image_col: str = "Image",
        x_col: str = "X",
        y_col: str = "Y",
        z_col: str = "Z",
    ):
        self.csv_path = csv_path
        self.image_df = pd.read_csv(csv_path, header=0, skipinitialspace=True)
        self.image_col = image_col
        self.x_col = x_col
        self.y_col = y_col
        self.z_col = z_col

    def name2coord(self, img_name: str) -> tuple[float, float, float]:
        """
        Finds the XYZ coordinates for a given image name from the loaded DataFrame.

        Parameters:
        -----------
        img_name : str
            The name of the image to find coordinates for.

        Returns:
        --------
        tuple[float, float, float]
            A tuple containing the X, Y, and Z coordinates.
        """
        row = self.image_df[
            self.image_df[self.image_col].str.contains(img_name.split("_")[0])
        ]
        xyz = (
            row[self.x_col].values[0],
            row[self.y_col].values[0],
            row[self.z_col].values[0],
        )
        return xyz


def apply_dbscan(
    points: list[tuple[float, float]], eps=2, min_samples=2
) -> list[tuple[float, float]]:
    """
    Apply DBSCAN clustering to a set of points and return non-outliers.

    Parameters:
    -----------
    points : list of tuples
        List of (x, y) coordinates to be clustered.
    eps : float, optional
        Maximum distance between two points to be considered neighbors.
    min_samples : int, optional
        Minimum number of points to form a dense region (core point).

    Returns:
    --------
    non_outliers : list of tuples
        A list of (x, y) coordinates that are not outliers (points with cluster label -1 are excluded).
    """
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(points)
    non_outliers = [
        point for point, label in zip(points, labels) if label != -1
    ]
    return non_outliers


def point_list_average(points: np.ndarray) -> tuple[float, float]:
    """
    Calculate the average of a list of 2D points.

    Parameters:
    -----------
    points : np.ndarray
        Array of (x, y) points.

    Returns:
    --------
    tuple[float, float]
        A tuple containing the average x and y values.
    """
    average_point = np.average(points, axis=0)
    return tuple(average_point)


def get_coord_from_image_set(user_image_dir: str) -> tuple[float, float]:
    """
    Process images in the directory, match them to coordinates, and return the average location.

    Parameters:
    -----------
    user_image_dir : str
        The directory containing the images to process.

    Returns:
    --------
    tuple[float, float]
        The average coordinates of all matched points. Returns (0.0, 0.0) if no valid points are found.
    """
    # List all image files in the directory
    user_images = [
        os.path.join(user_image_dir, filename)
        for filename in os.listdir(user_image_dir)
        if os.path.isfile(os.path.join(user_image_dir, filename))
    ]

    # Initialize objects for image matching and coordinate retrieval
    image_matcher = ImageMatcher()
    img_data = ImageData(GROUND_TRUTH_PATH)

    locations = []

    # Process each image and retrieve coordinates
    for image_path in user_images:
        matched_images = image_matcher.find_matched_images(image_path, 6)

        # Get coordinates for matched images
        matched_coords = [
            img_data.name2coord(matched[0])[:2] for matched in matched_images
        ]

        # Normally, you would apply DBSCAN clustering, but it's temporarily removed
        non_outliers = matched_coords  # Uncomment DBSCAN if needed

        if non_outliers:
            # Calculate the average of non-outliers
            location = point_list_average(np.array(non_outliers))
            locations.append(location)

    # Return the average of all collected locations or (0.0, 0.0) if no valid locations found
    if locations:
        return point_list_average(np.array(locations))
    else:
        return (0.0, 0.0)

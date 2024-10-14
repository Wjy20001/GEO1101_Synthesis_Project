import os
from typing import Any

import cv2
import dbow
import numpy as np

import API.training as training
from API.const import DATABASE_CACHE_PATH, IMAGE_NAMES_CACHE_PATH


class ImageMatcher:
    """
    A class to match images using ORB (Oriented FAST and Rotated BRIEF) descriptors and a pre-trained database.

    Attributes:
    -----------
    db : dbow.Database
        The pre-trained database containing ORB descriptors for image matching.
    images_names : np.ndarray
        Array containing the names of images corresponding to the database entries.
    orb : Any
        The ORB detector and descriptor extractor from OpenCV.

    Methods:
    --------
    __init__(image_names_path: str = IMAGE_NAMES_CACHE_PATH, db_path: str = DATABASE_CACHE_PATH):
        Initializes the ImageMatcher with the given image names and database paths.

    find_matched_images(image_path: str, result_num: int = 5) -> list[tuple[str, float]]:
        Finds and returns the top matched images based on ORB descriptors for the given image path.
    """

    db: dbow.Database
    images_names: np.ndarray
    orb: Any

    def __init__(
        self,
        image_names_path: str = IMAGE_NAMES_CACHE_PATH,
        db_path: str = DATABASE_CACHE_PATH,
    ):
        """
        Initializes the ImageMatcher object by loading the image names and pre-trained ORB descriptor database.

        Parameters:
        -----------
        image_names_path : str
            Path to the NumPy file containing image names corresponding to the database.
        db_path : str
            Path to the pre-trained ORB descriptor database.

        Raises:
        -------
        ValueError:
            If the database file is not found at the specified db_path.
        """
        # Load image names
        self.images_names = np.load(image_names_path)

        # Check if the database path exists
        if not os.path.exists(DATABASE_CACHE_PATH):
            raise ValueError("Database doesn't exist")

        # Load the pre-trained ORB descriptor database
        self.db = training.database(db_path)

        # Initialize ORB detector and descriptor extractor
        self.orb = cv2.ORB_create()

    def find_matched_images(
        self, image_path: str, result_num: int = 5
    ) -> list[tuple[str, float]]:
        """
        Finds and returns the top matched images based on ORB descriptors.

        Parameters:
        -----------
        image_path : str
            The path to the input image file that needs to be matched.
        result_num : int, optional
            The number of top matching images to return (default is 5).

        Returns:
        --------
        list of tuples:
            A list of tuples where each tuple contains the matched image name and its similarity score.
        """
        # Read the image
        image = cv2.imread(image_path)

        # Detect keypoints and compute ORB descriptors
        _, descs = self.orb.detectAndCompute(image, None)
        if descs is None:
            return []

        # Convert ORB descriptors to the format required by the dbow library
        descs = [dbow.ORB.from_cv_descriptor(desc) for desc in descs]

        # Query the database for similar images
        scores: list[float] = self.db.query(descs)

        # Sort and select the top 'result_num' matching images based on similarity scores
        top_indices = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )[:result_num]

        # Return a list of matched image names and their corresponding scores
        return [(self.images_names[i], scores[i]) for i in top_indices]

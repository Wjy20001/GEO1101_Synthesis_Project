import os
from typing import Any
import cv2
import dbow
import numpy as np
import training
from const import DATABASE_CACHE_PATH, IMAGE_NAMES_CACHE_PATH
from preview import preview_mached_images


class ImageMatcher:
    """
    A class to match images using ORB descriptors and a pre-trained database.

    Attributes:
    -----------
    db : dbow.Database
        The database containing ORB descriptors.
    image_names : np.ndarray
        An array of image names corresponding to the database entries.
    orb : Any
        The ORB detector and descriptor extractor.

    Methods:
    --------
    __init__(image_names_path: str = IMAGE_NAMES_CACHE_PATH, db_path: str = DATABASE_CACHE_PATH):
        Initializes the ImageMatcher with the given image names and database paths.

    find_matched_images(image_path: str, result_num: int = 5):
        Finds and returns the top matched images for the given image path.
    """

    db: dbow.Database
    images_names: np.ndarray
    orb: Any

    def __init__(
            self,
            image_names_path: str = IMAGE_NAMES_CACHE_PATH,
            db_path: str = DATABASE_CACHE_PATH,
    ):

        self.images_names = np.load(image_names_path)
        if not os.path.exists(db_path):
            raise ValueError(f"Database doesn't exist at {db_path}")
        self.db = training.database(db_path)
        self.orb = cv2.ORB_create()

    def find_matched_images(
            self, image_path: str, result_num: int = 5
    ) -> list[tuple[str, float]]:
        image = cv2.imread(image_path)
        _, descs = self.orb.detectAndCompute(image, None)
        if descs is None:
            return []
        descs = [dbow.ORB.from_cv_descriptor(desc) for desc in descs]
        scores: list[float] = self.db.query(descs)
        top_indices = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )[:result_num]

        return [(self.images_names[i], scores[i]) for i in top_indices]


def get_database_and_image_paths(image_name: str):
    """
    Returns the correct database path and the images directory path based on the image name.

    Parameters:
    -----------
    image_name : str
        The name of the image.

    Returns:
    --------
    tuple[str, str]:
        The paths to the database, image names cache, and image directory for the specific view (front, left, right, top).
    """
    program_dir = os.getcwd()

    # Use the updated folder structure with "images" subdirectory
    if "front" in image_name:
        db_path = os.path.join(program_dir, "data", "front_only", "cache", "database.pickle")
        image_names_path = os.path.join(program_dir, "data", "front_only", "cache", "image_name_index_pairs.npy")
        image_dir = os.path.join(program_dir, "data", "front_only", "images")
    elif "left" in image_name:
        db_path = os.path.join(program_dir, "data", "left_only", "cache", "database.pickle")
        image_names_path = os.path.join(program_dir, "data", "left_only", "cache", "image_name_index_pairs.npy")
        image_dir = os.path.join(program_dir, "data", "left_only", "images")
    elif "right" in image_name:
        db_path = os.path.join(program_dir, "data", "right_only", "cache", "database.pickle")
        image_names_path = os.path.join(program_dir, "data", "right_only", "cache", "image_name_index_pairs.npy")
        image_dir = os.path.join(program_dir, "data", "right_only", "images")
    elif "top" in image_name:
        db_path = os.path.join(program_dir, "data", "top_only", "cache", "database.pickle")
        image_names_path = os.path.join(program_dir, "data", "top_only", "cache", "image_name_index_pairs.npy")
        image_dir = os.path.join(program_dir, "data", "top_only", "images")
    else:
        raise ValueError("Image name must contain 'front', 'left', 'right', or 'top'.")

    # Add debug prints to check the paths
    print(f"Using database path: {db_path}")
    print(f"Using image names path: {image_names_path}")
    print(f"Using images directory: {image_dir}")

    return db_path, image_names_path, image_dir


if __name__ == "__main__":
    user_image_dir = os.path.join(os.getcwd(), "data", "user_images_2")

    # List of user images to match
    user_images = [
        os.path.join(user_image_dir, filename)
        for filename in [
            "image010_front.jpg",
            "image010_left.jpg",
            "image010_right.jpg",
            "image010_top.jpg"
        ]
    ]

    all_images = []

    # Process each image individually
    for image in user_images:
        # Determine the correct database, image names cache, and images directory based on the image name
        db_path, image_names_path, image_dir = get_database_and_image_paths(os.path.basename(image))

        # Initialize the ImageMatcher with the specific database and image names
        image_matcher = ImageMatcher(image_names_path, db_path)

        # Find the top 3 matched images
        matched_images = [
            (os.path.join(image_dir, matched[0]), matched[1])
            for matched in image_matcher.find_matched_images(image, 10)
        ]

        all_images.append((image, matched_images))

    # Preview the matched images
    preview_mached_images(all_images)

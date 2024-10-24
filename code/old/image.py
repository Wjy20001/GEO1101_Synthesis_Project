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
        if not os.path.exists(DATABASE_CACHE_PATH):
            raise ValueError("Database doesn't exist")
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


if __name__ == "__main__":
    user_image_dir = os.path.join(os.getcwd(), "data", "user_images")
    user_images = [
        os.path.join(user_image_dir, filename)
        for filename in [
            "validation_021.jpg",
            "validation_023.jpg",
            "validation_025.jpg",
            "validation_027.jpg",
            "validation_029.jpg",
        ]
    ]
    image_matcher = ImageMatcher(IMAGE_NAMES_CACHE_PATH, DATABASE_CACHE_PATH)
    all_images = [
        (
            image,
            [
                (
                    os.path.join(os.getcwd(), "data", "training", matched[0]),
                    matched[1],
                )
                for matched in image_matcher.find_matched_images(image, 6)
            ],
        )
        for image in user_images
    ]

    preview_mached_images(all_images)

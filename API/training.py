import glob
import os
import time

import cv2
import dbow
import numpy as np
from tqdm import tqdm

from API.const import (DATABASE_CACHE_PATH, IMAGE_NAMES_CACHE_PATH,
                       VOCABULARY_CACHE_PATH)


def training(
    dataset_dir: str = os.path.join("data", "training"),
    cluster_num: int = 10,
    depth: int = 2,
    vocab_path: str = VOCABULARY_CACHE_PATH,
    image_name_path: str = IMAGE_NAMES_CACHE_PATH,
    database_path: str = DATABASE_CACHE_PATH,
) -> None:
    """
    Trains the DBoW (Bag of Words) vocabulary and database on a dataset of images.

    Parameters:
    -----------
    dataset_dir : str, optional
        Directory containing the training images. Default is 'data/training'.
    cluster_num : int, optional
        Number of clusters for vocabulary creation. Default is 10.
    depth : int, optional
        Depth of the vocabulary tree. Default is 2.
    vocab_path : str, optional
        Path to save the trained vocabulary. Default is VOCABULARY_CACHE_PATH.
    image_name_path : str, optional
        Path to save the image names. Default is IMAGE_NAMES_CACHE_PATH.
    database_path : str, optional
        Path to save the trained database. Default is DATABASE_CACHE_PATH.

    Returns:
    --------
    None
    """
    # Initialize the ORB feature extractor
    program_dir = os.getcwd()
    orb = cv2.ORB_create()

    # Define paths to image files (PNG and JPG)
    dataset_dir = os.path.join(program_dir, dataset_dir)
    png_path, jpeg_path = os.path.join(dataset_dir, "*.png"), os.path.join(
        dataset_dir, "*.jpg"
    )

    # Load all image paths from the dataset directory
    image_paths = glob.glob(png_path) + glob.glob(jpeg_path)
    images = []  # List to store the loaded images
    image_names = np.array([])  # Array to store image names

    # Load and append images and their names
    for image_path in tqdm(image_paths, desc="Loading images"):
        images.append(cv2.imread(image_path))
        image_name = os.path.basename(image_path)
        image_names = np.append(image_names, image_name)

    # Create a vocabulary using the DBoW framework
    vocabulary = dbow.Vocabulary(images, cluster_num, depth)

    # Save the vocabulary and image names
    vocabulary.save(vocab_path)
    np.save(image_name_path, image_names)

    # Initialize a database using the created vocabulary
    db = dbow.Database(vocabulary)

    # List to store invalid images (those with no ORB descriptors)
    invalid_images = []

    # Process each image and extract ORB descriptors
    for i, image in tqdm(enumerate(images), desc="Processing images"):
        _, descs = orb.detectAndCompute(image, None)
        if descs is None:
            invalid_images.append(
                image_paths[i]
            )  # Add invalid image to the list
            continue
        # Convert ORB descriptors to DBoW-compatible format
        descs = [dbow.ORB.from_cv_descriptor(desc) for desc in descs]
        db.add(descs)  # Add descriptors to the database

    # Save the created database
    db.save(database_path)


def database(database_path: str) -> dbow.Database:
    """
    Loads a pre-trained DBoW database from the given path. If the database does not exist,
    it trains a new one and then loads it.

    Parameters:
    -----------
    database_path : str
        Path to the DBoW database file.

    Returns:
    --------
    dbow.Database
        The loaded DBoW database.
    """
    if os.path.exists(database_path):
        return dbow.Database.load(database_path)
    else:
        # Train a new database if it doesn't exist
        training()
        return dbow.Database.load(database_path)

import glob
import os
import time

import cv2
from dbow import dbow_sift
import numpy as np
from tqdm import tqdm


def training(
    dataset_dir: str = None,
    cluster_num: int = None,
    depth: int = None,
    overwrite: bool = False
) -> None:
    # Define file paths relative to the dataset directory
    vocab_path = os.path.join(dataset_dir, "vocabulary.pickle")
    image_name_path = os.path.join(dataset_dir, "image_names.npy")
    database_path = os.path.join(dataset_dir, "database.pickle")

    # Check if existing files should be overwritten
    if not overwrite:
        if os.path.exists(vocab_path) and os.path.exists(database_path) and os.path.exists(image_name_path):
            print("Database, vocabulary, and image names already exist. Skipping training.")
            return
        else:
            print("One or more files not found. Proceeding with training.")

    print("===Loading Images===")
    sift = cv2.SIFT_create()  # Use SIFT instead of ORB
    png_path, jpeg_path = os.path.join(dataset_dir, "*.png"), os.path.join(dataset_dir, "*.jpg")
    image_paths = glob.glob(png_path) + glob.glob(jpeg_path)
    images = []
    image_names = np.array([])

    for image_path in tqdm(image_paths, desc="Adding image to images"):
        images.append(cv2.imread(image_path))
        image_name = os.path.basename(image_path)
        image_names = np.append(image_names, image_name)

    vocabulary = dbow_sift.Vocabulary(images, cluster_num, depth)
    print("===Vocabulary has been made===")
    print("===Database is being created===")
    vocabulary.save(vocab_path)
    np.save(image_name_path, image_names)

    db = dbow_sift.Database(vocabulary)
    invalid_images = []
    for i, image in tqdm(enumerate(images), desc="Processing images"):
        _, descs = sift.detectAndCompute(image, None)  # Use SIFT here
        if descs is None:
            invalid_images.append(image_paths[i])
            continue
        descs = [dbow_sift.SIFT.from_cv_descriptor(desc) for desc in descs]  # Changed to SIFT
        db.add(descs)
    db.save(database_path)


if __name__ == "__main__":
    start_time = time.time()  # Start timing
    start_hours, start_rem = divmod(start_time, 3600)
    start_minutes, start_seconds = divmod(start_rem, 60)

    print(f"Training started: {int(start_hours):02}:{int(start_minutes):02}:{int(start_seconds):02}")

    TEST_FOLDER_PATH = os.path.join("data", "latest_scan_flr")
    test_cluster_num: int = 1
    test_depth: int = 1
    overwrite_old_vocab: bool = True  # Set this to control overwriting

    # Run the training and save files directly to the dataset folder
    training(
        dataset_dir=TEST_FOLDER_PATH,
        cluster_num=test_cluster_num,
        depth=test_depth,
        overwrite=overwrite_old_vocab
    )
    
    # Calculate and format elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time
    end_hours, end_rem = divmod(elapsed_time, 3600)
    end_minutes, end_seconds = divmod(end_rem, 60)
    print(f"Elapsed time: {int(end_hours):02}:{int(end_minutes):02}:{int(end_seconds):02}")  # Print in hh:mm:ss

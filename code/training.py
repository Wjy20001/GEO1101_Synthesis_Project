import glob
import os
import time

import cv2
import dbow
import numpy as np
from const import (
    DATABASE_CACHE_PATH,
    IMAGE_NAMES_CACHE_PATH,
    VOCABULARY_CACHE_PATH,
)
from tqdm import tqdm


def training(
    dataset_dir: str = os.path.join("data", "training"),
    cluster_num: int = 10,
    depth=2,
    vocab_path: str = VOCABULARY_CACHE_PATH,
    image_name_path: str = IMAGE_NAMES_CACHE_PATH,
    database_path: str = DATABASE_CACHE_PATH,
) -> None:
    print("===Loading Images===")
    program_dir = os.getcwd()
    orb = cv2.ORB_create()
    dataset_dir = os.path.join(program_dir, dataset_dir)
    png_path, jpeg_path = os.path.join(dataset_dir, "*.png"), os.path.join(
        dataset_dir, "*.jpg"
    )
    image_paths = glob.glob(png_path) + glob.glob(jpeg_path)
    images = []
    image_names = np.array([])
    for image_path in tqdm(image_paths, desc="adding image to images"):
        images.append(cv2.imread(image_path))
        image_name = os.path.basename(image_path)
        image_names = np.append(image_names, image_name)

    vocabulary = dbow.Vocabulary(images, cluster_num, depth)
    print("===Vocabulary has been made===")
    print("===Database is being created===")
    vocabulary.save(vocab_path)
    np.save(image_name_path, image_names)

    db = dbow.Database(vocabulary)
    for image in tqdm(images, desc="Processing images"):
        _, descs = orb.detectAndCompute(image, None)
        descs = [dbow.ORB.from_cv_descriptor(desc) for desc in descs]
        db.add(descs)
    db.save(database_path)


def database(database_path: str) -> dbow.Database:
    if os.path.exists(database_path):
        return dbow.Database.load(database_path)
    else:
        training()
        return dbow.Database.load(database_path)


if __name__ == "__main__":
    start_time = time.time()  # Start timing
    print("training started: ", start_time)
    training()
    # Calculate and format elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time
    hours, rem = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(rem, 60)
    print(
        f"Elapsed time: {int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    )  # Print in hh:mm:ss

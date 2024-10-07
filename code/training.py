import glob
import os
import cv2
import numpy as np

# import numpy as np
# import extract_descriptors
# import perform_kmeans
# import save_bow_vectors
from const import (
    DATABASE_CACHE_PATH,
    IMAGE_NAMES_CACHE_PATH,
    VOCABULARY_CACHE_PATH,
)
import dbow


def training(
    dataset_dir: str = "data/training",
    cluster_num: int = 10,
    depth=2,
    clear_cache: bool = False,
):
    if os.path.exists(DATABASE_CACHE_PATH) and not clear_cache:
        return dbow.Database.load(DATABASE_CACHE_PATH)

    print("Loading Images")
    program_dir = os.getcwd()
    orb = cv2.ORB_create()
    dataset_dir = os.path.join(program_dir, dataset_dir)
    png_path, jpeg_path = os.path.join(dataset_dir, "*.png"), os.path.join(
        dataset_dir, "*.jpg"
    )
    image_paths = glob.glob(png_path) + glob.glob(jpeg_path)
    images = []
    image_names = np.array([])
    for image_path in image_paths:
        images.append(cv2.imread(image_path))
        image_name = os.path.basename(image_path)
        image_names = np.append(image_names, image_name)
    print("image_names: ", image_names)
    vocabulary = dbow.Vocabulary(images, cluster_num, depth)
    print("Vocabulary: ", vocabulary)
    vocabulary.save(VOCABULARY_CACHE_PATH)
    np.save(IMAGE_NAMES_CACHE_PATH, image_names)

    db = dbow.Database(vocabulary)
    for image in images:
        kps, descs = orb.detectAndCompute(image, None)
        descs = [dbow.ORB.from_cv_descriptor(desc) for desc in descs]
        db.add(descs)
    db.save(DATABASE_CACHE_PATH)
    return db


def database():
    if os.path.exists(DATABASE_CACHE_PATH):
        return dbow.Database.load(DATABASE_CACHE_PATH)
    else:
        db = training()
        return db


if __name__ == "__main__":
    training(clear_cache=True)

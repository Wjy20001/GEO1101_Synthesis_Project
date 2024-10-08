import glob
import os

import cv2
import dbow
import numpy as np
import training
from const import IMAGE_NAMES_CACHE_PATH
from preview import preview


def find_matched_images(
    image,
    db: dbow.Database,
    image_name_index_pairs: list[str],
    result_num: int = 10,
) -> list[tuple[str, float]]:
    orb = cv2.ORB_create()
    kps, descs = orb.detectAndCompute(image, None)
    descs = [dbow.ORB.from_cv_descriptor(desc) for desc in descs]
    scores: list[float] = db.query(descs)
    top_indices = sorted(
        range(len(scores)), key=lambda i: scores[i], reverse=True
    )[:result_num]

    return [(image_name_index_pairs[i], scores[i]) for i in top_indices]


def main():
    program_dir = os.getcwd()
    user_images = glob.glob(
        os.path.join(program_dir, "data", "user_images", "*.jpg")
    ) + glob.glob(os.path.join(program_dir, "data", "user_images", "*.png"))
    images = [cv2.imread(image) for image in user_images]
    db = training.training()
    print("db: ", db)
    if db is None:
        print("Database not found")
        return

    cwd = os.getcwd()
    image_names = np.load(IMAGE_NAMES_CACHE_PATH)
    all_images = []
    for i, image in enumerate(images):
        matched_images = find_matched_images(image, db, image_names, 3)
        temp_list: list[tuple[str, float]] = []
        for match in matched_images:
            file_name, score = match
            file_path = os.path.join(cwd, "data", "training", file_name)
            image_score: tuple[str, float] = [file_path, score]
            temp_list.append(image_score)
        all_images.append((image, temp_list))

    preview(all_images)


def match_user_image(user_image_paths: list[str]):
    images = [cv2.imread(image) for image in user_image_paths]
    db = training.training()
    print("db: ", db)
    if db is None:
        print("Database not found")
        return

    cwd = os.getcwd()
    image_names = np.load(IMAGE_NAMES_CACHE_PATH)
    all_images = []
    for i, image in enumerate(images):
        matched_images = find_matched_images(image, db, image_names, 3)
        temp_list: list[tuple[str, float]] = []
        for match in matched_images:
            file_name, score = match
            file_path = os.path.join(cwd, "data", "training", file_name)
            image_score: tuple[str, float] = (file_path, score)
            temp_list.append(image_score)
        all_images.append((image, temp_list))

    preview(all_images)


if __name__ == "__main__":
    # main()
    user_image_dir = os.path.join(os.getcwd(), "data", "user_images")
    user_images = [
        os.path.join(user_image_dir, filename)
        for filename in [
            "validation_001.jpg",
            "validation_002.jpg",
            "validation_003.jpg",
        ]
    ]
    match_user_image(user_images)

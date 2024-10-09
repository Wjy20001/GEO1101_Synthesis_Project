import os

import cv2
import dbow
import numpy as np
import pandas as pd
import training
from const import IMAGE_NAMES_CACHE_PATH


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


def match_user_image(user_image_paths: list[str], db):
    images = [cv2.imread(user_image_paths)]
    cwd = os.getcwd()
    image_names = np.load(IMAGE_NAMES_CACHE_PATH)
    all_images = []

    for i, image in enumerate(images):
        matched_images = find_matched_images(image, db, image_names, 3)
        temp_list: list[tuple[str, float]] = []
        name_list = []

        for match in matched_images:
            file_name, score = match
            name_list.append(file_name)
            file_path = os.path.join(
                os.path.dirname(cwd), "data", "training", file_name
            )
            image_score: tuple[str, float] = (file_path, score)
            temp_list.append(image_score)

        all_images.append((image, temp_list))

    return name_list


def extract_image_mappings(excel_file):
    # Load the excel file and parse the first sheet
    xls = pd.ExcelFile(excel_file)
    df = xls.parse(xls.sheet_names[0])

    # Initialize a dictionary to store image mappings
    image_mappings = {}

    # Iterate through each row in the dataframe
    for index, row in df.iterrows():
        user_image = row["User image name (image you took)"]

        # Gather all ground truth images, ignoring NaN values
        ground_truth_images = (
            row[
                [
                    "Ground Truth (SLAM) image name",
                    "Unnamed: 4",
                    "Unnamed: 5",
                    "Unnamed: 6",
                    "Unnamed: 7",
                ]
            ]
            .dropna()
            .tolist()
        )

        # Map user image to ground truth images
        image_mappings[user_image] = ground_truth_images

    cleaned_mappings = {}

    for key, value in image_mappings.items():
        cleaned_images = [
            image.replace("_left", "")
            .replace("_right", "")
            .replace("_front", "")
            .replace("_bottom", "")
            .replace("_rear", "")
            .replace("_top", "")
            .replace(".png", "")
            .replace(".jpg", "")
            for image in value
        ]
        cleaned_mappings[key] = cleaned_images

    return cleaned_mappings


def process_image(user_image):
    matches = match_user_image(user_image)
    return os.path.basename(user_image), matches


def main():
    # Path to the Excel file
    excel_file = "./data/user_images/Image_matching_validation_sheet.xlsx"

    # Extract the image mappings
    mappings = extract_image_mappings(excel_file)

    # Train the database
    db = training.training()
    print("db: ", db)

    if db is None:
        print("Database not found")
        return

    # Test the setup_database
    user_image_dir = os.path.join(os.getcwd(), "data", "user_images")
    user_images = []

    for filename in os.listdir(user_image_dir):
        if filename.lower().endswith((".jpg", ".png")):
            user_images.append(os.path.join(user_image_dir, filename))

    matched_image_set = {}

    for image_path in user_images:
        np_matched_images = []
        matched_image = match_user_image(image_path, db)
        np_matched_images.append(matched_image)

        matched_images = [
            str(image)
            .replace("_left", "")
            .replace("_right", "")
            .replace("_front", "")
            .replace("_bottom", "")
            .replace("_rear", "")
            .replace("_top", "")
            .replace(".png", "")
            .replace(".jpg", "")
            for sublist in np_matched_images
            for image in sublist
        ]

        matched_image_set[os.path.basename(image_path)] = matched_images

    # print("mappings", mappings)
    # print("matched_image_set", matched_image_set)

    score = 0
    count = 0
    count_error = 0
    for key in matched_image_set.keys():
        matched_images = matched_image_set[key]
        mapped_images = mappings[key]

        # print(matched_images)
        # print(mapped_images)

        intersection = set(matched_images).intersection(set(mapped_images))
        if intersection:
            score += 2
            count += 1
        else:
            count_error += 1

    print(f"Total score: {score}")
    print(f"Number of successful matches: {count}")
    print(
        f"Rate of successful matches: {count/(count + count_error)*100}" + "%"
    )


if __name__ == "__main__":
    main()

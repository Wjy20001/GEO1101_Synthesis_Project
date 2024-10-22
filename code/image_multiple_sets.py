import os
from typing import Any
import cv2
import dbow
import numpy as np
import training
from preview import preview_mached_images


class ImageMatcher:
    db: dbow.Database
    images_names: np.ndarray
    orb: Any

    def __init__(
        self,
        image_names_path: str,
        db_path: str,
    ):
        self.images_names = np.load(image_names_path)
        self.db = training.database(db_path)
        self.orb = cv2.ORB_create()

    def find_matched_images(
        self, image_path: str, result_num: int = 3  # Default to top 3 matches
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


def find_best_matches_in_each_vocabulary(image_path: str, vocab_dir: str, top_n: int = 3):
    all_matches = []

    # Loop over all vocabulary folders and find the best matches in each
    for folder_name in os.listdir(vocab_dir)[:-6]:
        folder_path = os.path.join(vocab_dir, folder_name)
        if os.path.isdir(folder_path):
            vocab_path = os.path.join(folder_path, "vocabulary.pickle")
            image_names_path = os.path.join(folder_path, "image_name_index_pairs.npy")
            database_path = os.path.join(folder_path, "database.pickle")

            if not (os.path.exists(vocab_path) and os.path.exists(image_names_path) and os.path.exists(database_path)):
                continue  # Skip if files do not exist

            print(f"Comparing with vocabulary from folder: {folder_name}")
            matcher = ImageMatcher(image_names_path, database_path)
            matched_images = matcher.find_matched_images(image_path, top_n)

            if matched_images:
                all_matches.append((folder_name, matched_images))  # Store folder name and its top matches

    return all_matches


if __name__ == "__main__":
    user_image_dir = os.path.join(os.getcwd(), "data", "user_images")
    test_image_path = os.path.join("data","training", "p000037_front.jpg")

    # Folder containing the 16 vocabularies
    vocabularies_dir = os.path.join(os.getcwd(), "data", "separate_room_data")

    # Variable for the top N matches to check
    top_n = 5  # Change this value to show the top N matches for each vocabulary

    # Find the top matches in each vocabulary folder
    matches_in_vocabs = find_best_matches_in_each_vocabulary(test_image_path, vocabularies_dir, top_n)

    if matches_in_vocabs:
        preview_data = []
        for folder_name, matches in matches_in_vocabs:
            print(f"Best {top_n} matches from folder {folder_name}:")
            for match in matches:
                print(f"Image: {match[0]}, Score: {match[1]}")
            
            # Prepare data for preview
            preview_data.append(
                (test_image_path, [(os.path.join(vocabularies_dir, folder_name, match[0]), match[1]) for match in matches])
            )

        # Show the preview for each vocabulary folder
        preview_mached_images(preview_data)
    else:
        print("No matches found.")

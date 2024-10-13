import os
import pandas as pd
from image import ImageMatcher
from const import VALIDATION_FILE_PATH, IMAGE_NAMES_CACHE_PATH, DATABASE_CACHE_PATH

def extract_ground_truth_mappings(csv_file):
    """
    Extract ground truth mappings from the CSV file.
    Returns a dictionary where each key is a user image name,
    and the value is a list of ground truth image names.
    """
    df = pd.read_csv(csv_file)
    
    # Create a dictionary to store ground truth mappings
    ground_truth_mappings = {}

    for _, row in df.iterrows():
        user_image = row["User image name (image you took)"]
        # Get all ground truth image names and ignore NaN values
        ground_truth_images = row[[
            "Ground Truth (SLAM) image name",
            "Unnamed: 4",
            "Unnamed: 5",
            "Unnamed: 6",
            "Unnamed: 7"
        ]].dropna().tolist()

        # Ensure all ground truth images have the ".jpg" extension
        ground_truth_images = [img + ".jpg" if not img.endswith(".jpg") else img for img in ground_truth_images]

        ground_truth_mappings[user_image] = ground_truth_images

    return ground_truth_mappings


def calculate_score(matched_images, ground_truth_images):
    """
    Calculate the score based on how many ground truth images
    are in the list of matched images.
    Also returns a list of matched image names.
    """
    score = 0
    matched_image_names = []

    for matched_image, _ in matched_images:
        matched_image_basename = os.path.basename(matched_image)
        matched_image_names.append(matched_image_basename)
        if matched_image_basename in ground_truth_images:
            score += 1

    return score, matched_image_names


def main():
    # Load ground truth mappings from the CSV file
    ground_truth_mappings = extract_ground_truth_mappings(VALIDATION_FILE_PATH)

    # Create an instance of the ImageMatcher
    image_matcher = ImageMatcher(IMAGE_NAMES_CACHE_PATH, DATABASE_CACHE_PATH)

    # List of user images to test
    user_images = [
        "validation_021.jpg",
        "validation_023.jpg",
        "validation_025.jpg",
        "validation_027.jpg",
        "validation_029.jpg"
    ]

    # Path to the user images directory
    user_image_dir = os.path.join(os.getcwd(), "data", "user_images")

    # Iterate through each user image
    for user_image_name in user_images:
        user_image_path = os.path.join(user_image_dir, user_image_name)

        # Find the top n matched images for the current user image
        matched_images = image_matcher.find_matched_images(user_image_path, result_num=5)

        # Get the ground truth images for the current user image
        ground_truth_images = ground_truth_mappings.get(user_image_name, [])

        # Calculate the score based on the matched images
        score, matched_image_names = calculate_score(matched_images, ground_truth_images)

        # Print the detailed result
        print(f"Input image: {user_image_name}")
        print(f"Matched images: {', '.join(matched_image_names)}")
        print(f"Ground Truth images: {', '.join(ground_truth_images)}")
        print(f"Score: {score} points")
        print("-" * 50)


if __name__ == "__main__":
    main()

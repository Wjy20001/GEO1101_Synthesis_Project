import os
import glob
import cv2
import numpy as np
from tqdm import tqdm

def extract_descriptors(image_dir):
    # Initialize ORB detector
    orb = cv2.ORB_create()

    # Collect descriptors from all images in the 'frames' folder (supporting PNG and JPG)
    png_images = glob.glob(f"{image_dir}/*.png")
    jpg_images = glob.glob(f"{image_dir}/*.jpg")
    image_paths = png_images + jpg_images  # Combine PNG and JPG image lists

    if not image_paths:
        print("No images found in the 'frames' directory.")
        return None, None

    all_descriptors = []
    print("Extracting descriptors from images...")
    for image_path in tqdm(image_paths, desc="Processing Images"):
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            continue
        _, descriptors = orb.detectAndCompute(image, None)
        if descriptors is not None:
            all_descriptors.append(descriptors)

    if not all_descriptors:
        print("No valid descriptors found in the dataset.")
        return None, None

    all_descriptors = np.vstack(all_descriptors)
    return all_descriptors, image_paths

if __name__ == "__main__":
    # Example usage (would be handled in `run_setup.py`)
    image_dir = "data/dataset_x/frames"
    descriptors, paths = extract_descriptors(image_dir)

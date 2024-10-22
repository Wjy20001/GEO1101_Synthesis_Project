import glob
import os
import time
import cv2
import dbow
import numpy as np
from tqdm import tqdm

def training(
    dataset_dir: str = None,
    cluster_num: int = None,
    depth: int = None,
    vocab_path: str = None,
    image_name_path: str = None,
    database_path: str = None,
    overwrite: bool = False
) -> None:
    # Check if the files already exist
    if not overwrite and os.path.exists(vocab_path) and os.path.exists(image_name_path) and os.path.exists(database_path):
        print(f"Files already exist for {dataset_dir}, skipping training.")
        return

    print(f"\n===Loading Images from {dataset_dir}===")
    orb = cv2.ORB_create()
    png_path = os.path.join(dataset_dir, "*.png")
    jpeg_path = os.path.join(dataset_dir, "*.jpg")
    image_paths = glob.glob(png_path) + glob.glob(jpeg_path)
    
    images = []
    image_names = np.array([])

    # Load images (without progress bar for clarity)
    for image_path in image_paths:
        images.append(cv2.imread(image_path))
        image_name = os.path.basename(image_path)
        image_names = np.append(image_names, image_name)

    vocabulary = dbow.Vocabulary(images, cluster_num, depth)
    print("\n===Vocabulary has been made===")
    print("===Database is being created===")

    # Save the files
    vocabulary.save(vocab_path)
    np.save(image_name_path, image_names)

    db = dbow.Database(vocabulary)
    invalid_images = []

    # Progress bar for image processing
    for i, image in tqdm(enumerate(images), desc="Processing images", total=len(images)):
        _, descs = orb.detectAndCompute(image, None)
        if descs is None:
            print(f"Warning: No descriptors found for image {image_paths[i]}")
            invalid_images.append(image_paths[i])
            continue
        descs = [dbow.ORB.from_cv_descriptor(desc) for desc in descs]
        db.add(descs)

    db.save(database_path)


def process_multiple_folders(
    parent_folder: str = None,
    cluster_num: int = None,
    depth: int = None,
    overwrite: bool = False
) -> None:
    folder_names = [folder_name for folder_name in os.listdir(parent_folder) if os.path.isdir(os.path.join(parent_folder, folder_name))]

    # Loop through all folders in the parent folder with progress bar
    for folder_name in folder_names[2:]:
        folder_path = os.path.join(parent_folder, folder_name)
        if os.path.isdir(folder_path):
            # Start timing for this folder
            start_time = time.time()

            # Generate unique paths for each folder's outputs
            vocab_path = os.path.join(folder_path, "vocabulary.pickle")
            image_name_path = os.path.join(folder_path, "image_name_index_pairs.npy")
            database_path = os.path.join(folder_path, "database.pickle")
            
            print('-' * 60)
            print(f"\nTraining for folder: {folder_name}")
            training(
                dataset_dir=folder_path,
                cluster_num=cluster_num,
                depth=depth,
                vocab_path=vocab_path,
                image_name_path=image_name_path,
                database_path=database_path,
                overwrite=overwrite,  # Pass the overwrite flag
            )

            # Calculate time taken for this folder
            end_time = time.time()
            elapsed_time = end_time - start_time
            hours, rem = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(rem, 60)
            print(f"Training for {folder_name} completed in {int(hours):02}:{int(minutes):02}:{int(seconds):02} (hh:mm:ss)")


if __name__ == "__main__":
    start_time = time.time()  # Start timing

    # Testing parameters    
    PARENT_FOLDER_PATH = os.path.join("data", "separate_room_data")
    test_cluster_num: int = 150
    test_depth: int = 4
    overwrite_old_vocab: bool = True

    # Set overwrite to True or False based on your requirement
    process_multiple_folders(parent_folder=PARENT_FOLDER_PATH,
                             cluster_num=test_cluster_num,
                             depth=test_depth,
                             overwrite=overwrite_old_vocab)  # Set overwrite=False to skip existing files
    
    # Calculate and format total elapsed time
    end_time = time.time()
    total_elapsed_time = end_time - start_time
    total_hours, total_rem = divmod(total_elapsed_time, 3600)
    total_minutes, total_seconds = divmod(total_rem, 60)
    print(f"Total elapsed time: {int(total_hours):02}:{int(total_minutes):02}:{int(total_seconds):02}")  # Print in hh:mm:ss

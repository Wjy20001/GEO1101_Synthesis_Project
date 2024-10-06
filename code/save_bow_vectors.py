import os

import cv2
import numpy as np
from tqdm import tqdm


def calculate_bow_vector(descriptors, kmeans):
    bow_vector = np.zeros(kmeans.n_clusters, dtype=float)
    if descriptors is not None:
        clusters = kmeans.predict(descriptors)
        np.add.at(bow_vector, clusters, 1)
    return bow_vector


def save_bow_vectors(image_paths, image_dir, kmeans, output_dir):
    print("Calculating BoW vectors for each image...")
    bow_vectors = [
        calculate_bow_vector(
            cv2.ORB_create().detectAndCompute(
                cv2.imread(img, cv2.IMREAD_GRAYSCALE), None
            )[1],
            kmeans,
        )
        for img in tqdm(image_paths, desc="Calculating BoW")
    ]

    # Save BoW vectors and image names (store relative paths)
    relative_image_paths = [
        os.path.relpath(img, image_dir) for img in image_paths
    ]
    np.save(os.path.join(output_dir, "bow_vectors.npy"), bow_vectors)
    np.save(os.path.join(output_dir, "image_names.npy"), relative_image_paths)
    print(f"BoW vectors saved to '{output_dir}/bow_vectors.npy'.")
    print(f"Image names saved to '{output_dir}/image_names.npy'.")


if __name__ == "__main__":
    # Example usage (would be handled in `run_setup.py`)
    image_dir = "data/dataset_x/frames"
    image_paths = np.load("image_paths.npy")
    kmeans_model = np.load("kmeans_model.npy", allow_pickle=True).item()
    save_bow_vectors(image_paths, image_dir, kmeans_model, "data/dataset_x")

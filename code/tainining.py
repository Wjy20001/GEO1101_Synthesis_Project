import argparse
import extract_descriptors
import perform_kmeans
import save_bow_vectors


def training(
    dataset_dir: str = "data/training",
):
    extract_descriptors.extract_descriptors(dataset_dir)
    perform_kmeans.perform_kmeans


if __name__ == "__main__":
    training()

from typing import Any
from matplotlib import pyplot as plt
import cv2
import numpy as np


def preview(images: list[tuple[np.ndarray, list[tuple[str, float]]]]):
    num_sets = len(images)
    # We assume each set has 1 user image + N matched images
    num_cols = max(len(matched_images) + 1 for _, matched_images in images)

    # Calculate the figure size dynamically based on the number of sets and images per set
    plt.figure(figsize=(15, 5 * num_sets))

    for set_idx, (user_image, matched_images) in enumerate(images):
        # Plot the user image in the first column of the current row (set_idx)
        plt.subplot(num_sets, num_cols, set_idx * num_cols + 1)
        plt.imshow(cv2.cvtColor(user_image, cv2.COLOR_BGR2RGB))
        plt.title(f"User Image {set_idx+1}")
        plt.axis("off")

        # Plot the matched images for the current set
        for img_idx, (matched_image_name, score) in enumerate(matched_images):
            matched_image = cv2.imread(matched_image_name)
            if matched_image is None:
                continue
            plt.subplot(num_sets, num_cols, set_idx * num_cols + img_idx + 2)
            plt.imshow(cv2.cvtColor(matched_image, cv2.COLOR_BGR2RGB))
            plt.title(f"Match {img_idx+1}\nScore: {score:.2f}")
            plt.axis("off")

    plt.tight_layout()
    plt.show()

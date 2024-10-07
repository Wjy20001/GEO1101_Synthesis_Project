from matplotlib import pyplot as plt
import cv2


def preview(
    image, matched_images: list[tuple[str, float]]
):  # TODO: add type of image
    plt.figure(figsize=(15, 5))
    num_matched = len(matched_images)
    plt.subplot(1, num_matched + 1, 1)
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title("User Image")
    plt.axis("off")

    # Display the matched images
    for idx in range(num_matched):
        matched_image_name, score = matched_images[idx]
        matched_image = cv2.imread(matched_image_name)
        if matched_image is None:
            continue
        plt.subplot(1, num_matched + 1, idx + 2)
        plt.imshow(cv2.cvtColor(matched_image, cv2.COLOR_BGR2RGB))
        plt.title(f"Match {idx+1}\nScore: {score:.2f}")
        plt.axis("off")

    plt.tight_layout()
    plt.show()

from image import find_matched_images


def benchmark():
    # read spreadsheet of answers

    # Read all user images from directory (50 images)
    images = []
    correct = 0
    incorrect = 0
    for image in images:
        matched = find_matched_images()  # file name and score
        # compare file name is in spreadsheet
        correct += 1
        incorrect += 1
    accuracy = correct / len(images)

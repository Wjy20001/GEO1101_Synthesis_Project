import os
from PIL import Image

# Function to crop an image to square dimensions
def crop_to_square(image):
    width, height = image.size
    # Find the size to crop to (smallest of width or height)
    new_size = min(width, height)

    # Calculate coordinates to crop center square
    left = (width - new_size) / 2
    top = (height - new_size) / 2
    right = (width + new_size) / 2
    bottom = (height + new_size) / 2

    # Crop the image to the square
    return image.crop((left, top, right, bottom))

# Function to process all images in a folder
def crop_images_in_folder(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Process each image in the input folder
    for filename in os.listdir(input_folder):
        # Check if the file is an image (optional: add more image extensions if needed)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
            image_path = os.path.join(input_folder, filename)
            image = Image.open(image_path)

            # Crop the image to a square
            cropped_image = crop_to_square(image)

            # Save the cropped image to the output folder
            output_path = os.path.join(output_folder, filename)
            cropped_image.save(output_path)

            print(f"Cropped and saved: {output_path}")

# Paths to the input folder containing the images and the output folder to save cropped images
input_folder = r'D:\geomatics\geo1101\imagematching4sift\data\front\user_images'
output_folder = r'D:\geomatics\geo1101\imagematching4sift\data\front\user_images\square_images'

# Crop all images in the folder
crop_images_in_folder(input_folder, output_folder)

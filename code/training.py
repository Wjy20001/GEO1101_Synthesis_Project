import os
import pickle
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
# from const import GROUND_TRUTH_PATH, USER_IMAGE_PATH, CACHE_PATH  # Import path variables from const.py

# Extract image features using the VGG16 model
def extract_vgg16_features(image_path, model, transform):
    # Load and process the image, resizing it to VGG16's input size (224x224)
    img = Image.open(image_path).convert('RGB')
    img = transform(img)
    img = img.unsqueeze(0)  # Add batch dimension

    # Extract features
    with torch.no_grad():
        features = model(img)
    
    features = features.flatten().numpy()  # Convert PyTorch tensor to numpy array and flatten
    return features


# Function to preprocess reference images and save features
def preprocess_reference_images(GROUND_TRUTH_PATH, output_file):
    # Load the pretrained VGG16 model and remove the classification layer
    model = models.vgg16(pretrained=True)
    model = torch.nn.Sequential(*list(model.children())[:-1])  # Remove classification layers, keep convolutional layers
    model.eval()  # Set model to evaluation mode

    # Define image transformations
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Create cache folder if it doesn't exist
    # os.makedirs(CACHE_PATH, exist_ok=True)

    # Load reference images and extract VGG16 features
    ref_image_paths = [os.path.join(GROUND_TRUTH_PATH, img) for img in os.listdir(GROUND_TRUTH_PATH)]
    
    ref_vgg16_features = []  # List to store extracted feature vectors

    for image_path in ref_image_paths:
        # Extract VGG16 features
        features = extract_vgg16_features(image_path, model, transform)
        ref_vgg16_features.append(features)

    # Save extracted VGG16 features and image paths to a file
    # output_file = os.path.join(CACHE_PATH, 'reference_vgg16_data.pkl')
    with open(output_file, 'wb') as f:
        pickle.dump((ref_image_paths, ref_vgg16_features), f)

    print(f"Reference images processed and saved to {output_file}")


# Start processing
if __name__ == "__main__":
    ground_truth_path = os.path.join("data", "BK_slam_images")
    output_file = os.path.join("data", "training", "reference_vgg16_data.pkl")

    preprocess_reference_images(ground_truth_path, output_file)

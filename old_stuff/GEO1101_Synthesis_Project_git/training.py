import os
import cv2
import numpy as np
import pickle
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image


# 使用 VGG16 模型提取圖像特徵
def extract_vgg16_features(image_path, model, transform):
    # 加載並處理圖像，調整大小到 VGG16 的輸入大小（224x224）
    img = Image.open(image_path).convert('RGB')
    img = transform(img)
    img = img.unsqueeze(0)  # 增加批次維度

    # 提取特徵
    with torch.no_grad():
        features = model(img)
    
    features = features.flatten().numpy()  # 將 PyTorch 張量轉為 numpy 並展平
    return features


# Function to preprocess reference images and save features
def preprocess_reference_images(reference_folder, dataset, ground_truth, cache_folder):
    # 加載預訓練的 VGG16 模型，並去掉分類層
    model = models.vgg16(pretrained=True)
    model = torch.nn.Sequential(*list(model.children())[:-1])  # 去掉分類層，只保留卷積層
    model.eval()  # 設置為評估模式

    # 定義圖像轉換
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # 創建快取文件夾（如果不存在）
    os.makedirs(cache_folder, exist_ok=True)

    # 加載參考圖像，提取 VGG16 特徵
    ref_image_paths = [os.path.join(reference_folder, dataset, ground_truth, img) for img in
                       os.listdir(os.path.join(reference_folder, dataset, ground_truth))]
    
    ref_vgg16_features = []  # 用於存儲提取的特徵向量

    for image_path in ref_image_paths:
        # 提取 VGG16 特徵
        features = extract_vgg16_features(image_path, model, transform)
        ref_vgg16_features.append(features)

    # 保存提取的 VGG16 特徵和圖像路徑到文件
    output_file = os.path.join(reference_folder, dataset, cache_folder, 'reference_vgg16_data.pkl')
    with open(output_file, 'wb') as f:
        pickle.dump((ref_image_paths, ref_vgg16_features), f)

    print(f"{dataset.capitalize()} reference images processed and saved to {output_file}")


# Paths to the reference folder (ground truth) and cache folder
reference_folder = r'C:\Users\User\Syntehsis\git_for_sift\GEO1101_Synthesis_Project\data\dbow_sift\data'

# Datasets to train (front, left, right, top)
datasets = ['front']

ground_truth = 'ground_truth'
cache_folder = 'cache'

# Train on each dataset and save the results to the cache folder
for dataset in datasets:
    preprocess_reference_images(reference_folder, dataset, ground_truth, cache_folder)

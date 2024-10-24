import os
import numpy as np
import pickle
from scipy.spatial.distance import cosine
import matplotlib.pyplot as plt
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from sklearn.cluster import DBSCAN
import pandas as pd
from const import USER_IMAGE_PATH, CACHE_PATH, GROUND_TRUTH_COORDINATES_PATH, WALL_COORDINATES_PATH  # 引入 WALL_COORDINATES_PATH

# 使用 VGG16 模型提取圖像特徵
def extract_vgg16_features(image_path, model, transform):
    img = Image.open(image_path).convert('RGB')
    img = transform(img)
    img = img.unsqueeze(0)  # 增加批次維度

    # 提取特徵
    with torch.no_grad():
        features = model(img)
    
    features = features.flatten().numpy()  # 將 PyTorch 張量轉為 numpy 並展平
    return features

# Function to display the query image and reference images
def display_results(query_image_path, best_matches):
    num_matches = len(best_matches)
    fig, axes = plt.subplots(1, num_matches + 1, figsize=(15, 5))

    # 顯示查詢影像
    query_image = Image.open(query_image_path).resize((224, 224))
    query_image = np.array(query_image)
    axes[0].imshow(query_image)
    axes[0].set_title("Query Image")
    axes[0].axis('off')

    # 顯示匹配影像
    for i, (dist, ref_image_path) in enumerate(best_matches):
        ref_image = Image.open(ref_image_path).resize((224, 224))
        ref_image = np.array(ref_image)
        axes[i + 1].imshow(ref_image)
        axes[i + 1].set_title(f"Match {i + 1}\nDist: {dist:.2f}")
        axes[i + 1].axis('off')

    plt.tight_layout()
    plt.show()

# Function to extract coordinates from CSV based on matching image name
def extract_coordinates_from_match(ref_image_path, csv_path):
    # 加載 CSV 文件
    coordinates_df = pd.read_csv(csv_path)

    # 提取影像名稱的基礎部分 (去掉 _front, _left 這些後綴)
    base_name = os.path.basename(ref_image_path).split('_')[0] + '.jpg'

    # 查找對應影像的座標
    row = coordinates_df[coordinates_df['Image'] == base_name]
    
    if row.empty:
        print(f"Coordinates not found for image: {base_name}")
        return (0.0, 0.0)  # 如果找不到座標，返回 (0.0, 0.0)
    
    # 提取 X, Y 座標
    x = row['X'].values[0]
    y = row['Y'].values[0]
    return (x, y)

# Perform DBSCAN clustering
def apply_dbscan_to_matches(all_coords, eps=1, min_samples=3):
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(all_coords)
    return labels

# Function to plot DBSCAN clusters along with wall coordinates
def plot_dbscan_results_with_wall(all_coords, labels, wall_coords):
    plt.figure(figsize=(8, 8))
    unique_labels = set(labels)

    # 繪製牆壁座標作為底圖
    wall_coords = np.array(wall_coords)
    plt.scatter(wall_coords[:, 0], wall_coords[:, 1], c='gray', label='Wall', s=5, alpha=0.5)  # 灰色牆壁座標

    # 繪製 DBSCAN 結果
    for label in unique_labels:
        label_coords = [all_coords[i] for i in range(len(all_coords)) if labels[i] == label]
        label_coords = np.array(label_coords)
        if label == -1:
            plt.scatter(label_coords[:, 0], label_coords[:, 1], c='red', label='Outliers', s=20)  # 調整 s 值來改變點的大小
        else:
            plt.scatter(label_coords[:, 0], label_coords[:, 1], label=f'Cluster {label}', s=20)  # 調整 s 值來改變點的大小

    plt.title('DBSCAN Clustering Results with Wall Coordinates')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    plt.grid(True)
    plt.show()

# Load preprocessed reference data and match query images
def match_query_images(query_image_paths, reference_data_file, csv_path, wall_coords_path, top_n_matches=6):
    # 加載 VGG16 模型
    model = models.vgg16(pretrained=True)
    model = torch.nn.Sequential(*list(model.children())[:-1])  # 去掉分類層
    model.eval()

    # 定義圖像轉換
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    all_coords = []  # 用來儲存所有匹配影像的座標

    # 處理每個查詢影像
    for query_image_path in query_image_paths:
        print(f"\nProcessing query image: {query_image_path}")

        # 提取查詢影像的 VGG16 特徵
        query_features = extract_vgg16_features(query_image_path, model, transform)

        # 加載保存的參考數據
        with open(reference_data_file, 'rb') as f:
            ref_image_paths, ref_vgg16_features = pickle.load(f)

        # 比較查詢影像與參考影像的 VGG16 特徵向量
        distances = []
        for i, ref_features in enumerate(ref_vgg16_features):
            distance = cosine(query_features, ref_features)
            distances.append((distance, ref_image_paths[i]))

        # 排序並取得前 N 個最佳匹配
        distances.sort(key=lambda x: x[0])
        best_matches = distances[:top_n_matches]

        # 顯示結果
        display_results(query_image_path, best_matches)

        # 提取每個匹配影像的座標
        for _, ref_image_path in best_matches:
            coords = extract_coordinates_from_match(ref_image_path, csv_path)
            all_coords.append(coords)

    # 加載牆壁座標
    wall_df = pd.read_csv(wall_coords_path)
    wall_coords = wall_df[['x', 'y']].values  # 提取 x, y 座標

    # 對所有匹配影像的座標進行 DBSCAN 聚類
    labels = apply_dbscan_to_matches(all_coords)

    # 視覺化 DBSCAN 聚類結果並繪製牆壁座標
    plot_dbscan_results_with_wall(all_coords, labels, wall_coords)

# Paths to your query folder, reference data file, and wall coordinates file
reference_data_file = os.path.join(CACHE_PATH, 'reference_vgg16_data.pkl')
csv_path = GROUND_TRUTH_COORDINATES_PATH  # 使用 const.py 中定義的座標路徑
wall_coords_path = WALL_COORDINATES_PATH  # 使用牆壁座標的路徑

# 指定查詢影像
selected_query_images = [
    os.path.join(USER_IMAGE_PATH, 'p000061_front.jpg'),
    os.path.join(USER_IMAGE_PATH, 'p000061_left.jpg'),
    os.path.join(USER_IMAGE_PATH, 'p000061_top.jpg'),
    os.path.join(USER_IMAGE_PATH, 'p000061_right.jpg')
]

# 匹配查詢影像並進行聚類與視覺化
match_query_images(selected_query_images, reference_data_file, csv_path, wall_coords_path, top_n_matches=6)

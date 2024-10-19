import os
import numpy as np
import pickle
from scipy.spatial.distance import cosine
import matplotlib.pyplot as plt
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image


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
    # 設定圖像的數量
    num_matches = len(best_matches)

    # 創建一個 1 行 (num_matches + 1) 列的子圖網格
    fig, axes = plt.subplots(1, num_matches + 1, figsize=(15, 5))

    # 加載查詢圖像
    query_image = Image.open(query_image_path).resize((224, 224))
    query_image = np.array(query_image)

    # 在第 1 個子圖中顯示查詢圖像
    axes[0].imshow(query_image)
    axes[0].set_title("Query Image")
    axes[0].axis('off')

    # 加載並顯示每個匹配的參考圖像
    for i, (dist, ref_image_path) in enumerate(best_matches):
        ref_image = Image.open(ref_image_path).resize((224, 224))
        ref_image = np.array(ref_image)

        # 顯示參考圖像
        axes[i + 1].imshow(ref_image)
        axes[i + 1].set_title(f"Match {i + 1}\nDist: {dist:.2f}")
        axes[i + 1].axis('off')

    # 顯示所有圖像在一個窗口
    plt.tight_layout()
    plt.show()


# Load preprocessed reference data and match query images
def match_query_images(query_image_paths, reference_data_file, top_n_matches=5):
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

    # 加載保存的參考數據
    with open(reference_data_file, 'rb') as f:
        ref_image_paths, ref_vgg16_features = pickle.load(f)

    # 處理查詢影像
    for query_image_path in query_image_paths:
        print(f"\nProcessing query image: {query_image_path}")

        # 提取查詢影像的 VGG16 特徵
        query_features = extract_vgg16_features(query_image_path, model, transform)

        # 比較查詢影像與參考影像的 VGG16 特徵向量
        distances = []
        for i, ref_features in enumerate(ref_vgg16_features):
            distance = cosine(query_features, ref_features)  # 使用餘弦距離
            distances.append((distance, ref_image_paths[i]))

        # 排序並取得前 N 個最佳匹配
        distances.sort(key=lambda x: x[0])
        best_matches = distances[:top_n_matches]

        # 顯示結果
        display_results(query_image_path, best_matches)


# Paths to your query folder and reference data file
query_folder = r'C:\Users\User\Syntehsis\git_for_sift\GEO1101_Synthesis_Project\data\user_images'
reference_data_file = r'C:\Users\User\Syntehsis\git_for_sift\GEO1101_Synthesis_Project\data\dbow_sift\data\front\cache\reference_vgg16_data.pkl'

# Manually specify the query images
selected_query_images = [
    os.path.join(query_folder, 'p000126_front.jpg'),
    os.path.join(query_folder, 'image001_front.jpg'),
    os.path.join(query_folder, 'image002_front.jpg'),
    os.path.join(query_folder, 'image003_front.jpg')
]

# Match the query images against the preprocessed reference data and display the results
match_query_images(selected_query_images, reference_data_file, top_n_matches=5)

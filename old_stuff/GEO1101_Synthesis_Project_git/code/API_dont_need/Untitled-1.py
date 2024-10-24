import pickle
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
from const import USER_IMAGE_PATH, CACHE_PATH, GROUND_TRUTH_PATH, WALL_COORDINATES_PATH
from scipy.spatial import KDTree

# 指定 .pkl 檔案的路徑
pkl_file_path = 'C:/Users/User/Syntehsis/CNN/GEO1101_Synthesis_Project/data/training/cache/reference_vgg16_data.pkl'

# 讀取並打印 .pkl 檔案的內容
with open(pkl_file_path, 'rb') as file:
    data = pickle.load(file)

# data 是一個 tuple，包含 (ref_image_paths, ref_vgg16_features)
ref_image_paths, ref_vgg16_features = data

# 打印影像路徑和對應的 VGG16 特徵
print("Reference Image Paths:")
for path in ref_image_paths:
    print(path)


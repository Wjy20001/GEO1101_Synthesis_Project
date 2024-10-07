import os

program_dir = os.getcwd()

# === Not sure if these are needed === #
# IMAGES_CACHE_PATHS = os.path.join(program_dir, "data/cache/image_paths.npy")
# DESCRIPTOR_CACHE_PATH = os.path.join(
#     program_dir, "data/cache/descriptors.npy"
# )
# KMEANS_CACHE_PATH = os.path.join(program_dir, "data/cache/kmeans.npy")
# BOW_CACHE_PATH = os.path.join(program_dir, "data/cache/bow.npy")
# =======================================

VOCABULARY_CACHE_PATH = os.path.join(
    program_dir, "data", "cache", "vocabulary.pickle"
)
DATABASE_CACHE_PATH = os.path.join(program_dir, "data", "cache", "database.pickle")
IMAGE_NAMES_CACHE_PATH = os.path.join(
    program_dir, "data", "cache", "image_name_index_pairs.npy"
)

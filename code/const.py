import os

program_dir = os.getcwd()

# TODO: change this file so we can train subset of training set
# training_set = "left_only"


VOCABULARY_CACHE_PATH = os.path.join(
    program_dir, "data", "cache", "vocabulary.pickle"
)
DATABASE_CACHE_PATH = os.path.join(
    program_dir, "data", "cache", "database.pickle"
)
IMAGE_NAMES_CACHE_PATH = os.path.join(
    program_dir, "data", "cache", "image_name_index_pairs.npy"
)

GROUND_TRUTH_PATH = os.path.join(
    program_dir, "data", "csvs", "slam_camera_coordinates.csv"
)

WALL_COORDINATES_PATH = os.path.join(
    program_dir, "data", "csvs", "BK_wall_coordinates.csv"
)

VALIDATION_FILE_PATH = os.path.join(
    program_dir, "data", "csvs", "manual_validation.csv"
)

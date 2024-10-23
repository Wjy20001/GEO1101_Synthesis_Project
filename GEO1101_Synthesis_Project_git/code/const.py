import os

program_dir = os.getcwd()


GROUND_TRUTH_PATH = os.path.join(
    program_dir, "data", "training", "ground_truth"
)
USER_IMAGE_PATH = os.path.join(
    program_dir, "data", "training", "user_images" 
)

CACHE_PATH = os.path.join(
    program_dir, "data", "training", "cache", 
)

WALL_COORDINATES_PATH= os.path.join(
    program_dir, "data", "csvs", "BK_wall_coordinates.csv", 
)

GROUND_TRUTH_COORDINATES_PATH= os.path.join(
    program_dir, "data", "csvs", "slam_camera_coordinates_take2_realworld.csv", 
)
import os

program_dir = os.getcwd()

# VOCABULARY_CACHE_PATH = os.path.join(
#     program_dir, "data", "cache", "vocabulary.pickle"
# )
# DATABASE_CACHE_PATH = os.path.join(
#     program_dir, "data", "cache", "database.pickle"
# )
# IMAGE_NAMES_CACHE_PATH = os.path.join(
#     program_dir, "data", "cache", "image_name_index_pairs.npy"
# )

GROUND_TRUTH_PATH = os.path.join(
    program_dir, "data", "csvs", "slam_camera_coordinates.csv"
)

WALL_COORDINATES_PATH = os.path.join(
    program_dir, "data", "csvs", "BK_wall_coordinates.csv"
)

VALIDATION_FILE_PATH = os.path.join(
    program_dir, "data", "csvs", "manual_validation.csv"
)

BUILDING_EDGE_PATH = os.path.join(
    program_dir, "data", "routing", "boundary.geojson"
)

NODES_PATH = os.path.join(
    program_dir, "data", "routing", "nodes.geojson"
)

ROOMS_PATH = os.path.join(
    program_dir, "data", "routing", "rooms.geojson"
)

ROUTING_PATH = os.path.join(
    program_dir, "data", "routing", "routing.geojson"
)

API_FOLDER_PATH = os.path.join(
    program_dir, "API"
)
# USER_IMAGE_PATH = os.path.join("data")
# CACHE_PATH = os.path.join()
# GROUND_TRUTH_COORDINATES_PATH = os.path.join()
# WALL_COORDINATES_PATH = os.path.join()

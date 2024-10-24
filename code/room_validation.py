import pandas as pd
import os
import convertcoordinate as cc
from pyproj import Transformer

from point_in_polygon import point_in_polygon 
from module_matching_local import match_query_images_and_get_center



def get_room_name(img_name: str, floorplan_json_path: str) -> str:
    img_full_path: str = os.path.join(user_image_folder, img_name)
    
    #needs to be in list else matching breaks
    img_to_test = [img_full_path]
    print('-' * 60)
    print(f'retrieving coordinates for {img_to_test}')
    center_coords = match_query_images_and_get_center(img_to_test, reference_data_file, csv_path_coord, top_n_matches=6, min_DBSCAN_samples=1)

    print(f'found coordinate:\t\t{center_coords}')
    center_coords = cc.convert_coordinates(center_coords)
    print(f'CRS conversion yields:\t\t{center_coords}')


    room: str = point_in_polygon(center_coords, floorplan_json_path)
    print(f'found room:\t\t\t{room}')
    return room if room else ''


def print_statistics(df: pd.DataFrame) -> None: 
    validate: pd.Series = df['true_room'] == df['found_room']
    correct_match_count: int = validate.sum()
    df_length: int = len(df)
    matched_percentage: float = validate.mean() * 100  

    stats_report: str = (f"Total test user images used:\t{df_length}\n"
                         f"Correctly matched rooms:\t{correct_match_count}\n"
                         f"Room match percentage:\t\t{matched_percentage:.2f}%")

    print("=" * 40)
    print(stats_report)
    print("=" * 40)
    

if __name__ == "__main__":
    #define paths
    
    csv_path_validation: str = os.path.join("data", "csvs", "room_validation_linkage.csv")
    user_image_folder: str = os.path.join("data", "user_images")
    rooms_json_path: str = os.path.join("data", "floorplans", "BK_floorplan_latlong.geojson")

    reference_data_file: str = os.path.join("data", "training", 'reference_vgg16_data.pkl')
    csv_path_coord: str = os.path.join("data", "csvs", "slam_camera_coordinates_merged.csv")
    user_image_folder: str = os.path.join("data", "user_images")

    #disable a warning message for debugging
    os.environ["LOKY_MAX_CPU_COUNT"] = "4"

    # get validation data as dataframe
    df_full: pd.DataFrame = pd.read_csv(csv_path_validation, dtype=pd.StringDtype())

    #again disable warnings so i can do 3 rows only for time management
    # df = df_full.head(1).copy()
    # df.loc[:, 'found_room'] = df.loc[:,'user_image_name'].apply(lambda x: get_room_name(x, rooms_json_path))
    # df.loc[:, 'found_room'] = df.loc[:,'found_room'].astype(pd.StringDtype())

    #uncomment below when ready!!!!!!

    # Apply the function to the 'user_image_name' column
    df_full['found_room'] = df_full['user_image_name'].apply(lambda x: get_room_name(x, rooms_json_path))
    df_full['found_room'] = df_full['found_room'].astype(pd.StringDtype())

    print_statistics(df_full)
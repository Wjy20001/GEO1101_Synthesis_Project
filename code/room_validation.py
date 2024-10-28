import pandas as pd
import os
import convertcoordinate as cc
from pyproj import Transformer

from point_in_polygon import point_in_polygon 
from module_matching_local import match_query_images_and_get_center



def get_room_name(img_names: str | list, floorplan_json_path: str, top_n_matches: int =6, min_DBSCAN_samples: int = 3) -> str:
    print('-' * 60)
    print(f'retrieving coordinates for {img_names}')
    print('-' * 30)
    if isinstance(img_names, str):
        img_full_path: str = os.path.join(user_image_folder, img_names)
        #needs to be in list else matching breaks
        img_to_test = [img_full_path]
        
        center_coords = match_query_images_and_get_center(img_to_test, reference_data_file, csv_path_coord, top_n_matches=top_n_matches, min_DBSCAN_samples=1)
    
    elif isinstance(img_names, list):
        img_to_test = [os.path.join(user_image_folder, img_name) for img_name in img_names]
        center_coords = match_query_images_and_get_center(img_to_test, reference_data_file, csv_path_coord, top_n_matches=top_n_matches, min_DBSCAN_samples=min_DBSCAN_samples)

    else:
        raise TypeError

    print('-' * 30)
    print(f'found coordinate:\t\t{center_coords}')
    center_coords = cc.convert_coordinates(center_coords)
    print(f'CRS conversion yields:\t\t{center_coords}')


    room: str = point_in_polygon(center_coords, floorplan_json_path)
    print(f'found room:\t\t\t{room}')
    return room if room else ''


def print_statistics(df: pd.DataFrame, toggle: bool) -> None: 
    validate: pd.Series = df['true_room'] == df['found_room']
    correct_match_count: int = validate.sum()
    df_length: int = len(df)
    matched_percentage: float = validate.mean() * 100  

    if toggle:
        stats_report: str = (f"Total test user images used:\t{df_length}\n"
                            f"Correctly matched rooms:\t{correct_match_count}\n"
                            f"Room match percentage:\t\t{matched_percentage:.2f}%")
    else:
        stats_report: str = (f"Total test user positions:\t{df_length}\n"
                            f"Correctly matched rooms:\t{correct_match_count}\n"
                            f"Room match percentage:\t\t{matched_percentage:.2f}%")
        
    print("=" * 40)
    print(stats_report)
    print("=" * 40)

    # Filter for mismatches and print details if any
    mismatches = df[~validate]
    if not mismatches.empty:
        print("Mismatched Entries:")
        for _, row in mismatches.iterrows():
            print(f"Position ID: {row['position_id']}\tTrue Room: {row['true_room']}\tFound Room: {row['found_room']}\timage_names: {row['user_image_name']}")
    else:
        print("All entries matched correctly.")

if __name__ == "__main__":
    #define paths
    
    csv_path_validation: str = os.path.join("data", "csvs", "image_validation_linkage.csv")
    rooms_json_path: str = os.path.join("API", "data", "floorplan.geojson")

    reference_data_file: str = os.path.join("data", "training", 'model.pkl')
    csv_path_coord: str = os.path.join("data", "csvs", "slam_camera_coordinates_merged_v2.csv")
    user_image_folder: str = os.path.join("data", "user_images")

    #disable a warning message for debugging
    os.environ["LOKY_MAX_CPU_COUNT"] = "4"

    # get validation data as dataframe
    df_full: pd.DataFrame = pd.read_csv(csv_path_validation, dtype=pd.StringDtype())

    df_full['position_id'] = df_full['position_id'].astype(int)

    # single image matching = True
    # multiple image matching = False
    diagnostics_toggle = False

    # (DBSCAN) parameters
    N_best_matches: int = 5 #default=6 
    min_DBSCAN_samples: int = 2 #default=3


    if diagnostics_toggle:
        # Apply the function to the 'user_image_name' column
        df_full['found_room'] = df_full['user_image_name'].apply(lambda x: get_room_name(x, rooms_json_path, top_n_matches=N_best_matches))
        df_full['found_room'] = df_full['found_room'].astype(pd.StringDtype())

        print_statistics(df_full, toggle=diagnostics_toggle)
    
    else:
        #below we group by room so we can input 2 or more images for matching results

        #group by position id to get image set for every position
        grouped_df = df_full.groupby('position_id').agg({'user_image_name': list,     #list the images for a single user position      
                                                    'true_room': 'first' #because it will be equal for every image with same position_id
                                                    }).reset_index()

        #filter out positions that have one single image (just to be sure!)
        filtered_df = grouped_df[grouped_df['user_image_name'].apply(len) >= 2].copy()

        filtered_df['found_room'] = filtered_df['user_image_name'].apply(lambda x: get_room_name(x, rooms_json_path, top_n_matches=N_best_matches, 
                                                                                                 min_DBSCAN_samples=min_DBSCAN_samples))
        filtered_df['found_room'] = filtered_df['found_room'].astype(pd.StringDtype())

        
        print_statistics(filtered_df, toggle=diagnostics_toggle)


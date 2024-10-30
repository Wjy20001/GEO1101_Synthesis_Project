import pandas as pd
import os
import time  # Import time for timing calculations
import convertcoordinate as cc
from pyproj import Transformer
from tqdm import tqdm

from point_in_polygon import point_in_polygon
from module_matching_local import match_query_images_and_get_center

def get_room_name_and_time(img_names: str | list, floorplan_json_path: str, top_n_matches: int = 6, min_DBSCAN_samples: int = 3):
    start_time = time.time()
    # print('-' * 60)
    if isinstance(img_names, str):
        img_full_path: str = os.path.join(user_image_folder, img_names)
        img_to_test = [img_full_path]
        center_coords = match_query_images_and_get_center(img_to_test, reference_data_file, csv_path_coord, top_n_matches=top_n_matches, min_DBSCAN_samples=1)
    
    elif isinstance(img_names, list):
        img_to_test = [os.path.join(user_image_folder, img_name) for img_name in img_names]
        center_coords = match_query_images_and_get_center(img_to_test, reference_data_file, csv_path_coord, top_n_matches=top_n_matches, min_DBSCAN_samples=min_DBSCAN_samples)
    else:
        raise TypeError

    center_coords = cc.convert_coordinates(center_coords)
    room: str = point_in_polygon(center_coords, floorplan_json_path)
    # print(f'CRS conversion yields =\t{center_coords}')
    # print(f'found room =\t\t\t{room}')

    calculation_time = time.time() - start_time
    return room if room else '', calculation_time


def print_statistics(df: pd.DataFrame, toggle: bool, save_path: str = None) -> None:
    validate: pd.Series = df['true_room'] == df['found_room']
    correct_match_count: int = validate.sum()
    df_length: int = len(df)
    matched_percentage: float = validate.mean() * 100

    stats_report = (f"Total test user {'images' if toggle else 'positions'} used:\t{df_length}\n"
                    f"Correctly matched rooms:\t{correct_match_count}\n"
                    f"Room match percentage:\t\t{matched_percentage:.2f}%")
    
    print("=" * 40)
    print(stats_report)
    print("=" * 40)

    mismatches = df[~validate]
    if not mismatches.empty:
        print("Mismatched Entries:")
        for _, row in mismatches.iterrows():
            print(f"Position ID: {row['position_id']}\tTrue Room: {row['true_room']}\tFound Room: {row['found_room']}\timage_names: {row['user_image_name']}")
    else:
        print("All entries matched correctly.")

    # Save the diagnostics to a CSV if a path is provided
    if save_path:
        df.to_csv(save_path, index=False)
        print(f"Diagnostics saved to {save_path}")


if __name__ == "__main__":
    # Define paths
    #get latest version from API/data
    rooms_json_path = os.path.join("API", "data", "floorplan.geojson")
    reference_data_file = os.path.join("API", "data", 'model.pkl')
    csv_path_coord = os.path.join("API", "data", "slam_coordinates.csv")

    #get sample images and linkage from data/
    user_image_folder = os.path.join("data", "user_images")
    csv_path_validation = os.path.join("data", "csvs", "image_validation_linkage.csv")
    

    os.environ["LOKY_MAX_CPU_COUNT"] = "4"

    df_full = pd.read_csv(csv_path_validation, dtype=pd.StringDtype())
    df_full['position_id'] = df_full['position_id'].astype(int)


    diagnostics_toggle = 'single'   # 'single' or 'multi'
    N_best_matches = 1 #default = 6
    cluster_size = 1 #default = 3

    # for cluster_size in tqdm(range(1, 6), desc='cluster_size'):
    #define how to save diagnostics
    diagnostics_csv_path = os.path.join("data", "diagnostics", f"diagnostics_{diagnostics_toggle}_N={N_best_matches}_cs={cluster_size}.csv")
    
    if diagnostics_toggle == 'single':
        # For individual images
        df_full[['found_room', 'calculation_time']] = df_full['user_image_name'].apply(
            lambda x: get_room_name_and_time(x, rooms_json_path, N_best_matches, cluster_size)
        ).apply(pd.Series)

        print_statistics(df_full, toggle=diagnostics_toggle, save_path=diagnostics_csv_path)
    
    elif diagnostics_toggle == 'multi':

        # For grouped images
        grouped_df = df_full.groupby('position_id').agg({
            'user_image_name': list, 'true_room': 'first'
        }).reset_index()

        filtered_df = grouped_df[grouped_df['user_image_name'].apply(len) >= 2].copy()

        filtered_df[['found_room', 'calculation_time']] = filtered_df['user_image_name'].apply(
            lambda x: get_room_name_and_time(x, rooms_json_path, N_best_matches, cluster_size)
        ).apply(pd.Series)

        print_statistics(filtered_df, toggle=diagnostics_toggle, save_path=diagnostics_csv_path)

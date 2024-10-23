import pandas as pd
import os

from point_in_polygon import point_in_polygon  # Assuming you need this function later

def get_room_name(img_name: str) -> str:
    img_full_path: str = os.path.join(user_image_folder, img_name)
    
    img_coordinate: tuple[float, float] = (4.0, 4.0) #replace by function 

    room: str = point_in_polygon(*img_coordinate, floorplan_json_path)

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
    csv_path: str = os.path.join("data", "room_validation", "room_validation_linkage.csv")
    user_image_folder: str = os.path.join("data", "room_validation", "user_images")
    floorplan_json_path: str = os.path.join("data", "room_validation", "test_floorplan.geojson")

    # get validation data as dataframe
    df: pd.DataFrame = pd.read_csv(csv_path, dtype=pd.StringDtype())

    # Apply the function to the 'user_image_name' column
    df['found_room'] = df['user_image_name'].apply(get_room_name)
    df['found_room'] = df['found_room'].astype(pd.StringDtype())

    print_statistics(df)
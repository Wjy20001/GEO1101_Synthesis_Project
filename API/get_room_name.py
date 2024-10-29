import os

from pyproj import Transformer
from shapely.geometry import Point
import geopandas as gpd


from API.CNN import match_query_images_and_get_center

# define standard CRS transformer 28992 -> 4326
CRS28992_4326 = Transformer.from_crs(
    "EPSG:28992", "EPSG:4326", always_xy=True
)


# Function to convert coordinates from EPSG:28992 to WGS84 using Transformer
def convert_coordinates(coordinates, transformer=CRS28992_4326):

    if isinstance(
        coordinates[0], list
    ):  # Check if it's a list of coordinates (for LineString or Polygon)
        return [
            convert_coordinates(coord, transformer) for coord in coordinates
        ]
    else:  # If it's a single point
        # Transform the coordinates from EPSG:28992 (x, y) to EPSG:4326 (longitude, latitude)
        return transformer.transform(
            coordinates[0], coordinates[1]
        )  # Use (x, y) order for EPSG:28992 to EPSG:4326


def point_in_polygon(point: tuple[float, float], geojson_file_path: str):

    x, y = point
    # Validate input types
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        raise ValueError("Coordinates x and y must be numeric.")

    if not os.path.exists(geojson_file_path):
        raise FileNotFoundError(
            f"GeoJSON file '{geojson_file_path}' not found."
        )

    # Read GeoJSON file into GeoDataFrame and transform to Dutch coordinate system (EPSG:28992)
    gdf = gpd.read_file(geojson_file_path)
    gdf = gdf.to_crs("EPSG:28992")

    # Create point geometry
    point = Point(x, y)

    # Find polygon containing point
    contains_point = gdf.contains(point)
    if contains_point.any():
        return gdf.loc[contains_point, "room"].iloc[0]

    return ""  # The point is not inside any polygon --> so empty string for dataframes


def get_room_name(
    img_names: str | list,
    floorplan_json_path: str,
    ref_vgg16_features: list,
    ref_image_paths: list,
    slam_csv_path: str,
    top_n_matches: int = 6,
    min_DBSCAN_samples: int = 3,
) -> tuple[str, tuple[float, float]]:

    print(f"retrieving coordinates for {len(img_names)} user images")
    print("-" * 30)

    print("ref image paths:", ref_image_paths)

    if isinstance(img_names, str):
        # needs to be in list else matching breaks
        img_names = [img_names]

        center_coords = match_query_images_and_get_center(
            img_names,
            ref_vgg16_features,
            ref_image_paths,
            slam_csv_path,
            top_n_matches=top_n_matches,
            min_DBSCAN_samples=1,
        )

    elif isinstance(img_names, list):

        center_coords = match_query_images_and_get_center(
            img_names,
            ref_vgg16_features,
            ref_image_paths,
            slam_csv_path,
            top_n_matches=top_n_matches,
            min_DBSCAN_samples=min_DBSCAN_samples,
        )

    else:
        raise TypeError

    print("-" * 30)
    print(f"center_coords:\t\t{center_coords}")
    user_coordinate_latlng = convert_coordinates(center_coords)
    print(f"CRS conversion yields:\t\t{user_coordinate_latlng}")

    room = point_in_polygon(center_coords, floorplan_json_path)
    print(f"found room:\t\t\t{room}")

    return room, user_coordinate_latlng if room else tuple([None, None])


def get_file_paths(folder_path, extension="", images=False):
    if extension == "geojson":
        # Find all GeoJSON files
        geojson_files = [
            os.path.join(folder_path, filename)
            for filename in os.listdir(folder_path)
            if filename.lower().endswith(".geojson")
        ]

        # Separate 'floorplan' and 'node' files if they exist
        floorplan_file = next(
            (file for file in geojson_files if "floorplan" in file.lower()),
            None,
        )
        node_file = next(
            (file for file in geojson_files if "nodes" in file.lower()), None
        )

        if not floorplan_file or not node_file:
            raise FileNotFoundError(
                "Required 'floorplan' or 'node' geojson file is missing."
            )

        return (floorplan_file, node_file)

    elif extension == "csv":
        # Find the CSV file
        csv_files = [
            os.path.join(folder_path, filename)
            for filename in os.listdir(folder_path)
            if filename.lower().endswith(".csv")
        ]

        if len(csv_files) == 1:
            return csv_files[0]
        elif len(csv_files) == 0:
            raise FileNotFoundError("No CSV file found in the folder.")
        else:
            raise ValueError("Multiple CSV files found. Only one expected.")

    elif extension == "pkl":
        # Find the pickle file
        csv_files = [
            os.path.join(folder_path, filename)
            for filename in os.listdir(folder_path)
            if filename.lower().endswith(".pkl")
        ]

        if len(csv_files) == 1:
            return csv_files[0]
        elif len(csv_files) == 0:
            raise FileNotFoundError("No pkl file found in the folder.")
        else:
            raise ValueError("Multiple pkl files found. Only one expected.")

    elif images:
        # Find all image files with specified extensions
        image_files = [
            os.path.join(folder_path, filename)
            for filename in os.listdir(folder_path)
            if filename.lower().endswith(("jpg", "jpeg", "png"))
        ]

        if not image_files:
            raise FileNotFoundError(
                "No image files (jpg, jpeg, png) found in the folder."
            )

        return image_files

    else:
        raise ValueError(
            "Unsupported file extension. Only 'geojson', 'csv', 'jpg', 'jpeg', and 'png' are supported."
        )


if __name__ == "__main__":
    user_img_path = os.path.join("API", "input_images")
    data_path = os.path.join("API", "data")

    img_names: list = get_file_paths(user_img_path, images=True)
    floorplan_json_path, _ = get_file_paths(data_path, extension="geojson")
    trained_model_path: str = get_file_paths(data_path, extension="pkl")
    slam_csv_path: str = get_file_paths(data_path, extension="csv")

    room_name = get_room_name(
        img_names, floorplan_json_path, trained_model_path, slam_csv_path
    )
    print(room_name)

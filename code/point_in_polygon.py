import json
from shapely.geometry import shape, Point
import os
import convertcoordinate as cc

def point_in_polygon(point: tuple[float, float], geojson_file_path:str):
    x, y = point
    # Validate input types
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        raise ValueError("Coordinates x and y must be numeric.")
    
    if not os.path.exists(geojson_file_path):
        raise FileNotFoundError(f"GeoJSON file '{geojson_file_path}' not found.")
    
    try:
        with open(geojson_file_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid GeoJSON file format: {e}")

    # Validate the GeoJSON structure
    if 'features' not in data or not isinstance(data['features'], list):
        raise ValueError("GeoJSON file must contain a 'features' list.")

    # Create a Shapely Point object for the input coordinates
    point = Point(x, y)
    
    # Iterate over the features (polygons) in the GeoJSON file
    for feature in data['features']:
        if 'geometry' not in feature or not feature['geometry']:
            continue  # Skip invalid geometries

        geometry = shape(feature['geometry'])
        
        # Check if the point is within the polygon
        if geometry.contains(point):
            return feature['properties'].get('room', 'Unnamed Polygon')  # Return polygon name or a default

    return None  # The point is not inside any polygon


if __name__ == "__main__":
    # Example usage
    #coordinate of BK in EPSG:28992 for testing purposes
    test_eastwing = (85224.66,446928.80)
    test_westwing = (85138.73,446829.61)
    test_central = (85207.94,446863.64)
    orange = (85225.31, 446915.81)
    test_coord = orange

    #convert to latlong
    test_coord = cc.convert_coordinates(test_coord)
    geojson_file = os.path.join('data', 'room_validation', 'BK_rooms_latlong.geojson')

    try:
        resulting_room = point_in_polygon(test_coord, geojson_file)
        if resulting_room:
            print(f"The point {tuple(test_coord)} is inside {resulting_room}.")
        else:
            print(f"The point {tuple(test_coord)} is outside any of the polygons in {geojson_file}.")
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")

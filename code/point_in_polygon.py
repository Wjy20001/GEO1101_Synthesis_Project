import json
from shapely.geometry import shape, Point
import os

def point_in_polygon(x, y, geojson_file):
    # Validate input types
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        raise ValueError("Coordinates x and y must be numeric.")
    
    if not os.path.exists(geojson_file):
        raise FileNotFoundError(f"GeoJSON file '{geojson_file}' not found.")
    
    try:
        with open(geojson_file) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid GeoJSON file format: {e}")

    # Validate the GeoJSON structure
    if 'features' not in data or not isinstance(data['features'], list):
        raise ValueError("GeoJSON file must contain a 'features' list.")

    # Create a Shapely Point object for the input coordinates
    point = Point(x, y)

    # Iterate over the features (polygons) in the GeoJSON file
    for polygon in data['features']:
        if 'geometry' not in polygon or not polygon['geometry']:
            continue  # Skip invalid geometries

        geometry = shape(polygon['geometry'])
        
        # Check if the point is within the polygon
        if geometry.contains(point):
            return polygon['properties'].get('name', 'Unnamed Polygon')  # Return polygon name or a default

    return None  # The point is not inside any polygon


if __name__ == "__main__":
    # Example usage
    x, y = 5.0, 4.0
    geojson_file = os.path.join('data', 'room_validation', 'test_floorplan.geojson')

    try:
        resulting_room = point_in_polygon(x, y, geojson_file)
        if resulting_room:
            print(f"The point ({x}, {y}) is inside {resulting_room}.")
        else:
            print(f"The point ({x}, {y}) is outside any of the polygons in {geojson_file}.")
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")

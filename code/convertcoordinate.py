import json
from pyproj import Transformer


# Function to convert coordinates from EPSG:28992 to WGS84 using Transformer
def convert_coordinates(coordinates, transformer):
    if isinstance(coordinates[0], list):  # Check if it's a list of coordinates (for LineString or Polygon)
        return [convert_coordinates(coord, transformer) for coord in coordinates]
    else:  # If it's a single point
        # Transform the coordinates from EPSG:28992 (x, y) to EPSG:4326 (longitude, latitude)
        return list(
            transformer.transform(coordinates[0], coordinates[1]))  # Use (x, y) order for EPSG:28992 to EPSG:4326


# Function to convert GeoJSON geometry
def convert_geometry(geometry, transformer):
    geom_type = geometry['type']
    if geom_type == 'Point':
        geometry['coordinates'] = convert_coordinates(geometry['coordinates'], transformer)
    elif geom_type == 'LineString' or geom_type == 'MultiPoint':
        geometry['coordinates'] = convert_coordinates(geometry['coordinates'], transformer)
    elif geom_type == 'Polygon' or geom_type == 'MultiLineString':
        geometry['coordinates'] = [convert_coordinates(ring, transformer) for ring in geometry['coordinates']]
    elif geom_type == 'MultiPolygon':
        geometry['coordinates'] = [[convert_coordinates(ring, transformer) for ring in polygon] for polygon in
                                   geometry['coordinates']]
    return geometry


# Function to process the entire GeoJSON feature collection and update the CRS
def convert_geojson(geojson_data, transformer):
    # Update the CRS to EPSG:4326 (WGS84)
    geojson_data['crs'] = {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:EPSG::4326"
        }
    }

    # Convert all feature geometries
    for feature in geojson_data['features']:
        feature['geometry'] = convert_geometry(feature['geometry'], transformer)
    return geojson_data


# Main part of the code
def convert_geojson_epsg28992_to_latlong(input_geojson_path, output_geojson_path):
    # Define the transformer from EPSG:28992 to WGS84 (EPSG:4326)
    transformer = Transformer.from_crs("EPSG:28992", "EPSG:4326", always_xy=True)

    # Read input GeoJSON
    with open(input_geojson_path, 'r') as f:
        geojson_data = json.load(f)

    # Convert coordinates and update CRS
    converted_geojson = convert_geojson(geojson_data, transformer)

    # Write the output GeoJSON
    with open(output_geojson_path, 'w') as f:
        json.dump(converted_geojson, f, indent=2)


# Example usage:
input_geojson = r'D:\geomatics\geo1101\convertcoordinate\data\pointxy.geojson'  # Path to your input GeoJSON file
output_geojson = r'D:\geomatics\geo1101\convertcoordinate\data\pointlatlon.geojson'  # Path to your output GeoJSON file

convert_geojson_epsg28992_to_latlong(input_geojson, output_geojson)

print(f"Converted GeoJSON has been saved to {output_geojson}")
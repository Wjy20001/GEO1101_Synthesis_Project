import json
import os
import pickle
import shutil
import subprocess
from typing import List

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
import requests

# Importing custom functions
from API.get_room_name import get_file_paths, get_room_name
from API.routing import navigation
from functions_framework import http
from fastapi.middleware.cors import CORSMiddleware

API_FOLDER_PATH = os.path.join(os.getcwd(), "API")
data_path = os.path.join(API_FOLDER_PATH, "data")


# Create FastAPI instance
app = FastAPI()
allowed_origins = [
    "*",
    "http://localhost:9000",
    "https://synthesis-proj.netlify.app/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the user_data_cache folder exists
cache_dir = os.path.join(API_FOLDER_PATH, "user_data_cache")
os.makedirs(cache_dir, exist_ok=True)

if os.getenv("ENVIRONMENT") == "production":
    reference_data_file = os.getenv(
        "REFERENCE_DATA_URL"
    )  # Get from external server URL
    if not reference_data_file:
        raise ValueError("REFERENCE_DATA_URL is not set")
    response = requests.get(reference_data_file)
    ref_image_paths, ref_vgg16_features = pickle.loads(response.content)
else:
    reference_data_file = os.path.join(data_path, "model.pkl")
    print("reference data file:", reference_data_file)
    with open(reference_data_file, "rb") as f:
        ref_image_paths, ref_vgg16_features = pickle.load(f)


@app.get("/")
async def main():
    """
    Serves the main HTML page where users can upload images. (SIMPLE PLACEHOLDER, will become the UI of Hide)
    """
    # HTML form with an upload button for multiple file uploads
    content = """
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 10px;">
            <h2>Upload Images (PNG or JPG only)</h2>
            <form action="/localize" enctype="multipart/form-data" method="post">
                <input name="files" accept="image/*" type="file" multiple style="display: block; margin-bottom: 10px;">
                <input type="submit" value="Localize" style="padding: 10px 20px;">
            </form>
            <h2>Navigate</h2>
            <form action="/navigate" method="post">
                <label for="start_room_name">Enter Start Room:</label>
                <input type="text" id="start_room_name" name="start_room_name" required style="display: block; margin-bottom: 10px;">

                <label for="end_room_name">Enter Destination Room:</label>
                <input type="text" id="end_room_name" name="end_room_name" required style="display: block; margin-bottom: 10px;">

                <input type="submit" value="Navigate" style="padding: 10px 20px;">
            </form>
        </body>
    </html>
    """

    return HTMLResponse(content=content)


@app.post("/localize/")
async def upload_images(files: List[UploadFile] = File(...)):
    print("hooo--------------")
    """
    Handles image uploads, saves them to a directory, and calculates the user position based on the images.

    Parameters:
    -----------
    files : List[UploadFile]
        A list of uploaded files (images).

    Returns:
    --------
    JSONResponse
        A JSON-formatted response containing the user room and user coordinates.
    """
    # Process each uploaded file
    for file in files:
        # Get the file extension and ensure it's an allowed image type
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in {".png", ".jpg", ".jpeg"}:
            # If the file type is not allowed, raise an error
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not supported. Only PNG and JPG are allowed.",
            )

        # Define the path where the image will be saved
        image_path = os.path.join(cache_dir, file.filename)

        # Save the uploaded image to the cache_dir folder
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    # After saving all images, run the coordinate calculation using the uploaded images

    try:
        print(f"Calculating user position from uploaded images.")
        print("=" * 80)

        img_names: list = get_file_paths(cache_dir, images=True)
        floorplan_json_path = os.path.join(data_path, "floorplan.geojson")
        # trained_model_path: str = os.path.join(data_path, "model.pkl")
        slam_csv_path: str = os.path.join(data_path, "slam_coordinates.csv")

        user_room, user_coordinate = get_room_name(
            img_names,
            floorplan_json_path,
            ref_vgg16_features,
            ref_image_paths,
            slam_csv_path,
        )
        print("=" * 80)

    except subprocess.CalledProcessError as e:
        # Handle any errors that occur during the coordinate calculation
        raise HTTPException(
            status_code=500, detail=f"Error running coordinate.py: {str(e)}"
        )

    finally:
        # Clean up by deleting all files in the cache_dir directory
        print("-" * 30)
        print(f"removing user images")

        for file in os.listdir(cache_dir):
            file_path = os.path.join(cache_dir, file)

            try:
                os.remove(file_path)

            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")

    # Return the user coordinates as a JSON response
    print(f"Sending user position:\t\t{user_room}, {user_coordinate}")

    return JSONResponse(
        content={"user_room": user_room, "user_coordinate": user_coordinate}
    )


@app.get("/navigate/")
async def find_route(start_room_name: str, end_room_name: str):
    floorplan_json_path = os.path.join(data_path, "floorplan.geojson")
    nodes_json_path = os.path.join(data_path, "nodes.geojson")
    route_json_path = os.path.join(
        API_FOLDER_PATH, "user_data_cache", "route.geojson"
    )

    try:
        print("=" * 60)
        print("Calculating fastest route")
        print("Start Room:\t", start_room_name)
        print("End Room:\t", end_room_name)

        # Run navigation function to generate the GeoJSON file
        navigation(
            start_room_name,
            end_room_name,
            floorplan_json_path,
            nodes_json_path,
            route_json_path,
        )

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f"Error running scripts: {str(e)}"
        )

    try:
        # Load GeoJSON data from the generated file and return it as JSON response
        with open(route_json_path, "r") as file:
            geojson_data = json.load(file)

        print(f"Sending routing json")
        return JSONResponse(content=geojson_data)

    except FileNotFoundError:
        return JSONResponse(
            content={"error": "GeoJSON file not found."}, status_code=404
        )
    except json.JSONDecodeError:
        return JSONResponse(
            content={"error": "Invalid GeoJSON format."}, status_code=400
        )

    finally:
        # Delete the GeoJSON file after the response has been sent
        cache_path_name = os.path.join(
            os.path.basename(os.path.dirname(route_json_path)),
            os.path.basename(route_json_path),
        )

        if os.path.exists(route_json_path):
            try:
                os.remove(route_json_path)
                print(f"Deleted temporary file: {cache_path_name}")
            except Exception as e:
                print(f"Failed to delete {cache_path_name}: {e}")


@http
def handle_request(request: Request):
    return app(request)


if __name__ == "__main__":
    # Run the FastAPI app using Uvicorn when executed as a script
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

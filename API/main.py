import os
import shutil
import subprocess
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

# Importing custom functions
from API.get_room_name import get_room_name, get_file_paths


API_FOLDER_PATH = os.path.join(os.getcwd(), "API")


# Create FastAPI instance 
app = FastAPI()

# Ensure the user_data_cache folder exists
cache_dir = os.path.join(API_FOLDER_PATH, "user_data_cache")
os.makedirs(cache_dir, exist_ok=True)


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
                <input name="files" type="file" multiple style="display: block; margin-bottom: 10px;">
                <input type="submit" value="Localize" style="padding: 10px 20px;">
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=content)


@app.post("/localize/")
async def upload_images(files: List[UploadFile] = File(...)):
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
        print('=' * 80)
        
        data_path = os.path.join(API_FOLDER_PATH, "data")

        img_names: list = get_file_paths(cache_dir, images=True)
        floorplan_json_path, _ = get_file_paths(data_path, extension="geojson")
        trained_model_path: str = get_file_paths(data_path, extension="pkl")
        slam_csv_path: str = get_file_paths(data_path, extension="csv")

        user_room, user_coordinate = get_room_name(img_names, floorplan_json_path, trained_model_path, slam_csv_path)
        print('=' * 80)


    except subprocess.CalledProcessError as e:
        # Handle any errors that occur during the coordinate calculation
        raise HTTPException(status_code=500, detail=f"Error running coordinate.py: {str(e)}")


    finally:
        # Clean up by deleting all files in the cache_dir directory
        print('-' * 30)
        print(f"removing user images")

        for file in os.listdir(cache_dir):
            file_path = os.path.join(cache_dir, file)

            try:
                os.remove(file_path)

            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")


    # Return the user coordinates as a JSON response
    print(f"Sending user position:\t\t{user_room}, {user_coordinate}")

    return JSONResponse(content={"user_room": user_room,
                                 "user_coordinate": user_coordinate})


@app.post("/navigate/")
async def run_scripts():
    """
    Endpoint to trigger the execution of script1.py and script2.py.
    """
    try:
        pass

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f"Error running scripts: {str(e)}"
        )

    return JSONResponse(content={"message": "Scripts executed successfully"})



if __name__ == "__main__":
    # Run the FastAPI app using Uvicorn when executed as a script
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

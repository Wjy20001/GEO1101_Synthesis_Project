import os
import shutil
import subprocess
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

# Importing custom functions and constants
from API.const import API_FOLDER_PATH
from API.coordinate import get_coord_from_image_set

# Create FastAPI instance
app = FastAPI()

# Ensure the input_images folder exists
input_images_dir = os.path.join(API_FOLDER_PATH, "input_images")
os.makedirs(input_images_dir, exist_ok=True)


@app.get("/")
async def main():
    """
    Serves the main HTML page where users can upload images. (SIMPLE PLACEHOLDER, will become the UI of Hide)
    """
    # HTML form with an upload button for multiple file uploads
    content = """
    <html>
        <body>
            <h2>Upload Images (PNG or JPG only)</h2>
            <form action="/upload" enctype="multipart/form-data" method="post">
                <input name="files" type="file" multiple>
                <input type="submit" value="Upload">
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=content)


@app.post("/upload/")
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
        A JSON-formatted response containing the user coordinates.
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
        image_path = os.path.join(input_images_dir, file.filename)

        # Save the uploaded image to the input_images folder
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    # After saving all images, run the coordinate calculation using the uploaded images
    try:
        print(f"Calculating user position from uploaded images.")
        # Calculate the user position using the get_coord_from_image_set function
        user_position = get_coord_from_image_set(
            user_image_dir=input_images_dir
        )

    except subprocess.CalledProcessError as e:
        # Handle any errors that occur during the coordinate calculation
        raise HTTPException(
            status_code=500, detail=f"Error running coordinate.py: {str(e)}"
        )

    # Return the user coordinates as a JSON response
    print(f"Sending user position:\t\t{user_position}")
    return JSONResponse(content={"user coordinates": user_position})


@app.post("/localize/")
async def run_scripts():
    """
    Endpoint to trigger the execution of script1.py and script2.py.
    """
    try:
        # Run script1.py
        subprocess.run(["python", "path/to/script1.py"], check=True)
        # Run script2.py
        subprocess.run(["python", "path/to/script2.py"], check=True)

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f"Error running scripts: {str(e)}"
        )

    return JSONResponse(content={"message": "Scripts executed successfully"})



if __name__ == "__main__":
    # Run the FastAPI app using Uvicorn when executed as a script
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

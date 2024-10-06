
# Project README

## Overview

This project is designed to perform image matching using a Bag of Words (BoW) model, leveraging KMeans clustering and ORB descriptors. The project is organized into separate Python scripts that allow for the extraction of image frames from videos, computation of ORB descriptors, KMeans clustering for BoW vectors, and matching sample images to a dataset using the BoW model.

## Project Structure

The project is structured as follows:

- `code/`: Contains all Python scripts.
- `data/`: Contains the datasets (subfolders with images or videos).

- `code/extract_frames.py`: Extracts frames from a video and saves them in a `frames` folder.
- `code/extract_descriptors.py`: Extracts ORB descriptors from images.
- `code/perform_kmeans.py`: Performs KMeans clustering on the extracted descriptors to build a BoW model.
- `code/save_bow_vectors.py`: Saves the BoW vectors and image names after clustering.
- `code/match_image.py`: Matches a sample image to a set of BoW vectors.

## Python Version and Dependencies

- **Python Version**: 3.11.9
- **Required Libraries**:
  - `numpy`
  - `opencv-python`
  - `scikit-learn`
  - `tqdm`
  - `argparse`
  - `DBOW`
  TO DO: how to install dbow because it is not in pip!


To install the required libraries using `pip`, run:
```bash
pip install numpy opencv-python scikit-learn tqdm argparse
```

## Recommended Tool for Dependency Management

We recommend using [Poetry](https://python-poetry.org/) for dependency management and packaging. Poetry helps you declare, manage, and install dependencies of Python projects, ensuring you have the right stack everywhere.
Once you install poetry, you can simple install dependencies like this. It will create a virtual environment and install all the dependencies in it.
```bash
poetry install
```

## Scripts and Their Functionality

### 1. **extract_frames.py**
Extracts frames from a video and saves them in the `frames` subfolder within the dataset directory.

**Usage:**
```bash
python code/extract_frames.py <video_path> --frame_step <n>
```
- `video_path`: Path to the input video file.
- `frame_step`: Number of frames to skip before saving (e.g., `1` saves every frame, `20` saves every 20th frame).

### 2. **extract_descriptors.py**
Extracts ORB descriptors from all `.png` and `.jpg` images in the `frames` folder of a dataset.

**Usage:**
This script is called by other scripts, but it can be used independently as follows:
```bash
python code/extract_descriptors.py
```

### 3. **perform_kmeans.py**
Performs KMeans clustering on the descriptors to build a visual vocabulary (Bag of Words). The number of clusters can be controlled.

**Usage:**
```bash
python code/perform_kmeans.py
```

This script will prompt you to enter the number of clusters for KMeans.

### 4. **save_bow_vectors.py**
Saves the BoW vectors for each image and the corresponding image names in `.npy` files.

**Usage:**
```bash
python code/save_bow_vectors.py
```
This script processes the images based on the KMeans model and saves the BoW vectors and image names.

### 5. **match_image.py**
Matches a sample image to the images in the dataset by comparing their BoW vectors.

**Usage:**
```bash
python code/match_image.py <sample_image_path> --dataset <dataset_name> --show_image
```
- `sample_image_path`: Path to the sample image.
- `--dataset`: Name of the dataset folder (located in `data/`).
- `--show_image`: If specified, displays the sample and best match images.

### 6. **setup_database.py** (Main Orchestrator)
This script runs all the other steps in the correct order, starting from descriptor extraction to saving BoW vectors. It provides an entry point to process the dataset.

**Usage:**
```bash
python code/setup_database.py <dataset_dir> --clusters <n>
```
- `dataset_dir`: Path to the dataset directory containing the `frames` folder.
- `--clusters`: Number of clusters for KMeans.

## Example Workflow

### 1. Extract Frames from a Video
First, extract frames from a video in the dataset.
```bash
python code/extract_frames.py data/dataset_x/video.mp4 --frame_step 20
```

### 2. Run the Setup Process
Run the setup script to extract descriptors, perform KMeans clustering, and save BoW vectors.
```bash
python code/setup_database.py data/dataset_x --clusters 200
```

### 3. Match a Sample Image
Once the BoW model is created, match a sample image to find its closest match in the dataset.
```bash
python code/match_image.py data/test_user_images/sample_001.png --dataset dataset_x --show_image
```

## Lint, Format, and Test
So we all can work on the same source code, it's recommended to run the following commands before pushing the code.
```bash
poetry run black .
poetry run isort .
poetry run flake8 .
```
or simply with one command
```bash
poetry run check
```
These commands will format the code, check for linting errors and sort the imports so we don't need to have unnecessary merge conflicts.

---

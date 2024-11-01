# Project README

## Overview

This project presents an indoor navigation system based on image matching, aiming to address the challenges of localization and navigation in indoor environments. The system utilizes Simultaneous Localization and Mapping (SLAM) technology to capture high-resolution images and point cloud data, combined with the VGG16 model from Convolutional Neural Networks (CNN) for image processing, feature extraction, and matching.

In our research, we conducted experiments at the Faculty of Architecture and the Built Environment of Delft University of Technology, using a SLAM scanner to obtain 360-degree panoramic images and point cloud data of the indoor environment. Through cube mapping projection, we converted the panoramic images into six planar views, selecting the front, right, and left views as positioning references. Additionally, we reconstructed the indoor environment structure and designed node networks for positioning and navigation.

The system also provides a web-based application consisting of an app running in the browser and a server app to process image matching. Additionally, by collaborating with Esri Nederland, we leverage their technical expertise to enhance the system's usability and ensure it can be applied in diverse indoor environments.

## Project Structure

The project is structured as follows:
### 4. **image.py**
- `ImageMatcher` class for matching images using ORB descriptors and a pre-trained database.
- Methods to initialize the matcher, load the database, and find matched images.

### 5. **training.py**
- Functions to train the Bag of Words model using ORB descriptors.
- Processes images, creates a vocabulary, and builds a database of descriptors.
- Can be run independently to generate necessary files for image matching.

### 6. **localisation.py**
- Functions for localizing points based on matched images.
- Creates scatter plots of matched points.
- Computes central points for localization.
- Handles image data extraction from a CSV file.
- Can be used to visualize localization results.


## Python Version and Dependencies

- **Python Version**: 3.11.9
- **Required Libraries**:
Dependencies are listed in the `pyproject.toml` or `requirements.txt` file.


To install the required libraries using `pip`, run:
```bash
pip install -r requirements.txt
```

### Recommended Tool for Dependency Management

We recommend using [Poetry](https://python-poetry.org/) for dependency management and packaging. Poetry helps you declare, manage, and install dependencies of Python projects, ensuring you have the right stack everywhere.
Once you install poetry, you can simple install dependencies like this. It will create a virtual environment and install all the dependencies in it.
```bash
poetry install
```

## Scripts and Their Functionality
### Training the Bag of Words Model
To train the Bag of Words model, run the `training.py` script. This script processes images, computes ORB descriptors, and trains the BoW model. The script saves the vocabulary and database to disk for later use in image matching.

```bash
	poetry run python code/training.py
```

### Matching Images
To match images using the Bag of Words model, run the `image.py` script. This script loads the pre-trained database and vocabulary, computes ORB descriptors for a sample image, and matches the image to the database.

```bash
  poetry run python code/image.py
```

### Localizing Points
To localize points based on matched images, run the `localisation.py` script. This script loads matched points from a CSV file, computes central points for localization, and visualizes the localization results.

```bash
  poetry run python code/localisation.py
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

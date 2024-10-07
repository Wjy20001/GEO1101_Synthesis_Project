import pandas as pd
import numpy as np
from scipy.spatial import KDTree
import matplotlib.pyplot as plt

# Step 1: Load the 2D points from a CSV file
df = pd.read_csv(r'D:\geomatics\geo1101\floorplanvis\BK HALL wall edited.csv')  # replace 'points.csv' with your file path

# Convert the DataFrame to a NumPy array
points = df[['x', 'y']].values

# Step 2: Find the nearest neighbors for each point using KDTree
tree = KDTree(points)
# Query for the closest 3 points (excluding the point itself)
distances, indices = tree.query(points, k=4)  # k=4 to get more neighbors (increase if necessary)

# Step 3: Draw lines connecting each point to its closest neighbor if the distance is less than 50 meters
threshold = 2  # in meters
lines = []
for i, dists in enumerate(distances):
    for j in range(1, len(dists)):  # Start from the 1st nearest neighbor (2nd index)
        if dists[j] < threshold:  # only add lines for distances below the threshold
            nn = indices[i, j]
            line = [points[i], points[nn]]
            lines.append(line)

# Step 4: Visualize only the lines (no points)
plt.figure(figsize=(8, 8))

# Draw the lines
for line in lines:
    plt.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], 'b-')

plt.title('BK Hall Floor plan')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)
plt.show()

import pandas as pd
import numpy as np
from scipy.spatial import KDTree
import matplotlib.pyplot as plt


def load_points(file_path):
    """Load the 2D points from a CSV file."""
    df = pd.read_csv(file_path)
    points = df[['x', 'y']].values
    return points


def find_nearest_neighbors(points, k=4):
    """Find the nearest neighbors for each point using KDTree."""
    tree = KDTree(points)
    distances, indices = tree.query(points, k=k)
    return distances, indices


def get_lines_within_threshold(points, distances, indices, threshold):
    """Get the lines connecting points to their neighbors within a distance threshold."""
    lines = []
    for i, dists in enumerate(distances):
        for j in range(1, len(dists)):  # Start from the 1st nearest neighbor (2nd index)
            if dists[j] < threshold:  # only add lines for distances below the threshold
                nn = indices[i, j]
                line = [points[i], points[nn]]
                lines.append(line)
    return lines


def visualize_lines(lines, title='Floor Plan'):
    """Visualize lines on a plot."""
    plt.figure(figsize=(8, 8))

    for line in lines:
        plt.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], 'b-')

    plt.title(title)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    plt.show()


def main(file_path, threshold=2, k=4):
    """Main function to load points, find neighbors, and visualize the result."""
    points = load_points(file_path)
    distances, indices = find_nearest_neighbors(points, k=k)
    lines = get_lines_within_threshold(points, distances, indices, threshold)
    visualize_lines(lines, title='BK Hall Floor plan')


# Example usage:
if __name__ == "__main__":
    file_path = r'D:\geomatics\geo1101\floorplanvis\BK HALL wall edited.csv'
    main(file_path, threshold=2, k=4)

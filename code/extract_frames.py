import argparse
import cv2
import os
from tqdm import tqdm

# Function to extract frames from video
def extract_frames(video_path, frame_step=20):
    # Get the directory where the video is located
    video_dir = os.path.dirname(video_path)

    # Set the output folder to 'frames' inside the video directory
    output_folder = os.path.join(video_dir, "frames")

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Open the video file
    cap = cv2.VideoCapture(video_path)
    frame_count = 0

    # Get the total number of frames in the video for tqdm progress bar
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Loop through the video and save frames with tqdm progress bar
    with tqdm(total=total_frames // frame_step, desc="Extracting Frames", unit="frame") as pbar:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Save the frame only if it matches the frame_step
            if frame_count % frame_step == 0:
                # Use 5 digits in the filename (e.g., frame_00001.png)
                frame_filename = os.path.join(output_folder, f'frame_{frame_count:05d}.png')
                cv2.imwrite(frame_filename, frame)
                pbar.update(1)

            frame_count += 1

    # Release the video capture object
    cap.release()
    cv2.destroyAllWindows()

# Function to parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract frames from a video file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Only requires video_path and frame_step
    parser.add_argument("video_path", type=str, help="Path to the input video file.")
    parser.add_argument("--frame_step", type=int, default=20, help="Save every nth frame (e.g., 1 = every frame, 20 = every 20th frame)")

    return parser.parse_args()

def main():
    # Parse command-line arguments
    args = parse_args()

    # Call the extract_frames function with parsed arguments
    extract_frames(args.video_path, args.frame_step)

if __name__ == "__main__":
    main()

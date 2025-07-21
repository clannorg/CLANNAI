import cv2
import pandas as pd
import os
import numpy as np

def save_snapshot(frame, timestamp, prefix='snapshot'):
    """
    Save the current frame as a JPEG file with a timestamp-based filename.

    Parameters:
        frame (ndarray): The frame to be saved.
        timestamp (int): The timestamp in milliseconds used for naming the file.
        prefix (str): The prefix for the filename. Default is 'snapshot'.

    Returns:
        bool: True if the snapshot was saved successfully, False otherwise.
    """
    # Validate inputs
    if not isinstance(frame, (np.ndarray, np.generic)):
        print("Error: The frame is not a valid image.")
        return False
    
    if not isinstance(timestamp, int):
        print("Error: The timestamp must be an integer.")
        return False
    
    if not isinstance(prefix, str) or not prefix.strip():
        print("Error: The prefix must be a non-empty string.")
        return False
    
    # Create filename
    filename = f"{prefix}_{int(timestamp)}.jpg"
    
    # Convert filename to absolute path
    file_path = os.path.expanduser('~/street/data_results/' + filename)
    
    try:
        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Save the frame
        success = cv2.imwrite(file_path, frame)
        if not success:
            print(f"Error: Failed to save snapshot to {file_path}")
            return False
    except cv2.error as cv_err:
        print(f"OpenCV error while saving snapshot: {cv_err}")
        return False
    except Exception as e:
        print(f"Unexpected error saving snapshot: {e}")
        return False
    
    # print(f"Snapshot saved to {file_path}")
    return True

def corresponding_bgr_colors(color):
    """
    Convert a color name to its RGB values.

    Parameters:
        color (str): The color name.

    Returns:
        tuple: The corresponding RGB values.

    Raises:
        ValueError: If the color is unsupported.
    """
    # Convert the color name to lower case
    color = color.lower()
    
    # Define the color mappings
    colors = {
        'red': (0, 0, 255),
        'green': (0, 255, 0),
        'blue': (255, 0, 0),
        'yellow': (0, 255, 255),
        'cyan': (255, 255, 0),
        'magenta': (255, 0, 255),
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'gold': (0, 215, 255)  # Added gold color
    }
    
    if color not in colors:
        raise ValueError(f"Unsupported color: {color}")
    
    return colors[color]


def show_tracking_results(video_path, *args, save='off', prefix = 'snapshot', save_all = False, minimum_thickness = 2):
    """
    Display video with bounding boxes drawn from provided dictionaries and colors.

    Parameters:
        video_path (str): Path to the video file.
        *args: Alternating dictionaries of timestamp and bounding boxes, and color names.
        save (str): Whether to save frames ('on' or 'off').
        save_all (bool): wether to save all frames if True or only frames where tracking results are available if False
    """
    # Validate arguments
    if len(args) % 2 != 0:
        raise ValueError("Arguments should contain alternating dictionaries and color names")
    
    list_of_dicts = []
    list_of_colors = []

    for i in range(0, len(args), 2):
        if not isinstance(args[i], dict):
            raise TypeError(f"Expected a dictionary at position {i}, got {type(args[i])}")
        list_of_dicts.append(args[i])
        list_of_colors.append(corresponding_bgr_colors(args[i + 1]))

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return
    
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))

        save_this_one = save_all
        current_thickness = 2*(len(list_of_dicts) - 1) + minimum_thickness
        for index, dicts in enumerate(list_of_dicts):
            if timestamp_ms in dicts:
                x1, y1, x2, y2 = dicts[timestamp_ms]
                cv2.rectangle(frame, (x1, y1), (x2, y2), list_of_colors[index], current_thickness)
                save_this_one = True
                current_thickness -= 2

        cv2.imshow("Tracking", frame)

        if save.lower() == 'on' and save_this_one:
            save_snapshot(frame, timestamp_ms, prefix = prefix)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # ESC key or 'q'
            break

    if num_frames > 0:
        retention_rate = round(len({key for d in list_of_dicts for key in d})/ num_frames * 100, 1)
        print(f'Retention rate = {retention_rate} %')

    cap.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1) 

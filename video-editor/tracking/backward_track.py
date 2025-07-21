import cv2
import pickle
from tracking.forward_track import init_tracker, update_tracker
import os

def load_frames(video_path):
    """
    Load all frames from a video file into a dictionary.

    Parameters:
        video_path (str): Path to the video file.

    Returns:
        dict: A dictionary with timestamps as keys and frames as values.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Error opening video file: {video_path}")

    frames = {}
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        frames[timestamp_ms] = frame

    cap.release()
    return frames

def find_previous_ai_detection(ai_detect, current_timestamp, first_frame_timestamp, separation_time):
    """
    Find the most appropriate previous ai detection timestamp.

    Parameters:
        ai_detect (dict): Dictionary of ai detections.
        current_timestamp (int): The current timestamp to check against.
        separation_time (int): Time separation threshold.
        first_frame_timestamp (int): timestamp of the first frame of the video.

    Returns:
        int or None: The closest previous ai detection timestamp or None.
    """
    past_timestamps = [ts for ts in ai_detect if ts < current_timestamp]
    if not past_timestamps:
        return None

    past_timestamps.sort(reverse=True)
    gaps = [(past_timestamps[i] - past_timestamps[i + 1]) for i in range(len(past_timestamps) - 1)]
    significant_gaps = [past_timestamps[i] for i in range(len(past_timestamps) - 1) if gaps[i] > separation_time]
    previous_ai_timestamp = significant_gaps[0] if significant_gaps else past_timestamps[-1]

    return previous_ai_timestamp if previous_ai_timestamp != first_frame_timestamp else None

def track_detection_backward(video_path, ai_detect, save='off', prefix=None):
    """
    Track the ball backward in the video using ai detections.

    Parameters:
        video_path (str): Path to the video file.
        ai_detect (dict): Dictionary with timestamps as keys and bounding boxes as values.
        save (str): Whether to save the detections ('on' or 'off').
        prefix (str): Prefix for the filename if saving detections.

    Returns:
        dict: A dictionary with timestamps and bounding boxes of the tracked ball.
    """
    if not ai_detect:
        raise ValueError("No ai detections provided.")
    
    frames = load_frames(video_path)
    
    if not frames:
        raise ValueError("No frames loaded from video.")
    
    backward_track = {}
    fps = cv2.VideoCapture(video_path).get(cv2.CAP_PROP_FPS)
    num_frames = len(frames)
    ts_separation = int(1000 / fps * 1.10)  # Safety factor of 10% to account for rounding errors
    sorted_timestamps = sorted(frames.keys())
    first_frame_timestamp_ms = sorted_timestamps[0]  # Assume the first timestamp is the first in time

    current_index = len(sorted_timestamps)-1
    while current_index >= 0:
        current_timestamp = sorted_timestamps[current_index]
        
        if current_timestamp in ai_detect:
            current_index -= 1
            continue

        previous_ai_timestamp = find_previous_ai_detection(ai_detect, current_timestamp, first_frame_timestamp_ms, ts_separation)
        
        # Handle case where no future ai detection is available
        closest_ai_timestamp = min((ts for ts in ai_detect if ts > current_timestamp), default = None)
        if not closest_ai_timestamp:
            if previous_ai_timestamp:
                current_index = sorted_timestamps.index(previous_ai_timestamp) - 1
                continue
            else:
                break

        # Retrieve and set frame to the closest ai detection
        ai_frame = frames[closest_ai_timestamp]

        # Initialize the tracker with the ai bounding box
        x1, y1, x2, y2 = ai_detect[closest_ai_timestamp]
        ai_bbox = (x1, y1, x2 - x1, y2 - y1)
        tracker = init_tracker(ai_frame, ai_bbox)

        previous_index = sorted_timestamps.index(closest_ai_timestamp) - 1
        while previous_index >= 0:
            previous_timestamp_ms = sorted_timestamps[previous_index]
            previous_frame = frames[previous_timestamp_ms]
            previous_bbox = update_tracker(tracker, previous_frame)

            if previous_bbox and (previous_ai_timestamp is None or previous_timestamp_ms >= previous_ai_timestamp):
                x1, y1, w, h = previous_bbox
                backward_track[previous_timestamp_ms] = (x1, y1, x1 + w, y1 + h)
                previous_index -= 1
            else:
                break
        
        if previous_ai_timestamp:
            current_index = sorted_timestamps.index(previous_ai_timestamp) - 1
        else:
            break

    if num_frames > 0:
        retention_rate = round(len(set(ai_detect.keys()) | set(backward_track.keys())) / num_frames * 100, 1)
        print(f'Retention rate = {retention_rate} %')

    if save.lower() == 'on':
        file_name = f"/{prefix}_backward_track_detections.pkl" if prefix else "backward_track_detections.pkl"
        file_path = os.path.expanduser('~/street/data_results/' + file_name)
        try:
            with open(file_path, 'wb') as file:
                pickle.dump(backward_track, file)
            print(f"Detections saved to {file_path}")
        except Exception as e:
            print(f"Error saving detections: {e}")

    return backward_track

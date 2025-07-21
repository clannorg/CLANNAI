import os
import pickle
import cv2

def merge_tracking_results(video_path, ai_detect, *args, save='off', prefix=None):
    """
    Merge multiple dictionaries of bounding box detections based on their timestamps.

    Args:
        video_path (str): Path to the video file used to calculate the retention rate.
        ai_detect (dict): A dictionary where keys are timestamps (int) and values are bounding boxes (tuple of 4 ints).
        *args (tuple): Additional dictionaries with the same structure as `ai_detect`, representing detections from other sources.
                        Each dictionary should be followed by a tracking direction ('forward' or 'backward').
        save (str): If 'on', the merged results will be saved to a pickle file. Defaults to 'off'.
        prefix (str, optional): Prefix for the filename if `save` is 'on'. Defaults to None.

    Returns:
        dict: A dictionary where keys are timestamps and values are the selected bounding boxes.
              The bounding box selection is based on the availability and priority of sources,
              with `ai_detect` having the highest priority.
    """
    # Open the video file and check validity
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Error opening video file: {video_path}")

    # Calculate video duration in milliseconds
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    if fps <= 0:
        raise ValueError("Frames per second (fps) is zero or negative. Unable to determine video length.")
    
    total_duration_ms = int((num_frames / fps) * 1000)

    # Initialize merged tracks with a deep copy of ai detections
    merged_tracks = ai_detect.copy()

    # Process additional dictionaries and directions
    list_of_dicts = []
    list_of_directions = []

    if len(args) % 2 != 0:
        raise ValueError("Arguments must be provided as pairs of dictionary and direction.")

    for i in range(0, len(args), 2):
        if not isinstance(args[i], dict):
            raise TypeError(f"Expected a dictionary at position {i}, got {type(args[i])}.")
        if not isinstance(args[i + 1], str):
            raise ValueError(f"Expected a string for tracking direction at position {i + 1}, got {type(args[i + 1])}.")
        if args[i + 1].lower() not in ('forward', 'backward'):
            raise ValueError(f"Expected 'forward' or 'backward' for tracking directions, got {args[i + 1]}.")
        # Append the valid dictionary and direction to the lists
        list_of_dicts.append(args[i])
        list_of_directions.append(args[i + 1].lower())


    # Merge the dictionaries based on timestamp and direction
    total_timestamps = set(t for d in list_of_dicts for t in d.keys())
    new_timestamps = total_timestamps - set(ai_detect.keys())
    for timestamp_ms  in new_timestamps:
        old_priority = total_duration_ms
        new_priority = old_priority
        for i, track_dict in enumerate(list_of_dicts):
            if timestamp_ms in track_dict:
                direction = list_of_directions[i]
                if direction == 'forward':
                    previous_timestamps = [t for t in ai_detect.keys() if t < timestamp_ms]
                    if previous_timestamps:
                        new_priority = timestamp_ms - max(previous_timestamps)
                    else:
                        new_priority = total_duration_ms
                elif direction == 'backward':
                    future_timestamps = [t for t in ai_detect.keys() if t > timestamp_ms]
                    if future_timestamps:
                        new_priority = min(future_timestamps) - timestamp_ms
                    else:
                        new_priority = total_duration_ms

                if new_priority < old_priority:
                    merged_tracks[timestamp_ms] = track_dict[timestamp_ms]
                    old_priority = new_priority

    # Calculate and print retention rate
    if num_frames > 0:
        retention_rate = round(len(merged_tracks) / num_frames * 100, 1)
        print(f'Retention rate = {retention_rate} %')

    # Save merged results if requested
    if save.lower() == 'on':
        file_name = f"{prefix}_merged_tracks_detections.pkl" if prefix else "merged_tracks_detections.pkl"
        file_path = os.path.expanduser('~/street/data_results/' + file_name)
        try:
            with open(file_path, 'wb') as file:
                pickle.dump(merged_tracks, file)
            print(f"Detections saved to {file_path}")
        except Exception as e:
            print(f"Error saving detections: {e}")

    return merged_tracks

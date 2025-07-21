import cv2
import pickle
import os

def init_tracker(frame, bbox):
    """
    Initialize the CSRT tracker with the given frame and bounding box.
    
    Parameters:
        frame: The initial frame from which to start tracking.
        bbox: The initial bounding box for the object to track (x1, y1, x2, y2).

    Returns:
        tracker: Initialized CSRT tracker.
    """
    tracker = cv2.TrackerCSRT_create()
    tracker.init(frame, bbox)
    return tracker

def update_tracker(tracker, frame):
    """
    Update the tracker with a new frame and return the updated bounding box.
    
    Parameters:
        tracker: The tracker object.
        frame: The frame to update the tracker with.

    Returns:
        bbox: The updated bounding box (x1, y1, x2, y2) if tracking is successful, else None.
    """
    success, bbox = tracker.update(frame)
    if success:
        return tuple(map(int, bbox))
    return None

def find_next_ai_detection(ai_detect, current_timestamp, last_frame_timestamp, separation_time):
    """
    Find the most appropriate next ai detection timestamp.

    Parameters:
        ai_detect (dict): Dictionary of ai detections.
        current_timestamp (int): The current timestamp to check against.
        separation_time (int): Time separation threshold.
        last_frame_timestamp (int): timestamp of the last frame of the video

    Returns:
        int or None: The closest previous ai detection timestamp or None.
    """
    future_timestamps = [ts for ts in ai_detect if ts > current_timestamp]
    if not future_timestamps:
        return None

    future_timestamps.sort()
    gaps = [(future_timestamps[i + 1] - future_timestamps[i]) for i in range(len(future_timestamps) - 1)]
    gap_exceeds_separation = [future_timestamps[i] for i in range(len(future_timestamps) - 1) if gaps[i] > separation_time]
    next_ai_timestamp = gap_exceeds_separation[0] if gap_exceeds_separation else future_timestamps[-1]

    return next_ai_timestamp if next_ai_timestamp != last_frame_timestamp else None

def track_detection_forward(video_path, ai_detect, save='off', prefix = None):
    """
    Track the ball forward in the video using the last available ai detection.

    Parameters:
        video_path (str): Path to the video file.
        ai_detect (dict): Dictionary with timestamps as keys and bounding boxes as values.

    Returns:
        dict: A dictionary with timestamps and bounding boxes of the tracked ball.
    """
    if not ai_detect:
        print("No ai detections provided.")
        return {}

    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return {}, None

    forward_track = {}
    fps = cap.get(cv2.CAP_PROP_FPS)
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    last_frame_timestamp_ms = int((num_frames-1) / fps * 1000)
    ts_separation = int(1 / fps * 1000 * 1.10)  # Safety factor

    while True:
        ret, _ = cap.read()
        if not ret:
            break

        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))

        if timestamp_ms in ai_detect:
            # Skip frames where ai detections are already available
            continue

        # Find future ai detection timestamps
        future_timestamps = [ts for ts in ai_detect if ts > timestamp_ms]
        future_timestamps.sort()

        # Determine next ai timestamp
        next_ai_timestamp = find_next_ai_detection(ai_detect, timestamp_ms, last_frame_timestamp_ms, ts_separation)

        # Handle case where no previous ai detection is available
        previous_timestamps = [ts for ts in ai_detect if ts < timestamp_ms]
        if previous_timestamps:
            closest_ai_timestamp = max(previous_timestamps)
        else:
            if next_ai_timestamp:
                next_ai_frame_index = int(round(next_ai_timestamp / 1000 * fps))
                cap.set(cv2.CAP_PROP_POS_FRAMES, next_ai_frame_index)
                continue
            else:
                break

        # Retrieve and set frame to the closest ai detection
        ai_frame_index = int(round(closest_ai_timestamp / 1000 * fps))
        cap.set(cv2.CAP_PROP_POS_FRAMES, ai_frame_index)
        ret, ai_frame = cap.read()
        if not ret:
            print(f"Failed to read frame at index {ai_frame_index}.")
            continue

        # Initialize the tracker with the ai bounding box
        x1, y1, x2, y2 = ai_detect[closest_ai_timestamp]
        ai_bbox = (x1, y1, x2 - x1, y2 - y1)
        tracker = init_tracker(ai_frame, ai_bbox)

        # Track the ball forward
        while True:
            next_ret, next_frame = cap.read()
            if not next_ret:
                break

            next_bbox = update_tracker(tracker, next_frame)
            next_timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
            if next_bbox and (next_ai_timestamp is None or next_timestamp_ms <= next_ai_timestamp):
                x1, y1, w, h = next_bbox
                x2 = x1 + w
                y2 = y1 + h
                forward_track[next_timestamp_ms] = (x1, y1, x2, y2)
            else:
                break

        if next_ai_timestamp:
            next_ai_frame_index = int(round(next_ai_timestamp / 1000 * fps))
            cap.set(cv2.CAP_PROP_POS_FRAMES, next_ai_frame_index)
        else:
            break

    if num_frames > 0:
        retention_rate = round(len(set(ai_detect.keys()) | set(forward_track.keys()))/ num_frames * 100, 1)
        print(f'Retention rate = {retention_rate} %')

    # Save detections if specified
    if save.lower() == 'on':
        file_name = f"{prefix}_forward_track_detections.pkl" if prefix else "forward_track_detections.pkl"
        file_path = os.path.expanduser('~/street/data_results/' + file_name)
        try:
            with open(file_path, 'wb') as file:
                pickle.dump(forward_track, file)
            print(f"Detections saved to {file_path}")
        except Exception as e:
            print(f"Error saving detections: {e}")

    # Release the video capture object
    cap.release()
    return forward_track

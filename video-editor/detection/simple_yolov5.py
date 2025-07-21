import cv2
import torch
import pandas as pd
import pickle
import os

def detect_objects_yolo(frame, model):
    """
    Detect objects in a frame using YOLOv5 model.
    
    Parameters:
        frame (ndarray): The video frame as a NumPy array.
        model (torch.nn.Module): The YOLOv5 model.

    Returns:
        DataFrame: Pandas DataFrame with bounding boxes, class ids, and scores.
    """
    results = model(frame)
    return results.pandas().xyxy[0]  # Returns a DataFrame with columns: xmin, ymin, xmax, ymax, name, confidence

def detect_sports_ball_yolo(video_path, save='off', prefix = None, model_size = 'x', confidence = 0.5):
    """
    Detects 'sports ball' in a video file and returns a dictionary of timestamps and bounding box coordinates.

    Parameters:
        video_path (str): Path to the video file.
        save (str): Whether to save the results to a file ('on' or 'off').

    Returns:
        dict: A dictionary where keys are timestamps (milliseconds) and values are bounding box coordinates (x1, y1, x2, y2).
    """
    if not os.path.isfile(video_path):
        print(f"Error: Video file does not exist: {video_path}")
        return {}

    model_path = os.path.expanduser('~/street/detection/yolov5' + model_size + '.pt')
    print(model_path)
    try:
        # Attempt to load a larger YOLOv5 model and use GPU if available
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {device}")
        model = torch.hub.load('ultralytics/yolov5', 'yolov5' + model_size, device = device)
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

    # Open video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return {}

    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    yolo_detect = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        results = detect_objects_yolo(frame, model)
        print(f'Timestap {timestamp_ms}')

        if not results.empty:
            for _, row in results.iterrows():
                if row['name'] == 'sports ball' and row['confidence'] > confidence:
                    x1, y1, x2, y2 = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
                    yolo_detect[timestamp_ms] = (x1, y1, x2, y2)
                    break  # Assuming we only need one detection per frame

    if num_frames > 0:
        retention_rate = round(len(yolo_detect) / num_frames * 100, 1)
        print(f'Retention rate = {retention_rate} %')

    if save.lower() == 'on':
        file_name = f"{prefix}_simple_yolo_detections.pkl" if prefix else "simple_yolo_detections.pkl"
        file_path = os.path.expanduser('~/street/data_results/' + file_name)
        try:
            # Save the YOLO detections to the file
            with open(file_path, 'wb') as file:
                pickle.dump(yolo_detect, file)
            print(f"Detections saved to {file_path}")
        except Exception as e:
            print(f"Error saving detections: {e}")

    cap.release()
    
    return yolo_detect

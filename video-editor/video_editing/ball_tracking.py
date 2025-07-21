'''
Functions to provide automatic ball tracking in a video.
'''

from street.detection.simple_yolov5 import detect_sports_ball_yolo
from street.detection.manual_enhance import manually_enhance_ai_detections
from street.tracking.forward_track import track_detection_forward
from street.tracking.backward_track import track_detection_backward
from street.tracking.merge_results import merge_tracking_results
#from street.tracking.show_results import *


import time
import os
import pickle


def track_ball_in_clip(video_path):
    '''
    Function to track the ball in a video clip

    Input:
    video_clip: Video clip to track the ball in

    Output:
    ball_path: Path of the ball as a list of dictionaries with timestamp, x and y coordinates
    ball_path = [{'timestamp': 0, 'x': 0, 'y': 0},
                {'timestamp': 1000, 'x': 100, 'y': 100}]
    '''

    ball_path = [{'timestamp': 0, 'x': 0, 'y': 0},
                {'timestamp': 1000, 'x': 100, 'y': 100}]
    
    start_time = time.time()
    prefix = 'test'


    ai_detections_file_path = os.path.expanduser('~/street/data_results/' + prefix + '_simple_yolo_detections.pkl')
    
    if os.path.isfile(ai_detections_file_path):
        with open(ai_detections_file_path, 'rb') as file:
            ai_detect = pickle.load(file)
    else:
        ai_detect = detect_sports_ball_yolo(video_path, save='on', prefix= prefix)
    print('Time taken for AI detection: ', time.time() - start_time)

    # FORWARD TRACKING
    forward_detections_file_path = os.path.expanduser('~/street/data_results/' + prefix + '_forward_track_detections.pkl')
    if os.path.isfile(forward_detections_file_path):
        with open(forward_detections_file_path, 'rb') as file:
            forward_track = pickle.load(file)
    else:
        forward_track = track_detection_forward(video_path, ai_detect, save = 'on', prefix = prefix)
    print('Time taken for forward tracking: ', time.time() - start_time)

    # BACKWARD TRACKING
    backward_detections_file_path = os.path.expanduser('~/street/data_results/' + prefix + '_backward_track_detections.pkl')
    if os.path.isfile(backward_detections_file_path):
        with open(backward_detections_file_path, 'rb') as file:
            backward_track = pickle.load(file)
    else:
        backward_track = track_detection_backward(video_path, ai_detect, save = 'on', prefix = prefix)
    print('Time taken for backward tracking: ', time.time() - start_time)

    # MERGE TRACKING RESULTS
    merged_detections_file_path = os.path.expanduser('~/street/data_results/' + prefix +  '_merged_tracks_detections.pkl')
    if os.path.isfile(merged_detections_file_path):
        with open(merged_detections_file_path, 'rb') as file:
            merged_tracks = pickle.load(file)
    else:
        # Forward merging
        merged_tracks = merge_tracking_results(video_path, ai_detect, forward_track, 'forward', save='on', prefix = prefix)
        # Backward merging
        merged_tracks = merge_tracking_results(video_path, ai_detect, backward_track, 'backward', save='on', prefix = prefix)
    print('Time taken for merging forward tracking: ', time.time() - start_time)


    # MANUAL ENHANCEMENT
    manual_ai_detections_file_path = os.path.expanduser('~/street/data_results/' + prefix +  '_manual_ai_detections.pkl')
    if os.path.isfile(manual_ai_detections_file_path):
        with open(manual_ai_detections_file_path, 'rb') as file:
            manual_ai_detect = pickle.load(file)
    else:
        manual_ai_detect, num_retention_frames = manually_enhance_ai_detections(video_path, ai_detect, merged_tracks, save = 'on', prefix = prefix)
        pass


    all_tracks = merged_tracks
    # Convert the AI detections to a single point ball path
    ball_path = []
    ball_path_timestamps = []
    for ts_key in all_tracks.keys():
        x_min, y_min, x_max, y_max = all_tracks[ts_key]
        x = (x_min + x_max) / 2
        y = (y_min + y_max) / 2
        ts_x_y = {'timestamp': ts_key, 'x': x, 'y': y}
        ball_path_timestamps.append(ts_key)
        ball_path.append(ts_x_y)
    
    print('Ball path timestamps:',sorted(ball_path_timestamps))
    return ball_path
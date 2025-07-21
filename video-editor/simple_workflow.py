import os
from detection.simple_yolov5 import *
from detection.manual_enhance import *
from tracking.forward_track import *
from tracking.backward_track import *
from tracking.merge_results import *
from tracking.show_results import *
import time

def main():
    #video_path = os.path.expanduser('~/Downloads/street_vid_001.mp4')
    #video_path = os.path.expanduser('~/Downloads/Trafford Arena Bangalore - September 1, 2024. Goal Highlights.mp4')
    #video_path = os.path.expanduser('~/Downloads/Rush Arena Bangalore - August 31, 2024. Goal Highlights.mp4')
    #video_path = os.path.expanduser('~/Downloads/Germans_street_vid_001.mp4')
    #video_path = os.path.expanduser('~/Downloads/girl_beach_street_vid_001.mp4')
    #video_path = os.path.expanduser('~/Downloads/girl_indoor_street_vid_001.mp4')
    video_path = os.path.expanduser('~/Downloads/Trafford Arena Bangalore - October 4, 2024. Extended Highlights.mp4')
    
    #prefix = 'kids'
    #prefix = 'trafford'
    #prefix = 'rush'
    #prefix = 'germans'
    #prefix = 'girl_beach'
    #prefix = 'girl_indoor'
    prefix = 'trafford_october'

    confidence = 0.5
    thickness = 2

    #start_time = time.time()
    #ai_detect = detect_sports_ball_yolo(video_path, save = 'on', prefix = prefix, confidence = confidence)
    ai_detections_file_path = os.path.expanduser('~/street/data_results/' + prefix + '_simple_yolo_detections.pkl')
    with open(ai_detections_file_path, 'rb') as file:
        ai_detect = pickle.load(file)
    #end_time = time.time()
    #print(f"ai detect time is : {(end_time - start_time)/60:.1f} minutes")

    #start_time = time.time()
    #forward_track = track_detection_forward(video_path, ai_detect, save = 'on', prefix = prefix)
    '''forward_detections_file_path = os.path.expanduser('~/street/data_results/' + prefix + '_forward_track_detections.pkl')
    with open(forward_detections_file_path, 'rb') as file:
        forward_track = pickle.load(file)'''
    #end_time = time.time()
    #print(f"forward track processing time is : {(end_time - start_time)/60:.1f} minutes")
    
    #start_time = time.time()
    #backward_track = track_detection_backward(video_path, ai_detect, save = 'on', prefix = prefix)
    '''backward_detections_file_path = os.path.expanduser('~/street/data_results/' + prefix + '_backward_track_detections.pkl')
    with open(backward_detections_file_path, 'rb') as file:
        backward_track = pickle.load(file)'''
    #end_time = time.time()
    #print(f"backward track time is : {(end_time - start_time)/60:.1f} minutes")

    #start_time = time.time()
    #merged_tracks = merge_tracking_results(video_path, ai_detect, forward_track, 'forward', save='on', prefix = prefix)
    merged_detections_file_path = os.path.expanduser('~/street/data_results/' + prefix +  '_merged_tracks_detections.pkl')
    with open(merged_detections_file_path, 'rb') as file:
        merged_tracks = pickle.load(file)
    #end_time = time.time()
    #print(f"merging takes : {(end_time - start_time)/60:.1f}")
    
    #start_time = time.time()
    #manual_ai_detect, num_retention_frames = manually_enhance_ai_detections(video_path, ai_detect, merged_tracks, save = 'on', prefix = prefix, thickness = thickness)
    '''manual_ai_detections_file_path = os.path.expanduser('~/street/data_results/' + prefix +  '_manual_ai_detections.pkl')
    with open(merged_detections_file_path, 'rb') as file:
        manual_ai_detect = pickle.load(file)'''
    #end_time = time.time()
    #print(f"manual enhancement takes : {(end_time - start_time)/60:.1f}")
    
    #start_time = time.time()
    #manual_forward_track = track_detection_forward(video_path, manual_ai_detect, save = 'on', prefix = prefix + '_manual')
    '''manual_forward_detections_file_path = os.path.expanduser('~/street/data_results/' + prefix + '_manual_forward_track_detections.pkl')
    with open(manual_forward_detections_file_path, 'rb') as file:
        manual_forward_track = pickle.load(file)'''
    #end_time = time.time()
    #print(f"forward track #2 : {(end_time - start_time)/60:.1f}")
    
    #start_time = time.time()
    #manual_backward_track = track_detection_backward(video_path, manual_ai_detect, save = 'on', prefix = prefix + '_manual')
    '''manual_backward_detections_file_path = os.path.expanduser('~/street/data_results/' + prefix + '_manual_backward_track_detections.pkl')
    with open(manual_backward_detections_file_path, 'rb') as file:
        manual_backward_track = pickle.load(file)'''
    #end_time = time.time()
    #print(f"backward track #2 : {(end_time - start_time)/60:.1f}")
    
    #start_time = time.time()
    #manual_merged_tracks = merge_tracking_results(video_path, manual_ai_detect, manual_forward_track, 'forward', save='on', prefix = prefix + '_manual')
    manual_merged_detections_file_path = os.path.expanduser('~/street/data_results/' + prefix +  '_manual_merged_tracks_detections.pkl')
    with open(manual_merged_detections_file_path, 'rb') as file:
        manual_merged_tracks = pickle.load(file)
    #end_time = time.time()
    #print(f"merging #2 : {(end_time - start_time)/60:.1f}")
    
    show_tracking_results(video_path, manual_merged_tracks, 'blue', merged_tracks, 'black', ai_detect, 'red', save = 'on', minimum_thickness = 3, prefix = prefix)



if __name__ == "__main__":
    # Code to execute if the script is run directly
    main()

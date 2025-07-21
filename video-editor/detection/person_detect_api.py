import os, time
from google.cloud import videointelligence_v1 as videointelligence
from google.cloud.videointelligence_v1 import AnnotateVideoRequest
from moviepy.editor import VideoFileClip

from street.data_transfer.put_data_into_gcp_bucket import upload_file_to_gcp_bucket

from google.protobuf.json_format import MessageToDict
import json
import cv2
import numpy as np
from collections import defaultdict
import bisect


def get_track_boxes_from_person_detections(person_detections):
    # Prepare a per-track mapping from time to bounding boxes, and include track IDs
    track_boxes = []
    for person_idx, person in enumerate(person_detections):
        for track_idx, track in enumerate(person.tracks):
            timestamps = []
            boxes = []
            for timestamped_object in track.timestamped_objects:
                time_offset = timestamped_object.time_offset.total_seconds()
                bbox = timestamped_object.normalized_bounding_box
                # Store time and bbox
                timestamps.append(time_offset)
                boxes.append(bbox)
            # Store per-track timestamps, boxes, and track ID
            if timestamps:
                # Added code: Include track ID
                if track_idx != 0:
                    track_id = f"{person_idx + 1}_{track_idx + 1}"
                else:
                    track_id = f"p{person_idx + 1}"
                track_boxes.append({'times': timestamps, 'boxes': boxes, 'track_id': track_id})
    return track_boxes

def visualize_person_detections(original_video_path, annotated_video_path, track_boxes):
    '''
    Takes in a video, list of person detection annotations and draws bounding boxes and writes file to video

    Input
    - video_file_path: str
    - person_detections: list of person detection annotations
    - annotated_video_file_path: str

    Video with bounding boxes is written to file

    Output:
    - None
    - Writes video to file: annotated_video_file_path
    '''
    print('Visualizing person detections...')
    # Load the video
    clip = VideoFileClip(original_video_path)

    # write track boxes to a file
    #with open('./test_and_delete/track_boxes.json', 'w') as f:
    #    json.dump(track_boxes, f)

    # Function to interpolate bounding boxes
    def interpolate_bbox(t, times, boxes):
        # If t is before the first time, no box
        if t <= times[0]:
            return None #boxes[0]
        # If t is after the last time, no box
        if t >= times[-1]:
            return None #boxes[-1]
        # Find position in the list
        idx = bisect.bisect_left(times, t)
        t0 = times[idx - 1]
        t1 = times[idx]
        bbox0 = boxes[idx - 1]
        bbox1 = boxes[idx]
        ratio = (t - t0) / (t1 - t0)
        # Interpolate bbox
        bbox = videointelligence.NormalizedBoundingBox()
        bbox.left = bbox0.left + (bbox1.left - bbox0.left) * ratio
        bbox.top = bbox0.top + (bbox1.top - bbox0.top) * ratio
        bbox.right = bbox0.right + (bbox1.right - bbox0.right) * ratio
        bbox.bottom = bbox0.bottom + (bbox1.bottom - bbox0.bottom) * ratio
        return bbox

    # Now, define a function to draw bounding boxes and track IDs on each frame
    def annotate(get_frame, t):
        frame = get_frame(t)
        frame = frame.copy()  # Make frame writable
        frame_height, frame_width, _ = frame.shape

        # Draw bounding boxes from each track
        for track in track_boxes:
            times = track['times']
            boxes = track['boxes']
            track_id = track['track_id']  # Get track ID

            bbox = interpolate_bbox(t, times, boxes)
            if not times or bbox is None:
                continue


            # bbox has normalized coordinates
            left = int(bbox.left * frame_width)
            top = int(bbox.top * frame_height)
            right = int(bbox.right * frame_width)
            bottom = int(bbox.bottom * frame_height)

            # Draw rectangle on frame
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            # Added code: Put track ID text on the bounding box
            label = f"{track_id}"
            cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, # Font size
                        (255, 255, 255), 2)

        return frame
    
    # Create a new clip with annotated frames
    annotated_clip = clip.fl(annotate, apply_to=['video'])

    # Write the annotated video
    annotated_clip.write_videofile(annotated_video_path, codec='libx264', audio_codec='aac')

    return None

def get_person_detection_annotations(gcs_uri):
    
    start_time = time.time()
    client = videointelligence.VideoIntelligenceServiceClient()
    # Configure the request
    config = videointelligence.PersonDetectionConfig(
        include_bounding_boxes=True,
        include_attributes=True,
        include_pose_landmarks=True
    )
    context = videointelligence.VideoContext(person_detection_config=config)
    
    # Start the asynchronous request
    # Create the AnnotateVideoRequest
    request = AnnotateVideoRequest(
        input_uri=gcs_uri,
        features=[videointelligence.Feature.PERSON_DETECTION],
        video_context=context  # Include the context to include bounding boxes
    )
    operation = client.annotate_video(request)
    

    print("\nProcessing video for person detection annotations.")
    
    result = None
    try:
        result = operation.result(timeout=300)
    except Exception as e:
        print(f"An error occurred: {e}")
        print('Trying again')
        result = operation.result(timeout=300)
    
    print(type(result))
    print("\nFinished processing.\n")
    print("Time to process = ", round(time.time()-start_time),' seconds')

    annotation_result = result.annotation_results[0]
    print(type(annotation_result))
    person_detections = annotation_result.person_detection_annotations
    print(type(person_detections))
    print(len(person_detections),'person detections')

    return person_detections

def get_gcs_uri(clip):

    local_file_folder = './test_and_delete/'
    clip_file_name = 'clip_for_tracks.mp4'

    clip.write_videofile(local_file_folder + clip_file_name, 
                         codec='libx264', audio_codec='aac')
    print('Clip written to local successfully.')

    # Write the clip file to the GCS bucket
    bucket_name = "street-bucket"
    destination_folder = 'test_and_delete/'

    destination_blob_name = destination_folder + clip_file_name
    local_file_path = local_file_folder + clip_file_name

    upload_file_to_gcp_bucket(bucket_name, 
                              local_file_path, 
                              destination_blob_name)
    
    print(f'Clip written to GCS successfully: {bucket_name}/{destination_blob_name}')

    gcs_input_uri = f'gs://{bucket_name}/{destination_blob_name}'

    return gcs_input_uri

def get_track_boxes_from_clip(clip):

    gcs_input_uri = get_gcs_uri(clip)
    
    start_time = time.time()

    person_detections = get_person_detection_annotations(gcs_input_uri)
    
    track_boxes = get_track_boxes_from_person_detections(person_detections)

    print('Time taken to get track boxes: ', round(time.time() - start_time), ' seconds')  

    return track_boxes

def main():
    import os
    print(os.getcwd())

    # Define input video paths
    file_name = 'bellandur_blast.mp4'
    input_video_path = './data/intro_clips/' + file_name

    # Define output video paths
    test_and_delete_folder = './test_and_delete/'
    output_annotated_file_name = 'bellandur_blast_annotated.mp4'


    # Create a subclip using MoviePy
    print('Creating subclip...')
    clip = VideoFileClip(input_video_path)

    track_boxes = get_track_boxes_from_clip(clip)

    output_annotated_video_path = test_and_delete_folder + output_annotated_file_name

    visualize_person_detections(input_video_path, 
                                output_annotated_video_path,
                                track_boxes)

    return None

if __name__ == "__main__":
    main()
'''
Functions to provide automated people tracking in a video.
'''

import time, os, ast

from google.cloud import videointelligence_v1 as videointelligence
from google.cloud.videointelligence_v1 import AnnotateVideoRequest

from moviepy.editor import VideoFileClip

from street.data_transfer.put_data_into_gcp_bucket import upload_file_to_gcp_bucket

from street.detection.person_detect_api import get_track_boxes_from_clip
from street.detection.person_detect_api import visualize_person_detections


'''
def visualize_track_people(video_path, people_tracks, write_to_file = False):
    
    Creates a bounding box visualization of people tracks in a video.

    Input:
    - video_path: str
    - people_tracks: list of people tracks (returned from the Google Video Intelligence API)
    - write_to_file: bool

    Output:
    - video_with_annotations: Video file with bounding boxes around people tracks
    

    video_with_annotations = None
    if write_to_file:
        video_with_annotations.write_videofile('./test_and_delete/people_tracks.mp4')
    
    return video_with_annotations
    '''
def take_user_input():
    # Take user input: 1 (or more) track_id or pass
    # If the user presses enter, return None
    # Else return the string they entered
    user_input = input("Enter 1 (or more) track_id or press Enter to pass: ").strip()
    if user_input == '':
        return None
    else:
        '''
        Inputs:
        - single_track for software_camera
        - multiple_tracks for replay
        '''
        return user_input # .split(',') removed because the input is not a comma separated list

    
def write_clip_to_gcs_test_and_delete(video_path, clip_file_name = 'test.mp4'):
    '''
    Function to write a video clip to the GCS bucket directly to the test_and_delete folder
    '''
    bucket_name = "street-bucket"
    destination_folder = 'test_and_delete/'
    destination_blob_name = destination_folder + clip_file_name

    local_file_path = video_path

    upload_file_to_gcp_bucket(bucket_name, local_file_path, destination_blob_name)
    print(f'Clip written to GCS: {bucket_name}/{destination_blob_name}')

    gcs_input_uri = f'gs://{bucket_name}/{destination_blob_name}'
    return gcs_input_uri

def get_selected_people_track(track_boxes, selected_people, start_time = None, end_time = None):
    """
    Filters track_boxes to include only the tracks with track_ids in selected_people.

    Parameters:
    - track_boxes: list of dictionaries with keys 'times', 'boxes', 'track_id'
    - selected_people: list of track_ids to select

    Returns:
    - selected_people_tracks: list of dictionaries from track_boxes where 'track_id' is in selected_people
    """
    # Initialize a list to hold the selected tracks
    selected_people_tracks = []

    # Iterate over all tracks in track_boxes
    for track in track_boxes:
        # Check if the track_id is in the list of selected people
        if track['track_id'] in selected_people:

            # If times to cut the clip are not provided, add the track as is
            if start_time is None and end_time is None:
                # Add the track to the selected_people_tracks list
                selected_people_tracks.append(track)

            else:
                # Check if the track is within the time range
                # Get the times and bounding boxes for the track within the start and end times
                times = track['times']
                bboxes = track['boxes']
                track_id = track['track_id']

                adjusted_times = []
                adjusted_bboxes = []

                for time, bbox in zip(times, bboxes):
                    if time >= start_time and time <= end_time:
                        adjusted_times.append(time)
                        adjusted_bboxes.append(bbox)
                
                adjusted_track = {'times': adjusted_times, 'boxes': adjusted_bboxes, 'track_id': track_id}
                # Add the track to the selected_people_tracks list
                selected_people_tracks.append(adjusted_track)

    return selected_people_tracks

def get_frames_from_combined_people_tracks(selected_people_tracks):
    '''
    Function to get list of dictionaries {'timestamp': timestamp, 
                                            'left': left,
                                            'top': top,
                                            'right': right,
                                            'bottom': bottom
                                            } 
                                            from the selected people tracks

    Input:
    - selected_people_tracks: list of dictionaries with keys 'times', 'boxes', 'track_id'

    Returns:
    - frames_with_timestamps: Sorted [by timestamp] list of dictionaries with keys 'timestamp', 'left', 'top', 'right', 'bottom'

    Approach:
    - Get the bounding boxes from the selected people tracks

    '''
    # Dictionary to hold frames grouped by timestamp
    frames_by_timestamps = {}

    # Iterate over each selected track
    for track in selected_people_tracks:
        times = track['times']
        boxes = track['boxes']

        # For each timestamp and corresponding bounding box
        for time, box in zip(times, boxes):
            # Calculate the center of the bounding box
            left = box.left
            top = box.top
            right = box.right
            bottom = box.bottom

            # Add position to the list for this timestamp
            if time not in frames_by_timestamps:
                frames_by_timestamps[time] = {'left_list': [], 'top_list': [], 'right_list': [], 'bottom_list': []}
            
            frames_by_timestamps[time]['left_list'].append(left)
            frames_by_timestamps[time]['top_list'].append(top)
            frames_by_timestamps[time]['right_list'].append(right)
            frames_by_timestamps[time]['bottom_list'].append(bottom)
        # End of time, box loop
    # End of selected_people_tracks loop
    
    # Create the people_path by averaging positions at each timestamp
    frame_path = []
    for time in sorted(frames_by_timestamps.keys()):
        left_list = frames_by_timestamps[time]['left_list']
        top_list = frames_by_timestamps[time]['top_list']
        right_list = frames_by_timestamps[time]['right_list']
        bottom_list = frames_by_timestamps[time]['bottom_list']
        
        # Calculate the extreme ends of the bounding boxes
        left = min(left_list)
        top = min(top_list)
        right = max(right_list)
        bottom = max(bottom_list)

        frame_path.append({'timestamp': time, 
                            'left': left,'top': top,
                            'right': right, 'bottom': bottom})
    
    left_list = [frame['left'] for frame in frame_path]
    top_list = [frame['top'] for frame in frame_path]
    right_list = [frame['right'] for frame in frame_path]
    bottom_list =  [frame['bottom'] for frame in frame_path]
    
    # Calculate the extreme ends of the bounding boxes
    left = min(left_list)
    top = min(top_list)
    right = max(right_list)
    bottom = max(bottom_list)

    max_frame_path = []
    for time in sorted(frames_by_timestamps.keys()):
        max_frame_path.append({'timestamp': time, 
                               'left': left, 'top': top,
                               'right': right, 'bottom': bottom})
        
    return frame_path, max_frame_path

def get_average_camera_path_from_people_tracks(selected_people_tracks):
    """
    Combines the tracks of selected people into a single list of timestamped positions,
    averaging positions when multiple tracks overlap at the same timestamp.

    Parameters:
    - selected_people_tracks: list of dictionaries with keys 'times', 'boxes', 'track_id'

    Returns:
    - people_path: list of dictionaries with keys 'timestamp', 'x', 'y'
    """
    # Dictionary to hold positions grouped by timestamp
    positions_by_timestamp = {}

    # Iterate over each selected track
    for track in selected_people_tracks:
        times = track['times']
        boxes = track['boxes']

        # For each timestamp and corresponding bounding box
        for time, box in zip(times, boxes):
            # Calculate the center of the bounding box
            x_center = (box.left + box.right) / 2
            y_center = (box.top + box.bottom) / 2

            # Add position to the list for this timestamp
            if time not in positions_by_timestamp:
                positions_by_timestamp[time] = {'x_list': [], 'y_list': []}
            positions_by_timestamp[time]['x_list'].append(x_center)
            positions_by_timestamp[time]['y_list'].append(y_center)

    # Create the people_path by averaging positions at each timestamp
    people_path = []
    for time in sorted(positions_by_timestamp.keys()):
        x_list = positions_by_timestamp[time]['x_list']
        y_list = positions_by_timestamp[time]['y_list']
        x_avg = sum(x_list) / len(x_list)
        y_avg = sum(y_list) / len(y_list)
        people_path.append({'timestamp': time, 'x': x_avg, 'y': y_avg})

    return people_path

def get_camera_path_from_normalized_path(normalized_camera_path, frame_width, frame_height):
    '''
    Function to convert normalized camera path to pixel coordinates

    Input:
    - normalized_camera_path: List of dictionaries with timestamp, x and y coordinates normalized to the frame size
    - frame_width: Width of the frame
    - frame_height: Height of the frame

    Process:
    - Convert normalized x and y coordinates to pixel coordinates

    Output:
    - camera_path: List of dictionaries with timestamp, x and y coordinates in pixel coordinates
    '''
    camera_path = []
    for point in normalized_camera_path:
        timestamp = point['timestamp']
        x_normalized = point['x']
        y_normalized = point['y']
        # Convert normalized coordinates to pixel coordinates
        x_pixel = int(x_normalized * frame_width)
        y_pixel = int(y_normalized * frame_height)
        # Append the converted point to camera_path
        camera_path.append({
            'timestamp': timestamp * 1000,  # Convert to milliseconds
            'x': x_pixel,
            'y': y_pixel
        })
    return camera_path


def smooth_people_path(people_path, window_size=5):
    '''
    Smooth the people path with a moving average weighted by time
    
    Input:
    people_path: Single people_track object of the following format
    people_path  = [{'timestamp': 0, 'x': 0, 'y': 0},
                    {'timestamp': 1000, 'x': 100, 'y': 100}]

    Process:
    Create a weighted moving average of the people path based on how far the last few timestamps
    The timestamps are in milliseconds,look at the last 0.5 second of data

    Output:
    smooth_people_path: Single people_track object of the same format as input
    '''
    # Ensure the path is sorted by timestamp
    people_path.sort(key=lambda p: p['timestamp'])
    smooth_people_path = []
    n = len(people_path)

    for i in range(n):
        t_current = people_path[i]['timestamp']
        x_weighted_sum = 0.0
        y_weighted_sum = 0.0
        weight_sum = 0.0

        # Look back at previous points within the window size
        j = i
        while j >= 0 and (t_current - people_path[j]['timestamp']) <= window_size:
            delta_t = t_current - people_path[j]['timestamp']
            weight = 1.0 / (delta_t + 1e-6)  # Avoid division by zero
            x_weighted_sum += people_path[j]['x'] * weight
            y_weighted_sum += people_path[j]['y'] * weight
            weight_sum += weight
            j -= 1

        # Calculate weighted average
        x_avg = x_weighted_sum / weight_sum
        y_avg = y_weighted_sum / weight_sum

        # Append smoothed point
        smooth_people_path.append({
            'timestamp': t_current, 
            'x': x_avg,
            'y': y_avg
        })

    return smooth_people_path

def track_people_in_clip(clip_path):
    '''
    Function to get bounding boxes that track people in a video clip

    Input:
    video_clip: Video clip to track people in

    Process:
    Get track boxes from the Google Video Intelligence API
    Visualize track boxes on the original video
    Take user input: 1 (or more) track_id or pass

    Select required people tracks based on user input
    Create people_track object from all the people tracks

    Return people_track object

    Output:
    camera_path: Single camera_path object of the following format
    camera_path  = [{'timestamp': 0, 'x': 0, 'y': 0},
                    {'timestamp': 1000, 'x': 100, 'y': 100}]
    '''
    clip = VideoFileClip(clip_path)
    camera_path = None
    
    track_boxes = get_track_boxes_from_clip(clip)

    test_and_delete_folder = './test_and_delete/'
    output_annotated_file_name = 'all_people_tracks.mp4'
    output_annotated_video_path = test_and_delete_folder + output_annotated_file_name

    visualize_person_detections(clip_path, 
                                output_annotated_video_path,
                                track_boxes)
    
    # User watches the video to determine the track_ids of the people they want to track
    print('GO WATCH THE VIDEO [SINGLE TRACK]: ', output_annotated_video_path)

    #Take user input: 1 (or more) track_id or pass
    os.system("echo -n '\a'")  # Triggers the system beep
    selected_people = take_user_input()

    if selected_people is None:
        people_path = None
        camera_path = people_path
    else:
        #Select required people tracks based on user input
        print('Selected people:', selected_people)
        selected_people_tracks = get_selected_people_track(track_boxes, selected_people)
        
        #Create people_track object from all the people tracks
        print('Combining people tracks...')
        camera_path = get_average_camera_path_from_people_tracks(selected_people_tracks)

        # Get the frame size of the video clip
        original_frame_width = clip.size[0]
        original_frame_height = clip.size[1]
        camera_path = get_camera_path_from_normalized_path(camera_path, original_frame_width, original_frame_height)

        # Smooth the people path with a moving average weighted by time
        # people_path = smooth_people_path(people_path)

    # Return camera_path object
    return camera_path

def parse_people_track_selection_string(input_string):
    '''
    Input:
    - input_string: String in the format "[start_time, [p1, p2, ...], time, [p1, p2, ...], end_time]"
    Output:
    - List of tuples [(people_list, start_time, end_time), ...]
    '''
    # Convert the string to a list
    try:
        # Step 1: Replace curly quotes with straight quotes
        # Double curly quotes
        input_string = input_string.replace("“", "\"").replace("”", "\"")
        # Single curly quotes (in case they show up)
        input_string = input_string.replace("‘", "'").replace("’", "'")

        parsed_data = ast.literal_eval(input_string)
        if isinstance(parsed_data, list):
            return parsed_data
        else:
            raise ValueError("Input is not a valid list format.")
    except (ValueError, SyntaxError) as e:
        raise ValueError(f"Invalid input format: {e}")
    
def process_people_tracks_in_video_sections(input_data):

    times = input_data[::2]
    people = input_data[1::2]

    output_data = []
    print(times)
    print(people)

    for i in range(len(times)-1):
        people_list = people[i]
        section_start = times[i]
        section_end = times[i + 1] - 0.5
        
        output_data.append((people_list, section_start, section_end))
        
    return output_data

def track_multiple_people_in_clip(clip_path):

    '''
    Function to get bounding boxes that track multiple people in a video clip

    Input:
    video_clip: Video clip to track people

    Process:
    Get track boxes from the Google Video Intelligence API
    Visualize track boxes on the original video

    Take user input: Multiple track_id or pass
    Format: [start_time, [p1, p2, ...], time, [p1, p2, ...], end_time]

    Cut the video by the times in the user input

    Select required people tracks in each section

    Find the frame to capture over each of the frames in the video
    Fit frames into a constant [original] size frame

    Return the video clip with the selected people tracks

    Output:
    multi_person_video_clip: Single camera_path object of the following format
    '''
    clip = VideoFileClip(clip_path)
    print('File for tracking: ', clip_path)

    #call_api = input("Do you want to call the API to get the track boxes? (Enter n to skip): ")

    #if call_api != 'n':
    track_boxes = get_track_boxes_from_clip(clip)

    test_and_delete_folder = './test_and_delete/'
    output_annotated_file_name = 'all_people_tracks.mp4'
    output_annotated_video_path = test_and_delete_folder + output_annotated_file_name

    visualize_person_detections(clip_path, 
                                output_annotated_video_path,
                                track_boxes)

    # User watches the video to determine the track_ids of the people they want to track
    print('GO WATCH THE VIDEO [MULTI TRACK]: ', output_annotated_video_path)

    #Take user input: 1 (or more) track_id or pass
    os.system("echo -n '\a'")  # Triggers the system beep

    # Input format: [start_time, [p1, p2, ...], time, [p1, p2, ...], end_time]
    people_track_timeline = None
    try:
        people_track_timeline_string = take_user_input()
        if people_track_timeline_string is None:
            return None, None, None
        people_track_timeline = parse_people_track_selection_string(people_track_timeline_string)
    except ValueError as e:
        print(f"Error: {e}")
        print('ONLY ONE MORE TRY')
        people_track_timeline_string = take_user_input()
        people_track_timeline = parse_people_track_selection_string(people_track_timeline_string)
    
    frame_path = []
    max_frame_path = []

    if people_track_timeline_string is None:
        return None
    else:

        # Parse the user input
        if people_track_timeline is None:
            people_track_timeline = parse_people_track_selection_string(people_track_timeline_string)

        # Process the user input
        people_track_sections = process_people_tracks_in_video_sections(people_track_timeline)

        # Select required people tracks in each section
        for people_list, start_time, end_time in people_track_sections:

            people_tracks = get_selected_people_track(track_boxes, people_list,
                                                      start_time, end_time)

            # Find the frame to capture over each of the frames in the video
            # Fit frames into a constant [original] size frame
            combined_people_frame_path, max_frame = get_frames_from_combined_people_tracks(people_tracks)
            frame_path.extend(combined_people_frame_path)
            max_frame_path.extend(max_frame)

    # Return frame_path
    # frame_path = [{'timestamp': 0, 'left': 0, 'top': 0, 'right': 0, 'bottom': 0},...]

    print('\n===========FRAME PATH SELECTION COMPLETE===========\n')
    #print(frame_path[:5])
    #print(frame_path[-5:])

    # Write people_track_timeline_string to a file
    # Find the available ripley file number
    i = 0
    file_found = True
    while file_found:
        if not os.path.isfile('./test_and_delete/temp_game_files/people_track_timeline_' + str(i) + '.txt'):
            file_found = False
            break
        else:
            i += 1
    people_track_timeline_file_path = test_and_delete_folder + 'temp_game_files/people_track_timeline_' + str(i) + '.txt'
    with open(people_track_timeline_file_path, 'w') as file:
        file.write(people_track_timeline_string)
    
    return frame_path, max_frame_path, track_boxes

def main():

    # Read the video clip
    file_path = './data/game-recordings/Game27_1006/Game27_1006_p1.mp4'
    clip_start = 5*60 + 42
    clip_end = clip_start + 3
    video_clip = VideoFileClip(file_path).subclip(clip_start, clip_end)

    # Write clip to temporary file
    video_clip_path = './test_and_delete/cut_clip.mp4'
    annotated_video_path = './test_and_delete/people_tracks_clip.mp4'

    video_clip.write_videofile(video_clip_path)

    # Track people in the video clip
    people_path = track_people_in_clip(video_clip_path)

    
    return None

if __name__ == "__main__":
    main()
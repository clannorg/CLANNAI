import cv2
import numpy as np
from bidict import bidict
import math
from tracking.show_results import *
import pickle

def create_frame_index_to_timestamp_map(video_path):
    """
    Create a bidirectional mapping between frame indices and timestamps using OpenCV's actual timestamps.

    Parameters:
        video_path (str): Path to the video file.

    Returns:
        bidict: A bidirectional dictionary mapping frame indices to timestamps (in milliseconds).
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Error opening video file: {video_path}")
    
    try:
        indx_to_ts_map = bidict()
        frame_index = 0
        while True:
            ret = cap.grab()
            if not ret:
                break
            
            # Get the current timestamp from OpenCV (in milliseconds)
            timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
            indx_to_ts_map[frame_index] = timestamp_ms
            frame_index += 1
    
    finally:
        cap.release()

    return indx_to_ts_map

def create_four_click_dynamic_bounding_box_callback():
    """
    Creates a mouse callback function to dynamically update the bounding box using closure variables
    for storing the clicks and current mouse position.

    Returns:
        mouse_callback (function): The OpenCV mouse callback function.
        get_clicks (function): A function to retrieve the clicks and mouse position.
    """
    mouse_clicks = []
    current_mouse_position = None

    def mouse_callback(event, x, y, flags, param):
        nonlocal mouse_clicks, current_mouse_position

        if event == cv2.EVENT_LBUTTONDOWN and len(mouse_clicks) < 4:
            mouse_clicks.append((x, y))

        elif event == cv2.EVENT_MOUSEMOVE and len(mouse_clicks) >= 2:
            current_mouse_position = (x, y)   

    def get_clicks():
        return mouse_clicks, current_mouse_position
    
    def reset_clicks():
        nonlocal mouse_clicks, current_mouse_position
        mouse_clicks = []
        current_mouse_position = None

    return mouse_callback, get_clicks, reset_clicks

def define_bounding_box(clicks, current_mouse_position):
    """
    Define the bounding box based on up to four clicks: North, South, East, and West sides of the ball

    Parameters:
        clicks: list of tuples (x,y) where the clicks occured.
        current_mouse_position (tuple): Coordinates (x, y) of the current mouse position, for continuous box drawing.
        frame_shape (tuple): Shape of the video frame (height, width, channels).

    Returns:
        tuple: Bounding box coordinates (x1, y1, x2, y2).
    """
    if len(clicks) < 2:
        raise ValueError("There should be more than 2 clicks")
    
    x2 = current_mouse_position[0]
    a = clicks[0]
    b = clicks[1]
    x1 = int((a[0] + b[0])/2)
    if a[1] < b[1]:
        y1 = a[1]
        y2 = b[1]
    else:
        y1 = b[1]
        y2 = a[1]

    if len(clicks) == 3:
        x1 = clicks[2][0]
    elif len(clicks) == 4:
        x1 = clicks[2][0]
        x2 = clicks[3][0]
    if x1 > x2:
        p = x1
        x1 = x2
        x2 = p

    return (x1, y1, x2, y2)

def compare_bounding_boxes(box1, box2, tolerance=0.03):
    """
    Calculates the Intersection over Union (IoU) of two bounding boxes and 
    checks if their overlap exceeds a given tolerance.
    
    Parameters:
        box1 (tuple): Coordinates (x1, y1, x2, y2) of the first bounding box.
        box2 (tuple): Coordinates (x1, y1, x2, y2) of the second bounding box.
        tolerance (float): the amount of movement that is tolerated, the lower the tolerance, the smaller the 
                            object movements that are detected as a movement
    
    Returns:
        bool: True if IoU is greater than 1 - tolerance, False otherwise.
    """

    # Unpack coordinates
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2

    # Calculate the coordinates of the intersection box
    x1_inter = max(x1_1, x1_2)
    y1_inter = max(y1_1, y1_2)
    x2_inter = min(x2_1, x2_2)
    y2_inter = min(y2_1, y2_2)

    # Check for overlap
    if x1_inter >= x2_inter or y1_inter >= y2_inter:
        return False  # No overlap

    # Calculate intersection area
    inter_area = (x2_inter - x1_inter) * (y2_inter - y1_inter)

    # Calculate areas of both boxes
    area_box1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area_box2 = (x2_2 - x1_2) * (y2_2 - y1_2)

    # Calculate union area
    union_area = area_box1 + area_box2 - inter_area

    # Handle cases where the union area is zero (avoiding division by zero)
    if union_area == 0:
        return False

    # Calculate Intersection over Union (IoU)
    iou = inter_area / union_area

    # Return True if IoU exceeds the threshold, otherwise False
    return iou > (1 - tolerance)

def get_sphere_of_influence(timestamp, idx_ts_map, ai_detect, merged_tracks, forward_track = [], backward_track = []):
    
    current_index = idx_ts_map.inv[timestamp]
    all_ai_detect_timestamps_sorted = sorted(ai_detect.keys())
    ai_index = all_ai_detect_timestamps_sorted.index(timestamp)
    previous_ai_timestamp = all_ai_detect_timestamps_sorted[ai_index - 1] if ai_index > 0 else None
    next_ai_timestamp = all_ai_detect_timestamps_sorted[ai_index + 1] if ai_index < len(all_ai_detect_timestamps_sorted) - 1 else None
    
    all_merged_tracks_timestamps_sorted = sorted(merged_tracks.keys())
    current_merged_index = all_merged_tracks_timestamps_sorted.index(timestamp)
    last_post_merged_gap_ts = all_merged_tracks_timestamps_sorted[-1]
    first_pre_merged_gap_ts = all_merged_tracks_timestamps_sorted[0]
    for i in range(current_merged_index + 1, len(all_merged_tracks_timestamps_sorted)):
        if idx_ts_map.inv[all_merged_tracks_timestamps_sorted[i]] - idx_ts_map.inv[all_merged_tracks_timestamps_sorted[i-1]] > 1:
            last_post_merged_gap_ts = all_merged_tracks_timestamps_sorted[i-1]
            break
    for i in range(current_merged_index - 1, -1, -1):
        if - idx_ts_map.inv[all_merged_tracks_timestamps_sorted[i]] + idx_ts_map.inv[all_merged_tracks_timestamps_sorted[i+1]] > 1:
            first_pre_merged_gap_ts = all_merged_tracks_timestamps_sorted[i+1]
            break
    
    sphere_of_influence_left = timestamp
    sphere_of_influence_right = timestamp
    if not previous_ai_timestamp or first_pre_merged_gap_ts > idx_ts_map[idx_ts_map.inv[previous_ai_timestamp] + 1]:
        sphere_of_influence_left = first_pre_merged_gap_ts
    elif backward_track:
        tt = next((ts for ts in sorted(backward_track.keys(), reverse=True) if ts < timestamp and ts not in merged_tracks), None)
        sphere_of_influence_left = None if tt is None else max(idx_ts_map[idx_ts_map.inv[previous_ai_timestamp] + 1], idx_ts_map[idx_ts_map.inv[tt] + 1])
    elif forward_track:
        tt = next((ts for ts in sorted(forward_track.keys()) if ts > previous_ai_timestamp and ts not in merged_tracks), None)
        sphere_of_influence_left = None if tt is None else min(idx_ts_map[idx_ts_map.inv[timestamp] - 1], idx_ts_map[idx_ts_map.inv[tt] - 1])
    else:
        previous_ai_index = idx_ts_map.inv[previous_ai_timestamp]
        sphere_of_influence_left = idx_ts_map[int((current_index + previous_ai_index)/2) + 1] #forward track bias

    if not next_ai_timestamp or last_post_merged_gap_ts < idx_ts_map[idx_ts_map.inv[next_ai_timestamp] - 1]:
        sphere_of_influence_right = last_post_merged_gap_ts
    elif forward_track:
        tt = next((ts for ts in sorted(forward_track.keys()) if ts > timestamp and ts not in merged_tracks), None)
        sphere_of_influence_right = None if tt is None else min(idx_ts_map[idx_ts_map.inv[next_ai_timestamp] - 1], idx_ts_map[idx_ts_map.inv[tt] - 1])
    elif backward_track:
        tt = next((ts for ts in sorted(backward_track.keys()) if ts < next_ai_timestamp and ts not in merged_tracks), None)
        sphere_of_influence_right = None if tt is None else max( idx_ts_map[idx_ts_map.inv[timestamp] + 1], idx_ts_map[idx_ts_map.inv[tt] + 1])
    else:
        next_ai_index = idx_ts_map.inv[next_ai_timestamp]
        sphere_of_influence_right = idx_ts_map[int((current_index + next_ai_index)/2)] #forward track bias consistent

    return (sphere_of_influence_left, sphere_of_influence_right)

def classify_ai_detections(video_path, index_to_ts_map, ai_detect, merged_tracks, *args, thickness = 2, tolerance = 0.02):
    ''' try to classify the ai detections and set their sphere of influence
    by generating the ai_detect_classfied dictionary with timestamp : [bbox, True/False user verified, (a,b) tuple
    of the sphere of influence: the timestamps of the frames with a detection that originates from each ai detection 
    using the forward/backward track, ]'''

    # Process additional dictionaries and directions
    args_dict = {}

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
        args_dict[args[i+1].lower()] = (args[i])

    
    # Open the video file and check validity
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Error opening video file: {video_path}")

    # Calculate video duration in milliseconds
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    

    if fps <= 0:
        raise ValueError("Frames per second (fps) is zero or negative. Unable to determine video length.")
    
    total_duration_ms = int((num_frames / fps) * 1000)
    ai_detect_classified = {}
    sorted_ai_detect = sorted(ai_detect.keys())
    i = 0
    while i < len(sorted_ai_detect):
        i = max(0,i) # to go back (press 'b') on first frame
        ts = sorted_ai_detect[i]
        print(ts)
        previous_ts = index_to_ts_map[max(index_to_ts_map.inv[ts] - 1, 0)]
        next_ts = index_to_ts_map[min(index_to_ts_map.inv[ts] + 1, num_frames-1)]
        x1, y1, x2, y2 = ai_detect[ts]

        cap.set(cv2.CAP_PROP_POS_MSEC, ts)
        #cap.set(cv2.CAP_PROP_POS_FRAMES, index_to_ts_map.inv[ts])
        ret, frame = cap.read()

        if not ret:
            print(f"Error reading frame at index {index_to_ts_map.inv[ts]}")
            continue

        window_name = f"press enter for correct assesment, x to flip it, and b to go back"
        assessment = False
        color = corresponding_bgr_colors('red') #defaults to false assessent
        if (previous_ts in merged_tracks.keys() and next_ts in merged_tracks.keys() 
        and not compare_bounding_boxes(merged_tracks[previous_ts], merged_tracks[next_ts], tolerance = tolerance)):
            assessment = True
            color = corresponding_bgr_colors('green')
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
        cv2.imshow(window_name, frame)

        go_back = False
        while not go_back:
            key = cv2.waitKey(1)
        
            if key == 13:  # Enter key
                ai_detect_classified[ts] = [ai_detect[ts], assessment]
                break
            elif key == ord('x'):  # 'x' key
                ai_detect_classified[ts] = [ai_detect[ts], not assessment]
                break
            elif key == ord('b'):
                i -= 2
                go_back = True
        
        # Close the window
        cv2.destroyWindow(window_name)
        if not go_back:
            sphere_of_of_influence_left, sphere_of_influence_right = get_sphere_of_influence(ts, index_to_ts_map, ai_detect, merged_tracks)
            ai_detect_classified[ts].append((sphere_of_of_influence_left, sphere_of_influence_right))
        i += 1

    cap.release()  
    cv2.destroyAllWindows()  
    cv2.waitKey(1) 

    return ai_detect_classified

def create_manual_enhance(merged_tracks, ai_detect_classified, index_to_ts_map):
    
    num_frames = len(index_to_ts_map)
    manual_ai_detect = {}
    manual_enhance = []
    current_index = 0

    # Organizing the indices of frames that need manual enhancement
    while current_index < num_frames:
        current_ts = index_to_ts_map[current_index]
        print(current_ts)
        
        if current_ts in ai_detect_classified.keys():

            index_sphere_of_influence_left = index_to_ts_map.inv[ai_detect_classified[current_ts][2][0]] # get the sphere of influence as an index
            index_sphere_of_influence_right = index_to_ts_map.inv[ai_detect_classified[current_ts][2][1]] # get the sphere of influence as an index

            if ai_detect_classified[current_ts][1]:
                for i in range(index_sphere_of_influence_left, index_sphere_of_influence_right + 1):
                    manual_ai_detect[index_to_ts_map[i]] = merged_tracks[index_to_ts_map[i]]
            else:
                manual_enhance.extend(range(index_sphere_of_influence_left, index_sphere_of_influence_right + 1))
            
            current_index = index_sphere_of_influence_right + 1
            continue

        elif current_ts not in merged_tracks.keys():
            manual_enhance.append(current_index)
        
        current_index += 1
    
    if manual_enhance != sorted(manual_enhance): #check the algorithm is working correctly
        raise ValueError("The list is not sorted!")

    return manual_enhance, manual_ai_detect

def create_manual_enhance_chunks(manual_enhance):
    """
    Splits the `manual_enhance` list into chunks where consecutive frame indices are grouped together.
    A new chunk starts when the gap between two indices exceeds 1.

    Parameters:
        manual_enhance (list): A list of frame indices that need to be manually enhanced.

    Returns:
        list: A list of lists (chunks), where each sublist contains consecutive frame indices.
    """
    if not manual_enhance:
        return []

    chunks = []
    current_chunk = [manual_enhance[0]]

    for i in range(1, len(manual_enhance)):
        # Check if the current frame index is consecutive to the previous one
        if manual_enhance[i] - manual_enhance[i - 1] == 1:
            current_chunk.append(manual_enhance[i])
        else:
            chunks.append(current_chunk)
            current_chunk = [manual_enhance[i]]

    # Append the final chunk
    chunks.append(current_chunk)

    return chunks

def manually_enhance_ai_detections(video_path, ai_detect, merged_tracks, *args, save ='off', prefix = None, thickness = 2):
    

    index_to_ts_map = create_frame_index_to_timestamp_map(video_path)
    
    '''file_path = os.path.expanduser('~/street/data_results/' + prefix +  '_ai_detections_classified.pkl' if prefix else '~/street/data_results/_ai_detections_classified.pkl')
    with open(file_path, 'rb') as file:
        ai_detect_classified = pickle.load(file)'''
    ai_detect_classified = classify_ai_detections(video_path, index_to_ts_map, ai_detect, merged_tracks, *args)

    if save.lower() == 'on':
        file_name = f"/{prefix}_ai_detections_classified.pkl" if prefix else "ai_detections_classified.pkl"
        file_path = os.path.expanduser('~/street/data_results/' + file_name)
        try:
            with open(file_path, 'wb') as file:
                pickle.dump(ai_detect_classified, file)
            print(f"Detections saved to {file_path}")
        except Exception as e:
            print(f"Error saving detections: {e}")
            
    
    manual_enhance, manual_ai_detect = create_manual_enhance(merged_tracks, ai_detect_classified, index_to_ts_map)
    chunks = create_manual_enhance_chunks(manual_enhance)

    num_retention_frames = len(index_to_ts_map)

    # prompt the user to enter the number of frames between manual detections
    enhance_indices_spacing = 1 # prevending unbounded behavior, even though I do not see how that is even possible
    if chunks:
        print(f'There are {len(chunks)} chunks, with an average chunk length of {round(len(manual_enhance) / len(chunks))}')
        while True:
            try:
                enhance_indices_spacing = int(input('Enter the number of frames between manual detections: '))
                
                if enhance_indices_spacing <= 0:
                    print("Please enter a positive integer.")
                else:
                    break
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error opening video file.")
        return {}, 0

    # Processing chunks of frames
    for chunk in chunks:
        
        if len(chunk) <= 0:
            raise ValueError('Found an empty chunk')

        enhance_indices = []
        num_enhance_indices = int(len(chunk) / enhance_indices_spacing) + 1
        equalized_spacing = int(len(chunk) / num_enhance_indices) + 1
        first_index = math.ceil((len(chunk) % equalized_spacing) / 2) - 1
        enhance_indices.append(chunk[max(first_index, 0)])
        for i in range(num_enhance_indices - 1):
            first_index += equalized_spacing # first_index is no longer the first index, it becomes the second, and the third, etc.
            enhance_indices.append(chunk[first_index])

        for frame_index in enhance_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ret, frame = cap.read()
            ts = index_to_ts_map[frame_index]
            print(ts)
            if ts == 11500:
                print('stop')
            
            if not ret:
                print(f"Error reading frame at index {frame_index}")
                continue

            window_name = f"Click North, South, East and West side of the ball, enter to skip, and x to reset."
            cv2.imshow(window_name, frame)

            draw_red = False
            x1r , y1r, x2r, y2r = (0,0,0,0)
            if index_to_ts_map[frame_index] in ai_detect_classified.keys() and not ai_detect_classified[index_to_ts_map[frame_index]][1]:
                x1r , y1r, x2r, y2r = ai_detect_classified[index_to_ts_map[frame_index]][0]
                cv2.rectangle(frame, (x1r, y1r), (x2r, y2r), corresponding_bgr_colors('red'), thickness)
                draw_red = True

            # Set mouse callback
            mouse_callback, get_clicks, reset_clicks = create_four_click_dynamic_bounding_box_callback()
            cv2.setMouseCallback(window_name, mouse_callback)


            # Interaction loop for drawing bounding box
            while True:
                # Create a copy of the frame to draw the dynamic bounding box
                display_frame = frame.copy()
                if draw_red:
                    cv2.rectangle(frame, (x1r, y1r), (x2r, y2r), corresponding_bgr_colors('red'), thickness)

                clicks, current_mouse_position = get_clicks()

                if len(clicks) >= 2 and len(clicks) <= 3 and current_mouse_position:
                    x1, y1, x2, y2 = define_bounding_box(clicks, current_mouse_position)
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), corresponding_bgr_colors('green'), thickness)

                # Show updated frame
                cv2.imshow(window_name, display_frame)

                # Check for Enter key to skip or second click completion
                key = cv2.waitKey(1)

                if key == 13:  # Enter key press to skip
                    num_retention_frames -= 1
                    print("Skipping this frame.")
                    break

                if key == ord('x'):
                    reset_clicks()

                ### add possibility for esc to undo the box
                if len(clicks) == 4:
                    key = cv2.waitKey(3000)  # Brief pause for user confirmation
                    if key == ord('x'):
                        reset_clicks()
                    else:
                        x1, y1, x2, y2 = define_bounding_box(clicks, current_mouse_position)
                        manual_ai_detect[index_to_ts_map[frame_index]] = (x1, y1, x2, y2)
                        print(f"Bounding box saved: {(x1, y1, x2, y2)}")
                        break

            # Close the current frame window
            cv2.destroyWindow(window_name)

    if num_retention_frames > 0:
        retention_rate = round(len(manual_ai_detect) / num_retention_frames * 100, 1)
        print(f'Retention rate = {retention_rate} %')

    if save.lower() == 'on':
        file_name = f"{prefix}_manual_ai_detections.pkl" if prefix else "manual_ai_detections.pkl"
        file_path = os.path.expanduser('~/street/data_results/' + file_name)
        try:
            with open(file_path, 'wb') as file:
                pickle.dump(manual_ai_detect, file)
            print(f"Detections saved to {file_path}")
        except Exception as e:
            print(f"Error saving detections: {e}")

    cap.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1) 

    return manual_ai_detect, num_retention_frames

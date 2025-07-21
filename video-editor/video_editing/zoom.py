'''
This file deals with zoom functionality for the video editor.

Zoom will be used based on the position of the ball primarily
In some cases, player positions will be used to determine the zoom functionality
'''

from moviepy.editor import VideoClip, vfx, VideoFileClip
import math, os
import cv2 as cv
import bisect
import numpy as np
from vidstab import VidStab
import matplotlib.pyplot as plt

from street.video_editing.watermark import add_watermark

from street.video_editing.video_frames import VideoFrames
from street.video_editing.video_frames import simple_stabilize

from street.video_editing.video_effects import sharpen_image, smooth_image

def calculate_slope_degrees(p1, p2):
    """
    Calculate the slope in degrees between two points.
    
    Args:
        p1, p2 (tuple): Two points (x, y).
        
    Returns:
        float: Slope in degrees, range -90 to +90.
    """
    if p2[0] == p1[0]:  # Vertical line
        return 90 if p2[1] > p1[1] else -90
    slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
    return np.degrees(np.arctan(slope))

def group_points_by_slope_degrees(points, slope_threshold=10):
    """
    Group points into segments based on abrupt changes in slope (in degrees).
    
    Args:
        points (list of tuples): List of (x, y) points.
        slope_threshold (float): Threshold for significant slope change in degrees.
    
    Returns:
        list of lists: Groups of points forming segments.
    """
    segments = []
    current_segment = [points[0]]

    for i in range(1, len(points) - 1):
        slope1 = calculate_slope_degrees(points[i - 1], points[i])
        slope2 = calculate_slope_degrees(points[i], points[i + 1])
        if abs(slope2 - slope1) > slope_threshold:
            # If slope change exceeds threshold, start a new segment
            segments.append(current_segment)
            current_segment = [points[i]]
        else:
            current_segment.append(points[i])
    current_segment.append(points[-1])  # Add the last point to the final segment
    segments.append(current_segment)

    return segments

def convert_to_horizontal_lines(segments):
    """
    Convert sloped line segments to two horizontal lines, maintaining the number of points in each segment.
    
    Args:
        segments (list of lists): Groups of points forming segments.
    
    Returns:
        list of float: Modified y-values for the input segments.
    """
    modified_y_values = []

    for segment in segments:
        if len(segment) < 2:
            modified_y_values.extend([point[1] for point in segment])
            continue  # Add the segment and move on to the next one
        start_y = segment[0][1]
        end_y = segment[-1][1]

        # Divide segment into two parts with approximate half-lengths
        segment_length = len(segment)
        half_length = segment_length // 2

        # First half is assigned start_y, second half is assigned end_y
        modified_segment = [start_y] * half_length + [end_y] * (segment_length - half_length)

        # Check length and correct if necessary
        if len(modified_segment) < segment_length:
            # Add an extra point with end_y to match the original length
            modified_segment.append(end_y)
        elif len(modified_segment) > segment_length:
            # Remove the last point to match the original length
            modified_segment.pop()

        # Add the modified segment to the output
        assert len(modified_segment) == len(segment), f"Length mismatch: {len(modified_segment)} vs {len(segment)}"
        modified_y_values.extend(modified_segment)
    
    return modified_y_values

class CropResizeImage:
    def __init__(self, crop_width = None, crop_height = None):
        self.width = crop_width
        self.height = crop_height
    def __call__(self, image):
        '''
        Function to crop (from top left corner) and resize the image based on width and height in class initialization

        Input:
        - image: Image to crop and resize
        - width: Width to crop and resize the image
        - height: Height to crop and resize the image

        Output:
        - Image cropped and resized to the specified width and height
        '''

        # Get original image size
        original_height, original_width = image.shape[:2]
        #print('\n\nOriginal height:', original_height)
        #print('Original width:', original_width)

        # Crop the image to the specified width and height
        image = image[:self.height, :self.width]

        # Resize the image to the specified width and height
        # Interpolation method: cv2.INTER_AREA for shrinking
        # Interpolation method: cv2.INTER_CUBIC (slow) & cv2.INTER_LINEAR for zooming
        image = cv.resize(image, (original_width, original_height)) 
        
        return image

class MovingZoom:
    
    def __init__(self, path, frame_size = None):
        '''
        ball_path is a list of dictionaries with 'timestamp', 'x', 'y' coordinates to follow
        'timestamp' : in ms
        'x' : x pixel coordinate of the ball
        'y' : y pixel coordinate of the ball
        '''

        if frame_size is not None:
            self.ball_path = path #list of dictionaries with 'timestamp', 'x', 'y' coordinates to follow
            self.frame_size = frame_size #(width, height) of the zoom frame
            self.frame_path = None
        else:
            # Implies that frame_path is used
            self.frame_path = path # list of dictionaries with 'timestamp', 'left', 'top', 'right', 'bottom' coordinates to follow
            self.frame_size = None #(width, height) of the zoom frame
            self.ball_path = None
        return None
    
    def moving_zoom_with_frame_path(self, video_clip):
        '''
        Input:
        - video_clip: VideoClip object to apply the moving zoom effect

        Available variables:
        - self.frame_path: List of dictionaries with {'timestamp', 'left', 'top', 'right', 'bottom'} coordinates to follow
        self.frame_size: Holds the minimum frame edges to include relevant people in each frame
        Needs to expanded to get a reasonable frame at the correct aspect ratio


        Approach:
        - For each timestamp: create the final camera frame
            - Create the larger camera frame based on the minimum frame and the original aspect ratio
        - After the camera frames [per timestamp] are made
        - Loop through the video and interpolate the camera frames based on timestamp

        Output:
        - VideoClip object with the frame path based moving zoom effect applied
        '''
        def create_reel_frame(original_width, original_height, frame_box, reel_margin=0.1):
            '''
            Function to create the camera frame based on the minimum frame with the aspect ratio for an instagram reel (9:16)

            Input:
            - original_width: Width of the original image
            - original_height: Height of the original image

            - frame_box: Minimum frame margins to include relevant people [left, top, right, bottom]

            - reel_margin: Margin to include in the reel frame (default 10%)

            Output:
            - Final reel frame [left, top, right, bottom]

            Approach:
            Final reel frame needs to be centered around the frame box and have the aspect ratio of a reel
            - Compute 10% (or specified) reel margins (in absolute pixels)
            - Expand the bounding box by these margins

            - If the width goes wide in either, fit the width to the edges as necessary

            - Estimate reel height [with width fixed]
            - Height = 9/16 * Width
            - Find the height margins to include the reel height
            - Add the height margins to the bounding box

            Check that the reel frame is within the original frame vertically
            - If not, limit the frame to the original frame on the edges as necessary

            '''
            # Unpack the bounding box
            box_left, box_top, box_right, box_bottom = frame_box

            # Compute reel aspect ratio
            reel_aspect_ratio = 9 / 16 # width / height

            # Compute margins (in absolute pixels)
            margin_x = reel_margin * original_width
            margin_y = reel_margin * original_height

            # Expand the bounding box by these margins
            expanded_left = box_left - margin_x
            expanded_right = box_right + margin_x
            expanded_top = box_top - margin_y
            expanded_bottom = box_bottom + margin_y

            # Ensure the width fits within the original frame
            expanded_left = max(0, expanded_left)
            expanded_right = min(original_width, expanded_right)
            # Ensure the height fits within the original frame
            expanded_top = max(0, expanded_top)
            expanded_bottom = min(original_height, expanded_bottom)

            aspect_ratio = (expanded_right - expanded_left) / (expanded_bottom - expanded_top)

            # If the reel is too thin
            if aspect_ratio < reel_aspect_ratio:
                # Expand the width to match the aspect ratio
                reel_width = int((expanded_bottom - expanded_top) * reel_aspect_ratio)
                
                if reel_width >= original_width or expanded_right - expanded_left >= original_width:
                    expanded_left = 0
                    expanded_right = original_width
                else:
                    width_to_add = reel_width - (expanded_right - expanded_left)
                    while width_to_add > 0 and (expanded_left > 0 or expanded_right < original_width):
                        if expanded_left > 0:
                            expanded_left -= 1
                            width_to_add -= 1
                        if expanded_right < original_width:
                            expanded_right += 1
                            width_to_add -= 1
                # End of expanding width of the reel
            else: # If the reel is too wide

                # Calculate the reel height based on the expanded width
                reel_height = int((expanded_right - expanded_left) / reel_aspect_ratio)

                if reel_height >= original_height or expanded_bottom - expanded_top >= original_height:
                    expanded_top = 0
                    expanded_bottom = original_height
                else:
                    height_to_add = (reel_height - (expanded_bottom - expanded_top))
                    while height_to_add > 0 and (expanded_top > 0 or expanded_bottom < original_height):
                        if expanded_top > 0:
                            expanded_top -= 1
                            height_to_add -= 1
                        if expanded_bottom < original_height:
                            expanded_bottom += 1
                            height_to_add -= 1
                # End of expanding height of the reel

            '''
            # Calculate the reel height based on the expanded width
            reel_width = expanded_right - expanded_left
            reel_height = reel_width / reel_aspect_ratio

            # Center the height around the current vertical bounds
            height_margin = (reel_height - (expanded_bottom - expanded_top)) / 2
            expanded_top -= height_margin
            expanded_bottom += height_margin
            
            # Ensure the height fits within the original frame

            if expanded_top < 0:
                shift = -expanded_top
                expanded_top += shift
                expanded_bottom += shift
            if expanded_bottom > original_height:
                shift = expanded_bottom - original_height
                expanded_top -= shift
                expanded_bottom -= shift
                
            '''

            # Convert to integers for final frame coordinates
            expanded_left = int(round(expanded_left))
            expanded_top = int(round(expanded_top))
            expanded_right = int(round(expanded_right))
            expanded_bottom = int(round(expanded_bottom))

            reel_frame = [expanded_left, expanded_top, expanded_right, expanded_bottom]
            return reel_frame



        def create_full_frame(original_width, original_height, frame_box, min_frame_factor=0.3):
            '''
            Function to create the camera frame based on the minimum frame and maintains the original aspect ratio

            Input:
            - original_width: Width of the original image
            - original_height: Height of the original image

            - frame_box: Minimum frame margins to include relevant people [left, top, right, bottom]

            - min_frame_factor: Minimum frame factor to maintain in both dimensions

            Output:
            - Final camera frame [left, top, right, bottom]

            Approach:
            Final camera frame needs to be centered around the frame box and maintain the original aspect ratio
            - Compute 10% margins (in absolute pixels)
            - Expand the bounding box by these margins
            
            - Calculate the aspect ratio of the expanded bounding box
            - If too wide -> expand height to match based on the original aspect ratio
            - If too tall -> expand width to match based on the original aspect ratio

            - Get minimum width and height based on the minimum frame factor

            - Check that expanded width >= min_width and expanded height >= min_height
            - If below minimum, expand frame outward to the minimum width and height [Maintain aspect ratio]

            - Check frame against edges
            - If frame is outside the original frame, shift the frame to the edge of the original frame

            '''

            # Unpack the bounding box
            box_left, box_top, box_right, box_bottom = frame_box
            original_aspect_ratio = original_width / original_height

            # Compute 10% margins (in absolute pixels)
            margin_x = 0.1 * original_width
            margin_y = 0.1 * original_height

            # First expand the bounding box by these margins
            expanded_left   = box_left - margin_x
            expanded_right  = box_right + margin_x

            expanded_top    = box_top - margin_y
            expanded_bottom = box_bottom + margin_y

            # Calculate the aspect ratio of the expanded bounding box
            expanded_width  = expanded_right - expanded_left
            expanded_height = expanded_bottom - expanded_top
            expanded_frame_aspect_ratio = expanded_width / expanded_height

            # Enforce the minimum frame factor in both dimensions
            # If too wide
            if expanded_frame_aspect_ratio > original_aspect_ratio: # too wide
                # Add height to match
                new_height = expanded_width / original_aspect_ratio
                height_to_add = new_height - expanded_height
                expanded_top -= height_to_add / 2
                expanded_bottom += height_to_add / 2
            else: # too tall
                # Add width to match
                new_width = expanded_height * original_aspect_ratio
                width_to_add = new_width - expanded_width
                expanded_left -= width_to_add / 2
                expanded_right += width_to_add / 2
            
            # Aspect ratio of [expanded_left, expanded_top, expanded_right, expanded_bottom] is now the same as the original aspect ratio
            
            # Get minimum width and height based on the minimum frame factor
            min_width  = min_frame_factor * original_width
            min_height = min_frame_factor * original_height

            # Ensure width >= min_width, height >= min_height
            if expanded_right - expanded_left < min_width:
                # Too small - increase width and height proportionally
                width_increase  = min_width - (expanded_right - expanded_left)
                height_increase = min_height - (expanded_bottom - expanded_top)

                # Increase width and height proportionally
                expanded_left  -= width_increase / 2
                expanded_right += width_increase / 2
                expanded_top    -= height_increase / 2
                expanded_bottom += height_increase / 2
            
            # Check if frame width or height is greater than original
            # If so, adjust the frame to fit in the original frame
            if expanded_right - expanded_left > original_width or expanded_bottom - expanded_top > original_height:
                expanded_left, expanded_top, expanded_right, expanded_bottom = 0, 0, original_width, original_height
            
            # Check frame against edges
            if expanded_left < 0:
                shift = -expanded_left
                expanded_left  += shift
                expanded_right += shift
            if expanded_right > original_width:
                shift = expanded_right - original_width
                expanded_left  -= shift
                expanded_right -= shift
            
            if expanded_top < 0:
                shift = -expanded_top
                expanded_top    += shift
                expanded_bottom += shift
            if expanded_bottom > original_height:
                shift = expanded_bottom - original_height
                expanded_top    -= shift
                expanded_bottom -= shift
            
            # Convert to int for final crop coordinates
            expanded_left   = int(round(expanded_left))
            expanded_top    = int(round(expanded_top))
            expanded_right  = int(round(expanded_right))
            expanded_bottom = int(round(expanded_bottom))

            

            replay_camera_frame = [expanded_left, expanded_top, expanded_right, expanded_bottom]
            return replay_camera_frame
        
        def interpolate_frame_path(t_ms, frame_path):
            '''
            Function to interpolate the frame path based on the timestamp

            Input:
            - t: Timestamp to interpolate the frame path
            - frame_path: List of dictionaries with 'timestamp', 'left', 'top', 'right', 'bottom' coordinates to follow
            frame_path - camera_frame_path which contains the camera frame for each timestamp [sorted by timestamp]

            Output:
            - Interpolated left, top, right, bottom coordinates based on the timestamp
            '''

            # Extract the list of timestamps
            # Timestamps in frame_path are sorted
            timestamps = [point['timestamp'] for point in frame_path]
            t = t_ms/1000.0

            # If t is before the first timestamp, return the first point
            if t <= timestamps[0]:
                return int(frame_path[0]['left']), int(frame_path[0]['top']), int(frame_path[0]['right']), int(frame_path[0]['bottom'])

            # If t is after the last timestamp, return the last point
            if t >= timestamps[-1]:
                return int(frame_path[-1]['left']), int(frame_path[-1]['top']), int(frame_path[-1]['right']), int(frame_path[-1]['bottom'])

            # Find the index where t would fit into the sorted timestamps list
            index = bisect.bisect_right(timestamps, t) - 1

            # Get the two points surrounding t
            current_frame = frame_path[index]
            next_frame = frame_path[index + 1]

            # Interpolate between the two points
            ratio = (t - current_frame['timestamp']) / (next_frame['timestamp'] - current_frame['timestamp'])
            left = current_frame['left'] + ratio * (next_frame['left'] - current_frame['left'])
            top = current_frame['top'] + ratio * (next_frame['top'] - current_frame['top'])
            right = current_frame['right'] + ratio * (next_frame['right'] - current_frame['right'])
            bottom = current_frame['bottom'] + ratio * (next_frame['bottom'] - current_frame['bottom'])

            if (bottom - top)%2 != 0:
                bottom -= 1
            if (right - left)%2 != 0:
                right -= 1
            
            return int(left), int(top), int(right), int(bottom)
        
        def moving_average(data, window_size = 50):
            return [sum(data[max(0, i-window_size):i+1]) / (i - max(0, i-window_size) + 1) for i in range(len(data))]

        def exponential_smoothing(data, alpha=0.01):
            smoothed = [data[0]]  # Start with the first point
            for i in range(1, len(data)):
                smoothed.append(alpha * data[i] + (1 - alpha) * smoothed[-1])
            return smoothed
        
        def smooth_frame_path(frame_path):
            # Extract coordinates
            lefts = [point['left'] for point in frame_path]
            tops = [point['top'] for point in frame_path]
            rights = [point['right'] for point in frame_path]
            bottoms = [point['bottom'] for point in frame_path]
            timestamps = [point['timestamp'] for point in frame_path]

            
            # Apply exponential smoothing
            smoothed_lefts = exponential_smoothing(lefts)
            smoothed_tops = exponential_smoothing(tops)
            smoothed_rights = exponential_smoothing(rights)
            smoothed_bottoms = exponential_smoothing(bottoms)
            '''

            # Apply moving average
            smoothed_lefts = moving_average(lefts)
            smoothed_tops = moving_average(tops)
            smoothed_rights = moving_average(rights)
            smoothed_bottoms = moving_average(bottoms)
            '''
            # Update the frame path
            smoothed_path = []
            for i in range(len(frame_path)):
                smoothed_path.append({
                    'timestamp': timestamps[i],
                    'left': smoothed_lefts[i],
                    'top': smoothed_tops[i],
                    'right': smoothed_rights[i],
                    'bottom': smoothed_bottoms[i],
                })
            return smoothed_path
        def average_frame_smoothing(frame_path, look_around = 3, original_width = 1080, original_height = 1920):
            '''
            Function to average the frame path
            '''
            # Extract coordinates
            lefts = [point['left'] for point in frame_path]
            tops = [point['top'] for point in frame_path]
            rights = [point['right'] for point in frame_path]
            bottoms = [point['bottom'] for point in frame_path]
            timestamps = [point['timestamp'] for point in frame_path]

            mod_lefts = []
            mod_tops = []
            mod_rights = []
            mod_bottoms = []

            # Average the coordinates over the n +/- look_around range
            # For each timestamp, average the coordinates over the n +/- look_around
            # Return the averaged coordinates

            averaged_frame_path = []
            for i in range(len(frame_path)):
                # Loop through the n +/- look_around coordinates
                j_sum = 0
                left_sum = 0
                top_sum = 0
                right_sum = 0
                bottom_sum = 0
                for j in range(max(0, i - look_around), 
                               min(len(frame_path), i + look_around)):
                    # Average the coordinates
                    left_sum += lefts[j]
                    top_sum += tops[j]
                    right_sum += rights[j]
                    bottom_sum += bottoms[j]
                    j_sum += 1
                
                # Average the coordinates
                mod_lefts.append(left_sum / j_sum)
                mod_tops.append(top_sum / j_sum)
                mod_rights.append(right_sum / j_sum)
                mod_bottoms.append(bottom_sum / j_sum)

                # Add the averaged coordinates to the averaged frame path
                averaged_frame_path.append({
                    'timestamp': timestamps[i],
                    'left': max(0, min(original_width-1, mod_lefts[i])),
                    'top': max(0, min(original_height-1, mod_tops[i])),
                    'right': max(0, min(original_width-1, mod_rights[i])),
                    'bottom': max(0, min(original_height-1, mod_bottoms[i])),
                })

            return averaged_frame_path

        def post_process_reel_frame_path(reel_frame_path):
            '''
            Function to post process the reel frame path

            Input:
            - reel_frame_path: List of dictionaries with 'timestamp', 'left', 'top', 'right', 'bottom' coordinates to follow

            Output:
            - Post processed reel frame path
            '''
            # Smooth the reel frame path
            #smoothed_reel_frame_path = smooth_frame_path(reel_frame_path)

            # Average the reel frame path
            #reel_frame_path = average_frame_smoothing(reel_frame_path)
            
            return reel_frame_path

        

        
        '''
        Start of function code
        '''

        # Get frame size of video_clip
        original_frame_size = video_clip.size
        original_width, original_height = original_frame_size
        
        video_frames = VideoFrames(video_clip)
        audio_for_video = video_clip.audio
        #fps_for_video = video_clip.fps
        #duration_for_video = video_clip.duration

        minimum_frame_path = self.frame_path
        camera_frame_path = []
        reel_frame_path = []

        # Loop to create the camera frame for each timestamp
        # Iterate through timestamps in [minimum] frame path [which are sorted by timestamp]
        # self.frame_path = [{'timestamp': 0, 'left': 0, 'top': 0, 'right': 0, 'bottom': 0},...]
        for frame in minimum_frame_path:

            # Frames are provided in 0-1 range. Convert to pixel values
            frame_timestamp = frame['timestamp']
            frame_left = int(frame['left'] * original_width)
            frame_top = int(frame['top'] * original_height)
            frame_right = int(frame['right'] * original_width)
            frame_bottom = int(frame['bottom'] * original_height)

            minimum_frame_box = [frame_left, frame_top, frame_right, frame_bottom]

            #print('Margins [before adjustment]:', frame_timestamp, minimum_frame_box)

            camera_frame = create_full_frame(original_width, original_height, minimum_frame_box)
            reel_frame = create_reel_frame(original_width, original_height, minimum_frame_box)

            #print('Margins [after adjustment]:', frame_timestamp, camera_frame)
            #print('Reel margins:', frame_timestamp, reel_frame)

            camera_frame_path.append({'timestamp': frame_timestamp, 
                                      'left': camera_frame[0], 
                                      'top': camera_frame[1], 
                                      'right': camera_frame[2], 
                                      'bottom': camera_frame[3]})
            
            reel_frame_path.append({'timestamp': frame_timestamp,
                                    'left': reel_frame[0],
                                    'top': reel_frame[1],
                                    'right': reel_frame[2],
                                    'bottom': reel_frame[3]})
        
        # EXPT START
        # Plot the reel frame path with each edge separately
        lefts = [point['left'] for point in reel_frame_path]
        tops = [point['top'] for point in reel_frame_path]
        rights = [point['right'] for point in reel_frame_path]
        bottoms = [point['bottom'] for point in reel_frame_path]

        times = [point['timestamp'] for point in reel_frame_path]


        # Camera path is the list of timestamps and frames after frames are created for each timestamp based on the minimum frame
        # Camera path is used to interpolate the camera frame for each timestamp

        # Interpolate the camera frame for each timestamp
        frame_gen_for_path = video_frames.frame_generator()
        frame_gen = video_frames.frame_generator()

        moving_zoom_frames = []
        moving_zoom_timestamps = []

        reel_frames = []
        reel_timestamps = []

        width_of_interest = 1*1080
        height_of_interest = 1*1920

        reel_standard_width = int(1920)
        reel_standard_height = int(1920*16/9)

        reel_full_width = int(width_of_interest)#int(1080)
        reel_full_height = int(height_of_interest)#int(1920)

        # Creating the reel clip with VideoClip
        #video_clip

        # Post process reel_frame_path
        # Interpolate the reel frame path
        complete_reel_frame_path = []
        for image, t in frame_gen_for_path:
            # t is in milliseconds
            reel_box = interpolate_frame_path(t, reel_frame_path)
            complete_reel_frame_path.append({'timestamp': t/1000, 
                                             'left': reel_box[0], 
                                             'top': reel_box[1], 
                                             'right': reel_box[2], 
                                             'bottom': reel_box[3]})
        
        #print('BEFORE POST PROCESSING: Complete reel frame path:', complete_reel_frame_path)
        post_processed_reel_frame_path = post_process_reel_frame_path(complete_reel_frame_path)
        reel_frame_path = post_processed_reel_frame_path
        #print('AFTER POST PROCESSING: Complete reel frame path:', reel_frame_path)
        #'''
        
        # Create the reel clip with VideoClip
        def crop_reel_frame_for_fl(get_frame, t):
            #print(t) t is in seconds
            reel_left, reel_top, reel_right, reel_bottom = interpolate_frame_path(t*1000, reel_frame_path)  # Get the frame at time t
            frame = get_frame(t)

            # Resize reel to have standard instagram reel width and variable height

            #print(reel_top, reel_bottom, reel_left, reel_right)
            #print(reel_bottom - reel_top, reel_right - reel_left)
            #print(frame.shape)
            
            # Cropped image (reel)
            cropped_image = frame[reel_top:reel_bottom, reel_left:reel_right]
            
            #print('Reel margins:', reel_left, reel_top, reel_right, reel_bottom)
            #print('Cropped image shape:',cropped_image.shape)
            #print(reel_right, reel_left)
            
            # Calculate the aspect ratio of the cropped image
            cropped_aspect_ratio = cropped_image.shape[1] / cropped_image.shape[0]  # width / height

            # Get reel aspect ratio
            reel_aspect_ratio = reel_standard_width / reel_standard_height

            # Calculate the new dimensions
            if cropped_aspect_ratio < 9/16:  # Too thin
                #print('TOO THIN')
                # Expand reel_left and reel_right as needed
                reel_width_required = (reel_bottom - reel_top) * reel_aspect_ratio
                current_width       = reel_right - reel_left
                width_margin_to_add = reel_width_required - current_width
                
                #print('Current width:', current_width)
                #print('Reel width required:', reel_width_required)
                #print('Width margin to add:', width_margin_to_add)

                assert current_width > 0

                while width_margin_to_add > 0:
                    if reel_left == 0 and reel_right == original_width:
                        print('\n\nReel frame is already at the edges\n\n')
                        break
                    if reel_left > 0:
                        reel_left -= 1
                        width_margin_to_add -= 1
                    if reel_right < original_width:
                        reel_right += 1
                        width_margin_to_add -= 1
                
                cropped_image = frame[reel_top:reel_bottom, reel_left:reel_right]
                cropped_aspect_ratio = cropped_image.shape[1] / cropped_image.shape[0]  # width / height

                new_height = reel_standard_height
                new_width = int(new_height * cropped_aspect_ratio)
            
            elif cropped_aspect_ratio > 9/16:  # Too wide
                new_width = reel_standard_width
                new_height = int(new_width / cropped_aspect_ratio)
            
            else: # Aspect ratio = 9:16
                new_width = reel_standard_width
                new_height = reel_standard_height


            # Resize the image to the new dimensions based on reel aspect ratio
            #print('Reel Frame (20pc of standard)',new_height, new_width)

            resized_reel_image = cv.resize(cropped_image, (new_width, new_height))#, interpolation=cv.INTER_LINEAR)

            #print('Resized reel image shape:', resized_reel_image.shape)

            # Check if the video frame is within the reel frame and has aspect ratio 9:16
            # If its thinner, then fix it above. No way to fix it here
            # If its wider, add black boxes to the top and bottom
            reel_frame_aspect_ratio = resized_reel_image.shape[1] / resized_reel_image.shape[0]  # width / height
            if reel_frame_aspect_ratio < 9/16: # Too thin
                # Check if reel_frame_aspect_ratio is very close to 9/16
                if abs(reel_frame_aspect_ratio - 9/16) < 0.01:
                    print('Reel frame aspect ratio is very close to 9/16')
                else:
                    # Extend the width to the sides and snap to the edges
                    print('Shape:', resized_reel_image.shape)
                    print('SHOULD NEVER HAPPEN. FIX IT EARLIER')
                    raise ValueError('Reel frame is too thin')
                    pass
            
            elif reel_frame_aspect_ratio > 9/16: # Too wide
                # Add black boxes to the top and bottom
                reel_required_height = reel_standard_height
                height_box = int((reel_required_height - resized_reel_image.shape[0]) / 2)

                # Black box on top and bottom
                top_box = np.zeros((height_box, resized_reel_image.shape[1], 3), dtype=np.uint8)
                bottom_box = np.zeros((height_box, resized_reel_image.shape[1], 3), dtype=np.uint8)
                reel_final_image = np.concatenate((top_box, resized_reel_image, bottom_box), axis=0)
                    
            else: # Aspect ratio = 9:16
                reel_final_image = resized_reel_image

            #print('Reel Frame width:',  cropped_image.shape[1])
            #print('Reel Frame height:', cropped_image.shape[0])

            # Resize to standard instagram reel dimensions
            reel_final_image = cv.resize(reel_final_image, (reel_full_width, reel_full_height))

            return reel_final_image #frame[reel_top:reel_bottom, reel_left:reel_right]  # Crop to a region
        
        # Apply the custom cropping function
        # Cropped frames resized to standard instagram reel dimensions and boxes added to the frames
        ripley_reel = video_clip.fl(lambda gf, t: crop_reel_frame_for_fl(gf, t))

        # Add audio to the ripley reel
        ripley_reel = ripley_reel.set_audio(audio_for_video)

        # Write the cropped video to a file
        ripley_reel.write_videofile('./test_and_delete/temp_game_files/ripley_reel_clip.mp4')

        if ripley_reel.duration != 0:
            print("Valid duration:", ripley_reel.duration)

            # Write ripley_reel to a file
            # Find the next available ripley file number
            i = 0
            file_found = True
            while file_found:
                if not os.path.isfile('./test_and_delete/temp_game_files/ig_output_'+str(i)+'.mp4'):
                    file_found = False
                    break
                else:
                    i += 1
            reel_number = i
            output_ig_path = './test_and_delete/temp_game_files/ig_output_'+str(reel_number)+'.mp4'
            
            # Apply sharpening and smoothing effects
            ripley_reel = ripley_reel.fl_image(sharpen_image)
            ripley_reel = ripley_reel.fl_image(smooth_image)

            # Add watermark
            ripley_reel_with_logo = add_watermark(ripley_reel)
            ripley_reel_with_logo.write_videofile(output_ig_path, audio_codec='aac')# Needed for later reading the file 
            
            #, codec='png')
            # PNG files are massive (1GB per reel)

        else:
            print("Error: Ripley Reel Duration is zero!")

        for image, t in frame_gen:
            # t is in milliseconds
            # frame = left, top, right, bottom
            camera_frame_box = interpolate_frame_path(t, camera_frame_path)
            reel_frame_box = interpolate_frame_path(t, reel_frame_path)

            #print('[AFTER INTERPOLATION]:', t, camera_frame_box)

            frame_left, frame_top, frame_right, frame_bottom = camera_frame_box

            # Show the frame in the image
            image_mod = np.copy(image)
            # cv.rectangle(image_mod, (frame_left, frame_top), (frame_right, frame_bottom), (255, 0, 0), 2)
            
            # Crop the image to the specified width and height
            cropped_image = image_mod[frame_top:frame_bottom, frame_left:frame_right]

            # Resize to the original frame size
            cropped_image = cv.resize(cropped_image, (original_width, original_height))
            
            moving_zoom_frames.append(cropped_image)
            moving_zoom_timestamps.append(t)
            # End of for loop run by generator

        moving_zoom_video_frames = VideoFrames()
        moving_zoom_video_frames.add_frames_list(moving_zoom_frames, moving_zoom_timestamps)

        print('Number of frames:', len(moving_zoom_frames))
        print('Number of timestamps:', len(moving_zoom_timestamps))
        print('Start timestamp:', moving_zoom_timestamps[0])
        print('End timestamp:', moving_zoom_timestamps[-1])
        
        moving_zoom_video_clip = moving_zoom_video_frames.convert_video_frames_to_moviepy_clip()

        # Add audio to the video clip
        moving_zoom_video_clip = moving_zoom_video_clip.set_audio(audio_for_video)
        
        print('Frame size after MOVING ZOOM WITH FRAMES:', moving_zoom_video_clip.size)
        
        if moving_zoom_video_clip.duration != 0:
            print("Valid duration:", moving_zoom_video_clip.duration)
        else:
            print("Error: Duration is zero!")

        return moving_zoom_video_clip
    
    def moving_zoom_with_ball_path(self, video_clip):
        '''
        Function to apply the moving zoom effect based on the ball path

        Input:
        - video_clip: VideoClip object to apply the moving zoom effect

        Available variables:
        - self.ball_path: List of dictionaries with 'timestamp', 'x', 'y' coordinates to follow
        - self.frame_size: Tuple with width and height of the zoom frame

        Output:
        - VideoClip object with the moving zoom effect applied

        Functions defined in this function:
        - interpolate_ball_path: Function to interpolate the ball path based on the timestamp
        - check_frame_fits: Function to check if the frame fits in the image and adjust the margins if necessary

        Approach:
        - Extract the ball point from the ball path based on the timestamp
        - Calculate the frame margins based on the ball point and the frame size
        - Check if the frame fits in the image and adjust the margins if necessary
        - Crop the image to the specified width and height

        '''
        def interpolate_ball_path(t, ball_path):
            '''
            Function to interpolate the ball path based on the timestamp

            Input:
            - t: Timestamp to interpolate the ball path
            - ball_path: List of dictionaries with 'timestamp', 'x', 'y' coordinates to follow

            Output:
            - Interpolated x, y coordinates based on the timestamp
            '''

            # Extract the list of timestamps
            timestamps = [point['timestamp'] for point in ball_path]

            # If t is before the first timestamp, return the first point
            if t <= timestamps[0]:
                return ball_path[0]['x'], ball_path[0]['y']

            # If t is after the last timestamp, return the last point
            if t >= timestamps[-1]:
                return ball_path[-1]['x'], ball_path[-1]['y']

            # Find the index where t would fit into the sorted timestamps list
            index = bisect.bisect_right(timestamps, t) - 1

            # Get the two points surrounding t
            current_point = ball_path[index]
            next_point = ball_path[index + 1]

            # Interpolate between the two points
            ratio = (t - current_point['timestamp']) / (next_point['timestamp'] - current_point['timestamp'])
            x = current_point['x'] + ratio * (next_point['x'] - current_point['x'])
            y = current_point['y'] + ratio * (next_point['y'] - current_point['y'])

            return x, y

        def check_frame_fits(original_width, original_height, frame_box):
            '''
            Function to check if the frame fits in the image and adjust the margins if necessary

            Input:
            - original_width: Width of the original image
            - original_height: Height of the original image
            - frame_box: List with the frame margins [left, top, right, bottom]

            Output:
            - List with the adjusted frame margins [left, top, right, bottom]

            Approach:
            - Get the frame margins for the edges of the image
            - Adjust the frame to fit in the image by using the edges of the image [Snap to the edges]
            - Check if frame margins in the middle of the picture and adjust if necessary

            '''
            # Get the frame margins for the edges of the image
            frame_left, frame_top, frame_right, frame_bottom = frame_box

            # Check if the frame fits in the image
            if frame_left < 0 or frame_top < 0 or frame_right > original_width or frame_bottom > original_height:
                # Adjust the frame to fit in the image
                if frame_left < 0:
                    frame_left = 0
                    frame_right = self.frame_size[0]
                if frame_top < 0:
                    frame_top = 0
                    frame_bottom = self.frame_size[1]
                if frame_right > original_width:
                    frame_right = original_width
                    frame_left = original_width - self.frame_size[0]
                if frame_bottom > original_height:
                    frame_bottom = original_height
                    frame_top = original_height - self.frame_size[1]
            
            frame_top = int(frame_top)
            frame_bottom = int(frame_bottom)
            frame_left = int(frame_left)
            frame_right = int(frame_right)

            # Check frame margins in the middle of the picture
            if frame_bottom - frame_top != self.frame_size[1]:
                # Adjust frame_bottom or frame_top to fit the frame size
                if frame_bottom >= original_height:
                    frame_bottom = original_height
                    frame_top = original_height - self.frame_size[1]
                else:
                    frame_bottom += 1
                    frame_top = frame_bottom - self.frame_size[1]
            
            if frame_right - frame_left != self.frame_size[0]:
                # Adjust frame_right or frame_left to fit the frame size
                if frame_right >= original_width:
                    frame_right = original_width
                    frame_left = original_width - self.frame_size[0]
                else:
                    frame_right += 1
                    frame_left = frame_right - self.frame_size[0]

            assert frame_right - frame_left == self.frame_size[0]
            assert frame_bottom - frame_top == self.frame_size[1]

            # Return the frame margins in a frame box
            return [round(frame_left), round(frame_top), round(frame_right), round(frame_bottom)]
        
        '''
        Start of function code
        '''

        video_frames = VideoFrames(video_clip)
        audio_for_video = video_clip.audio
        frame_gen = video_frames.frame_generator()

        moving_zoom_frames = []
        moving_zoom_timestamps = []

        for image, t in frame_gen:

            ball_point = interpolate_ball_path(t, self.ball_path)
            #print('Ball point:', ball_point)
            #self.ball_point = self.ball_path[t]

            '''
            Good spot to add the variable zoom effect.
            Width and height margins can be adjusted based on zoom factor

            Zoom factor can be dependent on timestamp here

            zoom_factor = zf(t)

            width_margin = (self.frame_size[0] // 2)//zoom_factor
            height_margin = (self.frame_size[1] // 2)//zoom_factor


            '''
            width_margin = self.frame_size[0] // 2
            height_margin = self.frame_size[1] // 2
            
            # Get original image size
            original_height, original_width = image.shape[:2]

            if len(moving_zoom_frames) == 0:
                print('\n\nOriginal height:', original_height)
                print('Original width:', original_width)

            # Show the moving ball point in the image
            image_mod = np.copy(image)
            ball_point_x = int(ball_point[0])
            ball_point_y = int(ball_point[1])
            ball_center = (ball_point_x, ball_point_y)
            #cv.circle(image_mod, ball_center, 10, (255, 0, 0), -1)

            frame_left   = ball_point_x - width_margin
            frame_right  = ball_point_x + width_margin

            frame_top    = ball_point_y - height_margin
            frame_bottom = ball_point_y + height_margin

            #print('\n\n========', width_margin, height_margin, '========\n\n')

            
            frame_box = [frame_left, frame_top, frame_right, frame_bottom]

            # Check if the frame fits in the image and adjust the margins if necessary
            adjusted_frame_box = check_frame_fits(original_width, original_height, frame_box)
            frame_left, frame_top, frame_right, frame_bottom = adjusted_frame_box

            if (frame_bottom - frame_top)%2 != 0:
                frame_bottom -= 1
            if (frame_right - frame_left)%2 != 0:
                frame_right -= 1
            #print('\nAdjusted frame sizes:')
            #print(frame_bottom - frame_top, frame_right - frame_left)

            # Print before cropping
            #print('Frame box:', frame_left, frame_top, frame_right, frame_bottom)
            
            # Crop the image to the specified width and height
            cropped_image = image_mod[frame_top:frame_bottom, frame_left:frame_right]
            
            #print('Frame size width:',  frame_right - frame_left)
            #print('Frame size height:', frame_bottom - frame_top)

            '''
            # Resize the image to a specified width and height
            # Interpolation method: cv2.INTER_AREA for shrinking
            # Interpolation method: cv2.INTER_CUBIC (slow) & cv2.INTER_LINEAR for zooming
            # No need to resize the image so far
            # image = cv.resize(image, (self.frame_size[0], self.frame_size[1]))
            
            # The resize should include margins on the sides so that the zoomed camera frame can be added to the landscape video

            '''

            #print(cropped_image.shape)
            if cropped_image.shape[0] == 0 or cropped_image.shape[1] == 0:
                print('Empty frame')
                # Print the margins
                print('Frame box:', frame_box)
                print('Adjusted frame box:', adjusted_frame_box)
                print('Top:', frame_top)
                print('Bottom:', frame_bottom)
                print('Left:', frame_left)
                print('Right:', frame_right)
                continue
            moving_zoom_frames.append(cropped_image)
            moving_zoom_timestamps.append(t)

            # End for loop run by generator
        
        
        moving_zoom_video_frames = VideoFrames()
        moving_zoom_video_frames.add_frames_list(moving_zoom_frames, moving_zoom_timestamps)

        print('Number of frames:', len(moving_zoom_frames))
        print('Number of timestamps:', len(moving_zoom_timestamps))
        print('Start timestamp:', moving_zoom_timestamps[0])
        print('End timestamp:', moving_zoom_timestamps[-1])
        
        moving_zoom_video_clip = moving_zoom_video_frames.convert_video_frames_to_moviepy_clip()
        
        # Add audio to the video clip
        moving_zoom_video_clip = moving_zoom_video_clip.set_audio(audio_for_video)
        
        print('Frame size after MOVING ZOOM WITH BALL PATH:', moving_zoom_video_clip.size)
        
        if moving_zoom_video_clip.duration != 0:
            print("Valid duration:", moving_zoom_video_clip.duration)
        else:
            print("Error: Duration is zero!")

        return moving_zoom_video_clip
    
    def __call__(self, video_clip):
        '''
        Function for moving zoomed camera effect within a video clip
        
        Input:
        - video_clip: VideoClip object to apply the moving zoom effect
        - ball_path: List of dictionaries with 'timestamp', 'x', 'y' coordinates to follow
        - frame_size: Tuple with width and height of the zoom frame

        Output:
        - VideoClip object with the moving zoom effect applied
        '''

        if self.frame_path is not None:
            moving_zoom_video_clip_by_frame_path       = self.moving_zoom_with_frame_path(video_clip)
            return moving_zoom_video_clip_by_frame_path

        if self.ball_path is not None:
            moving_zoom_video_clip_by_ball_path                     = self.moving_zoom_with_ball_path(video_clip)
            return moving_zoom_video_clip_by_ball_path
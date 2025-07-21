'''
File to develop video frames class for video operations

Inputs:
- Video file

Provides video frame class with methods to perform operations on videos

Functions include
- Read video frames from video file
- Write video frames to video file
- Cut video by timestamps
- Get frame by index
- Get frame by timestamp
- Get number of frames
- Get total length of the video
- Get frames per second
'''

import cv2 as cv
import numpy as np
import time
import os

from moviepy.editor import VideoClip, ImageSequenceClip, CompositeVideoClip, VideoFileClip
from moviepy.editor import concatenate_videoclips

# Class to store frames and their timestamps
class VideoFrames:
    def __init__(self, clip = None):
        self.frames = []
        self.timestamps = []

        if isinstance(clip, VideoClip):
            self.convert_moviepy_clip_to_video_frames(clip)
        
        return None

    def convert_moviepy_clip_to_video_frames(self, clip):
        '''
        Function to convert a moviepy video clip to video frames

        Input:
        - clip: Moviepy video clip object

        Output:
        - None
        '''
        self.frames = []
        self.timestamps = []

        for frame in clip.iter_frames(with_times=True):
            timestamp, img_frame = frame

            # timestamp*1000 because moviepy measures timestamp in seconds
            self.timestamps.append(timestamp*1000)
            self.frames.append(img_frame)
        
        return None
    
    def convert_video_frames_to_moviepy_clip(self, fps = None, fps_speed_adjustment=1):
        '''
        Function to convert video frames to a moviepy video clip

        Output:
        - Moviepy video clip object
        '''
        # Set the FPS of the video clip , adjust if necessary
        if fps is None:
            fps = self.get_fps() * fps_speed_adjustment
        
        # Create an ImageSequenceClip from the frames
        image_sequence_clip = ImageSequenceClip(self.frames, fps=fps)
        
        composite_video_clip = CompositeVideoClip([image_sequence_clip])

        video_clip = concatenate_videoclips([composite_video_clip])

        #video_clip.write_videofile('./test_and_delete/clip_conversion_check.mp4')
        #user_input = input('Continue?')
        # Extra stuff in write - Normal video with no sound

        return video_clip

    def add_frame(self, frame, timestamp):
        self.frames.append(frame)
        self.timestamps.append(timestamp)
    
    def add_frames_list(self, frames_list, timestamps_list):
        self.frames.extend(frames_list)
        self.timestamps.extend(timestamps_list)
        return None

    def frame_generator(self):
        '''
        Function to generate frames and timestamps from the video frames object
        '''
        for frame, timestamp in zip(self.frames, self.timestamps):
            yield frame, timestamp

    def get_frame_by_index(self, index):
        if index < 0 or index >= len(self.frames):
            raise IndexError("Index out of range")
        return self.frames[index], self.timestamps[index]

    def get_frame_by_timestamp(self, timestamp):
        if timestamp < 0 or timestamp > self.timestamps[-1]:
            raise ValueError("Timestamp out of range")
        index = min(range(len(self.timestamps)), key=lambda i: abs(self.timestamps[i] - timestamp))
        return self.frames[index], self.timestamps[index]

    def get_number_of_frames(self):
        return len(self.frames)

    def _get_total_length(self):
        '''
        Function to get the total length of the video in seconds

        The video frames object might be cut from other videos
        ==> timestamp[0] is not necessarily zero in all cases

        Output:
        - Total length of the video
        '''
        if not self.timestamps:
            return 0
        return (self.timestamps[-1] - self.timestamps[0]) / 1000  # Return length in seconds
    
    def get_fps(self):
        return self.get_number_of_frames() / self._get_total_length()
    
    def reset_timestamps_to_start_at_zero(self):
        '''
        Function to reset the timestamps to start at zero
        '''
        start_time = self.timestamps[0]
        self.timestamps = [timestamp - start_time for timestamp in self.timestamps]
        return None
    
    def cut_video_by_timestamp(self, start, end): # start and end are in milliseconds

        # Find the index of the start and end timestamps
        start_index = min(range(len(self.timestamps)), key=lambda i: abs(self.timestamps[i] - start))
        end_index = min(range(len(self.timestamps)), key=lambda i: abs(self.timestamps[i] - end))

        # Create a video_frames object of the cut video
        vf_cut = VideoFrames()
        vf_cut.frames = self.frames[start_index:end_index]
        vf_cut.timestamps = self.timestamps[start_index:end_index]

        return vf_cut
    
    def write_video_frames_to_file(self, output_file_path):
        '''
        Function to write video frames to a video file

        Input:
        - output_file_path: Path to the output video file

        Output:
        - None
        '''
        start = time.time()
        # Get the height and width of the frames
        height, width, _ = self.frames[0].shape

        print(cv.VideoWriter_fourcc(*'avc1'))
        # Create a video writer object
        #out = cv.VideoWriter(output_file_path, cv.VideoWriter_fourcc(*'mp4v'), self.get_fps(), (width, height))
        out = cv.VideoWriter(output_file_path, cv.VideoWriter_fourcc(*'mp4v'), int(self.get_fps()), (width, height))


        # Write the frames to the video file
        for frame in self.frames:
            out.write(frame)

        # Release the video writer object
        out.release()

        print('Time taken to write video frames to video file:', round(time.time() - start), 'seconds')
        return None
# End of class
    
    

def create_video_frames_from_video_file(local_file_path):
    start = time.time()

    # Assert that the file exists
    assert os.path.exists(local_file_path), f"Error: The file '{local_file_path}' does not exist."


    # Read the video using OpenCV
    cap = cv.VideoCapture(local_file_path)

    video_frames = VideoFrames()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Get the current timestamp in milliseconds
        timestamp = cap.get(cv.CAP_PROP_POS_MSEC)

        # Add the frame and its timestamp to the list
        video_frames.add_frame(frame, timestamp)

    # Release the video capture object
    cap.release()

    print('Time taken to create video frames:', round(time.time() - start), 'seconds')

    return video_frames

def create_video_frames_from_video_file_with_timestamps(local_file_path, timestamps_of_interest, start_time_offset=7000, end_time_offset=3000):
    """
    Create VideoFrames object by reading only the segments around timestamps of interest.
    
    Args:
    - local_file_path (str): Path to the video file.
    - timestamps_of_interest (list of int): List of timestamps (in milliseconds) of interest.
    - buffer_time (int): Buffer time (in milliseconds) to add/subtract around each timestamp of interest.
    
    Returns:
    - VideoFrames: Object containing frames and their timestamps for the segments of interest.
    """
    start = time.time()

    # Read the video using OpenCV
    cap = cv.VideoCapture(local_file_path)
    fps = cap.get(cv.CAP_PROP_FPS)

    vf_list = []
    #video_frames = VideoFrames()

    for timestamp in timestamps_of_interest:
        
        video_frames = VideoFrames()
        start_time = max(0, timestamp - start_time_offset)
        end_time = timestamp + end_time_offset

        cap.set(cv.CAP_PROP_POS_MSEC, start_time)
        
        #i = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print('Breaks in the video')
                break

            current_timestamp = cap.get(cv.CAP_PROP_POS_MSEC)
            if current_timestamp > end_time:
                break

            video_frames.add_frame(frame, current_timestamp)
            # end while loop
        
        print(timestamp,'is done')
        vf_list.append(video_frames)

    # Release the video capture object
    cap.release()
    print('Time taken to create highlights video frames:', round(time.time() - start), 'seconds')

    return vf_list

def write_video_frames_to_video_file(vf_to_write, output_file_path):

    start = time.time()
    # Get the height and width of the frames
    height, width, _ = vf_to_write.frames[0].shape

    # Create a video writer object
    out = cv.VideoWriter(output_file_path, cv.VideoWriter_fourcc(*'mp4v'), vf_to_write.get_fps(), (width, height))

    # Write the frames to the video file
    print('Writing',len(vf_to_write.frames),'frames to the video file')
    print('FPS:', vf_to_write.get_fps())
    for frame in vf_to_write.frames:
        out.write(frame)

    # Release the video writer object
    out.release()

    print('Time taken to write video frames to video file:', round(time.time() - start), 'seconds')
    return None


def write_frames_to_file(vf_to_write, output_file_path):
    '''
    Function to write video_frames to a video file

    Input:
    - vf_to_write: VideoFrames object to write to the video file

    Output:
    - None
    '''

    start = time.time()
    
    # Get the FPS and frame size
    fps = vf_to_write.get_fps()
    height, width, _ = vf_to_write.frames[0].shape
    frame_size = (width, height)
    
    # Create a video writer object
    out = cv.VideoWriter(output_file_path, cv.VideoWriter_fourcc(*'mp4v'), fps, frame_size)

    print('Starting the write')
    # Write the frames to the video file
    for frame in vf_to_write.frame_generator(vf_to_write.frames):
        out.write(frame)

    # Release the video writer object
    out.release()
    print('Write complete')

    print('Time taken to write video frames to video file:', round(time.time() - start), 'seconds')
    return None


def simple_stabilize(input_path, output_path, threshold=5, smoothing_radius=5):
    cap = cv.VideoCapture(input_path)
    fps = int(cap.get(cv.CAP_PROP_FPS))
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    n_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))

    # Video writer to save stabilized output
    out = cv.VideoWriter(output_path, cv.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    # Initialize variables
    _, prev_frame = cap.read()
    prev_gray = cv.cvtColor(prev_frame, cv.COLOR_BGR2GRAY)
    transforms = np.zeros((n_frames - 1, 2), np.float32)

    # Calculate transformations for each frame
    for i in range(1, n_frames):
        ret, curr_frame = cap.read()
        if not ret:
            break

        curr_gray = cv.cvtColor(curr_frame, cv.COLOR_BGR2GRAY)

        # Estimate motion (translation only)
        flow = cv.calcOpticalFlowFarneback(prev_gray, curr_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        dx, dy = np.median(flow[..., 0]), np.median(flow[..., 1])

        # Threshold motion
        if abs(dx) < threshold:
            dx = 0
        if abs(dy) < threshold:
            dy = 0

        transforms[i - 1] = [dx, dy]
        prev_gray = curr_gray
        print(i)
    # Smooth transformations using a sliding window
    smoothed_transforms = transforms.copy()
    for i in range(smoothing_radius, len(transforms) - smoothing_radius):
        smoothed_transforms[i] = np.mean(
            transforms[i - smoothing_radius:i + smoothing_radius + 1], axis=0
        )

    # Reset capture to apply transformations
    cap.set(cv.CAP_PROP_POS_FRAMES, 0)

    # Apply transformations to stabilize frames
    for i in range(n_frames - 1):
        ret, frame = cap.read()
        if not ret:
            break

        dx, dy = smoothed_transforms[i]
        transform_matrix = np.float32([[1, 0, -dx], [0, 1, -dy]])
        stabilized_frame = cv.warpAffine(frame, transform_matrix, (width, height))
        out.write(stabilized_frame)
        print(i)

    cap.release()
    out.release()

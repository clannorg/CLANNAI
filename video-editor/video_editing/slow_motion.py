import cv2 as cv
from video_frames import VideoFrames, create_video_frames_from_video_file, write_video_frames_to_video_file

def fill_in_frames(video_frames, desired_fps = 30):
    '''
    To be done
    This function still needs to add interpolation of frames to the slow-motion video to reduce the choppiness
    '''
    pass

def create_slow_motion_video(video_frames, slow_factor, output_file_path = None):
    
    slow_mo = VideoFrames()
    initial_timestamp = video_frames.timestamps[0]

    for i in range(video_frames.get_number_of_frames()):
        frame, timestamp = video_frames.get_frame_by_index(i)
        
        # Adjust the timestamp by the slow factor
        adjusted_timestamp = (timestamp - initial_timestamp) * slow_factor
        slow_mo.add_frame(frame, adjusted_timestamp)

    # Fill in the frames to reduce the choppiness
    #slow_mo = fill_in_frames(slow_mo)

    # Write the slow-motion video to the output file
    if output_file_path is not None:
        write_video_frames_to_video_file(slow_mo, output_file_path)
    
    print('Slow-motion video created')
    return slow_mo

def usage_example():
    file_path = '../../sample_data/video_data/'
    file_name = 'IMG_5841.mp4'
    output_file_name = 'IMG_5841_slow_motion.mp4'
    slow_factor = 2

    video_frames = create_video_frames_from_video_file(file_path + file_name)
    slow_mo = create_slow_motion_video(video_frames, slow_factor, file_path + output_file_name)
    
def main():
    usage_example()

if __name__ == "__main__":
    main()


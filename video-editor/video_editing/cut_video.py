'''
File to write classes for cutting the video given different inputs

Inputs:
- List of timestamps of interest
- List of [start, end] timestamps of interest
- List of [start, duration] timestamps of interest
'''
import os
import time


# street packages
from .video_editor import VideoEditor

from .time_cut_fn import read_timestamps, timestamp_selector, get_timebands_from_timestamps

from moviepy.editor import concatenate_videoclips


def ts_to_cut_file(file_names, labels_of_interest = None):

    start_time = time.time()
    # Path to the video file
    read_file_path = file_names['file_path']
    read_file_name = file_names['input_file_name']

    # Path to the timestamp file
    timestamp_file_path = file_names['file_path']
    timestamp_file_name = file_names['timestamp_file_name']
    
    # Read the timestamps (provided in milliseconds) and (labels, descriptions) from the xlsx file
    label_dict = read_timestamps(timestamp_file_path + timestamp_file_name)
    print('Time taken to read timestamps:', round(time.time() - start_time))

    label_indices_of_interest = timestamp_selector(label_dict, labels_of_interest)
    timebands_and_info = get_timebands_from_timestamps(label_indices_of_interest, label_dict)

    # Get UTC timestamps from timestamps_of_interest and timestamp_of_video
    # To be added

    

    video_editor = VideoEditor(read_file_path + read_file_name)
    '''
    start_time = 3*3600+19*60+10
    end_time = start_time + 10
    test_video = video_editor.get_video_clip().subclip(start_time, end_time)
    test_video.write_videofile('./test_and_delete/temp_game_files/test_video_full_temp.mp4')

    test_video = video_editor.get_video_clip()

    clip_1 = test_video.subclip(0, 10)
    clip_2 = test_video.subclip(15, 20)

    clip_combined_12 = concatenate_videoclips([clip_1, clip_2])

    clip_combined_12.write_videofile("./test_and_delete/test_video_combined_12.mp4")

    clip_3 = test_video.subclip(0, 10)
    clip_4 = test_video.subclip(5, 10)

    clip_combined_34 = concatenate_videoclips([clip_3, clip_4])
    
    clip_combined_34.write_videofile("./test_and_delete/test_video_combined_34.mp4")'''

    '''audio = video_editor.get_video_clip().audio
    audio.write_audiofile("./test_and_delete/test_audio_full.mp3")'''
    video_list = video_editor.cut_video_by_timebands(timebands_and_info)

    print('Time taken to create this cut:', round(time.time() - start_time))
    return video_list

def process_game_code_files(file_path, game_code, number_of_files = 1, labels_of_interest = None):
    # Example usage
    print('Current working directory:', os.getcwd())

    
    mp4_postfix = '.mp4' #'.m2ts'#'.mp4'
    ts_postfix = '_timestamps.xlsx'
    cut_postfix = '_cut_vm003.mp4'

    print('Game code:', game_code)
    print('Number of files:', number_of_files)

    video_cuts_list = []
    for i in range(number_of_files):
        
        file_name_add = 'p' + str(i+1)
        file_code = game_code + '_' + file_name_add

        input_file_name = file_code + mp4_postfix
        timestamp_file_name = file_code + ts_postfix

        file_names = {}
        file_names['file_path'] = file_path
        file_names['input_file_name'] = input_file_name
        file_names['timestamp_file_name'] = timestamp_file_name

        cut_video = ts_to_cut_file(file_names, labels_of_interest)

        # Video height : 1920
        # Video width : 1080
        #'''
        if cut_video is not None and i > 1:
            mod_cut_video = []
            height, width = cut_video[0][0].size
            if height != 1080 or width != 1920:
                print('Height:', height)
                print('Width:', width)
                print('Resizing the video to 1920x1080')
                
                for video, t1, t2 in cut_video:
                    video_resize = video.resize((1920, 1080))
                    mod_cut_video.append((video_resize, t1, t2))
            
            if len(mod_cut_video) > 0:
                cut_video = mod_cut_video #'''
        
        if cut_video is not None:
            video_cuts_list.extend(cut_video)
    
    #for video, t1, t2 in video_cuts_list:
    #    video.write_videofile('./test_and_delete/clip_check.mp4')
    #    user_input = input('CLIP in CUT VIDEO: Check clip and press enter to continue: ')
    
    return video_cuts_list

def run_cut_video(game_code, number_of_files, file_path, labels_of_interest = None):

    video_cuts_list = process_game_code_files(file_path, game_code, number_of_files, labels_of_interest)
    return video_cuts_list


def main():
    pass

if __name__ == "__main__":
    main()


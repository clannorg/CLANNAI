'''
This script is used to create an Instagram reel format video from game clips
'''

import os
import json

from moviepy.editor import VideoFileClip, vfx, concatenate_videoclips

from street.data_transfer.get_data_from_gcp_bucket import download_single_file_from_gcp_bucket
from street.data_transfer.put_data_into_gcp_bucket import upload_file_to_gcp_bucket
from street.data_transfer.get_data_from_gcp_bucket import download_blobs_in_folder

from street.video_editing.zoom import MovingZoom

from street.video_editing.watermark import add_watermark

from street.video_editing.video_effects import sharpen_image, reduce_glare_and_haziness, enhance_colors


def get_reel_file_details(reel_name):

    reel_details = dict()
    game_recordings_folder = './data/game-recordings/'

    if reel_name == 'bellandur_blast':
        reel_details['game_code']   = 'Game27_1006'
        reel_details['file_name']   = 'Game27_1006_p1.mp4'
        reel_details['vm_file_path'] = game_recordings_folder + reel_details['game_code'] + '/' + reel_details['file_name']
        reel_details['clip_start']  = 5*60 + 42
        reel_details['clip_end']    = reel_details['clip_start'] + 5

    return reel_details



def create_reel_from_clip(video_clip, camera_path, frame_size = (1080, 1920), game_code = 'test'):


    # Create a MovingZoom object and initialize ball path and frame size
    moving_camera = MovingZoom(camera_path, frame_size)
    
    # Add moving camera effect to the video clip
    reel_clip = moving_camera(video_clip)
    
    print(type(video_clip), type(reel_clip))
    print('Video clip size:', video_clip.size)
    print('Reel clip size:', reel_clip.size)

    # Write the video clip to a file
    i = 0
    file_found = True
    while file_found:
        if not os.path.isfile('./data/reel_clips/'+ game_code +'/reel_clip_' + str(i) + '.mp4'):
            file_found = False
            break
        else:
            i += 1
    
    if reel_clip is not None:
        print(type(reel_clip))
        print('\n\nAdding watermark...')
        reel_clip = add_watermark(reel_clip, opacity=0.8, scale = 0.3)
        print('ADDED WATERMARK\n\n')
        print(type(reel_clip))
        
        # if .m2ts
        '''
        reel_clip = reel_clip.set_fps(50)
        reel_clip = reel_clip.fx(vfx.speedx, factor=0.5)
        reel_clip = reel_clip.subclip(0,int(0.5*reel_clip.duration))
        '''

        reel_clip.write_videofile('./data/reel_clips/'+ game_code +'/reel_clip_' + str(i)+'.mp4', 
                                                codec="libx264", audio_codec="aac")
        
        print('Reel clip created successfully')
        print('File saved as: ./data/reel_clips/'+game_code+'/reel_clip_' + str(i)+'.mp4')

    return reel_clip

def create_ripley_reel_from_video_clip(video_clip, annotation_file_path):
    '''
    Function to create a reel from a video clip

    Input:
        video_clip: Video clip to create a reel from
        game_code: Game code to save the reel
    
    Output:
        video_clip_with_replay_camera: Ripley reel video clip
    
    Approach:
    - Get the frame path from the annotation file
    - Create a MovingZoom object with the frame path
    - Add the moving camera effect to the video clip
    - Add audio to the video clip
    - Save the video clip

    '''
    print('Creating reel from video clip')

    # Get the frame path from the annotation file
    frame_path = get_frame_path_from_annotation_file(annotation_file_path) # MORE TO DO HERE

    # NEED TRACK BOXES FROM PEOPLE TRACKING

    # Get the audio from the video clip
    clip_audio = video_clip.audio

    # Creating reel clips
    replay_camera = MovingZoom(frame_path)
    video_clip_with_replay_camera = replay_camera(video_clip)

    # Add audio to the video clip
    video_clip_with_replay_camera   = video_clip_with_replay_camera.set_audio(clip_audio)

    return video_clip_with_replay_camera

    


def create_reels(video_clip, camera_path, game_code):
    '''
    Create reels from the video clip

    Args:
        video_path: Video file to create reels from
        original_frame_height: Original frame height of the video
        original_frame_width: Original frame width of the video
        camera_path: Camera path to create reels

    Returns:
        Video clips with reels
    '''

    # Get original frame size of the video
    original_frame_height = video_clip.size[1]
    original_frame_width = video_clip.size[0]

    # Creating reel clips

    # Original frame size * 2/3
    reel_height = int(2 * original_frame_height // 3)
    reel_width = int(2 * original_frame_width // 3)
    reel_frame_size = (reel_width, reel_height)
    create_reel_from_clip(video_clip, camera_path, reel_frame_size, game_code)

    # Convert any horizontal video to vertical format

    # Height is set to two_thirds of the original height
    # Width is set based on reels aspect ratio
    reel_height = int(2 * original_frame_height // 3)
    reel_width = int(9 * reel_height // 16)
    reel_frame_size = (reel_width, reel_height)

    # Frame size set to vertical format for Instagram reels
    create_reel_from_clip(video_clip, camera_path, reel_frame_size, game_code)

    # Frame size set to square format for Instagram reels
    reel_height = int(2 * original_frame_height // 3)
    reel_width = reel_height
    reel_frame_size = (reel_width, reel_height)
    create_reel_from_clip(video_clip, camera_path, reel_frame_size, game_code)

    # Frame size between vertical and square format for Instagram reels
    reel_height = int(2 * original_frame_height // 3)
    reel_width = int(reel_height*1080//1350)
    reel_frame_size = (reel_width, reel_height)
    create_reel_from_clip(video_clip, camera_path, reel_frame_size, game_code)

    return None

def put_reels_into_gcp_bucket(game_code, post_process = False):
    '''
    Function to look into a folder and put all the reels into the GCP bucket
    '''
    print('Putting reels into GCP bucket')
    bucket_name = 'street-bucket'

    # Get the list of files in the folder
    reel_clips_folder = './data/reel_clips/'+ game_code + '/'
    reel_clips = os.listdir(reel_clips_folder)

    # Put the files into the GCP bucket
    for reel_clip_file_name in reel_clips:

        if post_process:
            reel_clip = VideoFileClip(reel_clips_folder + reel_clip_file_name)
            print('\n\nPost processing the video clip...')
            reel_clip = reel_clip.fl_image(enhance_colors)
            reel_clip = reel_clip.fl_image(reduce_glare_and_haziness)
            reel_clip = reel_clip.fl_image(sharpen_image)
            # Write post processed video clip to a file
            reel_clip.write_videofile(reel_clips_folder + reel_clip_file_name)

        source_file_path = reel_clips_folder + reel_clip_file_name
        destination_blob_name = 'reel_clips/' + game_code + '/' + reel_clip_file_name

        print(f"Uploading '{reel_clip_file_name}' to GCP bucket.")
        upload_file_to_gcp_bucket(bucket_name, source_file_path, destination_blob_name)

def put_ripley_dataset_into_gcp_bucket(game_code):
    '''
    Function to look into a folder and put all the reels into the GCP bucket
    '''
    print('Putting reels into GCP bucket')
    bucket_name = 'street-bucket'

    # Get the list of files in the folder
    ripley_reel_dataset_folder = './data/ripley_dataset/' + game_code + '/'
    ripley_files = os.listdir(ripley_reel_dataset_folder)

    # Put the files into the GCP bucket
    for ripley_file in ripley_files:
        source_file_path = ripley_reel_dataset_folder + ripley_file
        destination_blob_name = 'ripley_dataset/' + game_code + '/' + ripley_file

        print(f"Uploading '{ripley_file}' to GCP bucket.")
        upload_file_to_gcp_bucket(bucket_name, source_file_path, destination_blob_name)

def make_reels(game_code):
    '''
    Function to make reels from the game clips - based on software camera output
    Input:
    - game_code: Game code to make reels from

    Output:
    - None

    Approach:
    - Check if the reels output path exists, and if not, create it
    - Get the available reel number
    - Read the camera path from the json file
    - Create a reel from the game clip
    - Put the reel into the GCP bucket
    '''
    
    reels_output_path = './data/reel_clips/'+ game_code + '/'
    # Check if the directory exists, and if not, create it
    if not os.path.exists(reels_output_path):
        os.makedirs(reels_output_path)
        print(f"Directory '{reels_output_path}' created.")
    
    available_reel_num = 0
    file_found = True
    while file_found:
        if not os.path.isfile('./test_and_delete/reel_info/ref_clip_' + str(available_reel_num) + '.mp4'):
            file_found = False
            break
        else:
            available_reel_num += 1

    for i in range(available_reel_num):
        # Read everything
        new_camera_path = None
        # Read the camera path from the json file
        with open('./test_and_delete/reel_info/ball_path_'+str(i)+'.json', 'r') as file:
            new_camera_path = json.load(file)
        
        new_clip_for_reference = VideoFileClip('./test_and_delete/reel_info/ref_clip_'+str(i)+'.mp4')

        create_reels(new_clip_for_reference, new_camera_path, game_code)

    put_reels_into_gcp_bucket(game_code)

    print('Reels created successfully')

def create_ripley_reels(game_code):
    '''
    Function to create reels from the ripley dataset
    Input:
    - game_code: Game code to create reels from

    Output:
    - None

    Approach:
    - Get the list of files in the folder [files are numebered 0, 1, 2, ...]
    - For each file, create a reel
    - Put the reels into the GCP bucket
    '''
    print('Creating reels from ripley dataset')

    # Get the list of files in the folder
    ripley_reel_dataset_folder = './data/ripley_dataset/' + game_code + '/'

    i = 0
    file_found = True
    while file_found:
        if not os.path.isfile(ripley_reel_dataset_folder + 'original_clip_'+str(i)+'.mp4'):
            file_found = False
            break
        else:
            i += 1
    reel_number = i

    for i in range(reel_number):
        
        original_clip = VideoFileClip(ripley_reel_dataset_folder + 'original_clip_'+str(i)+'.mp4')
        clip_with_tracks = VideoFileClip(ripley_reel_dataset_folder + 'clip_with_tracks_'+str(i)+'.mp4')
        ripley_reel_original = VideoFileClip(ripley_reel_dataset_folder + 'ripley_'+str(i)+'.mp4')
        people_track_timeline_file_path = ripley_reel_dataset_folder + 'people_track_timeline_string_'+str(i)+'.txt'

        ripley_reel = create_ripley_reel_from_video_clip(original_clip, people_track_timeline_file_path)

        # Write the ripley reel to a file in the ripley_reel_dataset_folder
        new_reel_path = ripley_reel_dataset_folder + 'ripley_reel_new_'+str(i)+'.mp4' 
        # Switch to 'ripley_'+str(i)+'.mp4' when it works

        ripley_reel.write_videofile(new_reel_path)

        print('New Ripley reel created successfully')
        print('File saved as: '+ new_reel_path)
    
    return None





def make_reels_from_ripley_dataset(game_code):
    '''
    Function to make reels from the ripley dataset
    
    Input:
    - game_code: Game code to make reels from

    Output:
    - None

    Approach:
    - Check local directory for the ripley dataset for the game code
    - If not found, check the bucket for the ripley dataset for the game code
    - Download the ripley files from the game code folder
        There are 4 files for each reel each with _0, _1, _2, _3 suffixes:
        - original_clip_0.mp4
        - clip_with_tracks_0.mp4
        - ripley_0.mp4
        - people_track_timeline_string_0.txt
    - Create reels from the ripley files
    - Put the reels into the GCP bucket
    '''
    print('Making reels from ripley dataset for game code: ', game_code)
    bucket_name = 'street-bucket'

    # Get the list of files in the folder
    ripley_reel_dataset_folder = './data/ripley_dataset/' + game_code + '/'
    
    # Check if the directory exists, and if not, create it
    if not os.path.exists(ripley_reel_dataset_folder):
        os.makedirs(ripley_reel_dataset_folder)
        print(f"Directory '{ripley_reel_dataset_folder}' created.")
    else:
        print(f"Directory '{ripley_reel_dataset_folder}' already exists.")

        source_folder = 'ripley_dataset/' + game_code + '/'
        destination_folder = './data/ripley_dataset/' + game_code + '/'
        
        download_blobs_in_folder(bucket_name, source_folder, destination_folder)
    
    # Create reels from the ripley files
    create_ripley_reels(game_code)

    # Put the reels into the GCP bucket
    put_ripley_dataset_into_gcp_bucket(game_code)

    print('Reels created successfully')

    return None

def create_goal_highlight_reels(game_code):
    '''
    Function to create goal highlight reels

    Approach:
    - Get the list of ripley reel files in the temp_game_files folder
    - Read the files in a loop
    - Concatenate the files
    - Create a reel from the concatenated video
    - Put the reel into the GCP bucket
    '''
    print('Creating goal highlight reels for game code: ', game_code)
    
    # Get the list of ripley reel files in the temp_game_files folder
    ripley_reel_files = os.listdir('./test_and_delete/temp_game_files/')
    ripley_reel_files = [file for file in ripley_reel_files if file.endswith('.mp4') and 'ig_output' in file]

    max_files = len(ripley_reel_files)

    # Read the files in a loop
    ripley_reel_list = []
    for i in range(max_files):
        
        ripley_file_name = 'ig_output_'+str(i)+'.mp4'

        # Read the file into a VideoFileClip object
        ripley_reel = VideoFileClip('./test_and_delete/temp_game_files/' + ripley_file_name)

        # Add to a list
        ripley_reel_list.append(ripley_reel)
    
    # Concatenate the files
    goal_highlight_reel = concatenate_videoclips(ripley_reel_list)

    # Put the goal highlight reel into the reel_clips folder for the game code
    goal_highlight_reel.write_videofile('./data/reel_clips/' + game_code + '/goal_highlight_reel.mp4', audio_codec="aac")

    return None
    
    
        
    

def main():

    #make_reels('Game65_1030')

    make_reels_from_ripley_dataset('Game65_1030')
    '''
    reel_name_list = ['bellandur_blast']

    reel_name = reel_name_list[0]

    # VM folder path details
    reel_details = get_reel_file_details(reel_name)
    

    if not os.path.isfile(reel_details['vm_file_path']):
        source_folder = 'game-recordings/' + reel_details['game_code'] + '/'
        destination_folder = './data/game-recordings/' + reel_details['game_code'] + '/'
        
        source_blob_name = source_folder + reel_details['file_name']
        destination_file_name = destination_folder + reel_details['file_name']

        print(f"Downloading '{reel_details['file_name']}' from GCP bucket.")
        download_single_file_from_gcp_bucket(source_blob_name, destination_file_name)

    
    # Read the intro clip video file
    full_video = VideoFileClip(reel_details['vm_file_path'])

    # Get the intro clip based on the start and end times
    reel_clip = full_video.subclip(reel_details['clip_start'], reel_details['clip_end'])

    # Replace ball path with detections from ball_tracking
    # reel_clip is a moviepy video clip object
    # ball_path = get_ball_path_from_tracking(reel_clip)

    # Create a test ball path for the video
    end_time = reel_clip.duration
    original_width, original_height = reel_clip.size
    
    ball_path = [{'timestamp': 0, 'x': original_width, 'y': 0},
                    
                { 'timestamp': 0.4 *end_time*1000,
                    'x': 0.4 * original_width, 'y': 0.5 * original_height},

                { 'timestamp': end_time*1000, 
                    'x': 0.4 * original_width, 'y': 0.5 * original_height}]
    
    # Use the ball path for a moving reem camera
    #reel_format_clip = VideoEditor().add_moving_zoom_to_video(reel_clip, ball_path)

    #print(reel_format_clip.size)
    #reel_format_clip.write_videofile('./test_and_delete/reel_clip.mp4', 
     #                                codec="libx264", audio_codec="aac")
     # 
    '''

    return None

if __name__ == "__main__":
    main()
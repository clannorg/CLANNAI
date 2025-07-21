
import cv2 as cv
import numpy as np
import os

from PIL import Image, ImageFilter
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from moviepy.editor import concatenate_videoclips

from .video_editor import VideoEditor
from .video_effects import enhance_colors, reduce_glare_and_haziness, sharpen_image

from street.video_editing.watermark import add_watermark


def resize_image_to_fit_with_margin(image, video, margin_percentage=0.1):

    # Get the frame size (width and height)
    frame_size = video.get_frame_size()

    # Extract width and height from the size
    frame_width, frame_height = frame_size

    # Calculate the margin in pixels
    margin_width = int(frame_width * margin_percentage)
    margin_height = int(frame_height * margin_percentage)

    # Calculate the new target size with margins
    target_width = frame_width - 2 * margin_width
    target_height = frame_height - 2 * margin_height

    # Get the original dimensions of the image
    original_width, original_height = image.size

    # Calculate the aspect ratios
    aspect_ratio_image = original_width / original_height
    aspect_ratio_target = target_width / target_height

    # Determine the new size based on the aspect ratio comparison
    if aspect_ratio_image > aspect_ratio_target:
        # The image is wider relative to the target area
        new_width = target_width
        new_height = int(target_width / aspect_ratio_image)
    else:
        # The image is taller relative to the target area
        new_height = target_height
        new_width = int(target_height * aspect_ratio_image)

    # Resize the image to the new size
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)

    # Apply a sharpening filter to the resized image
    sharpened_image = resized_image.filter(ImageFilter.SHARPEN)

    # Create a new image with a white background and the original frame size
    final_image = Image.new("RGBA", (frame_width, frame_height), (255, 255, 255, 255))

    # Calculate the position to center the resized image on the background with margins
    position = (margin_width + (target_width - new_width) // 2, 
                margin_height + (target_height - new_height) // 2)

    # Paste the resized image onto the white background
    final_image.paste(sharpened_image, position, resized_image)

    return final_image

def read_and_resize_logo(logo_path, video, logo_mod_path = None):
    '''
    This function reads the logo image and resizes it to fit the video frame size with a margin.

    Inputs:
    - logo_path (str): The path to the logo image file.
    - video (VideoEditor): The video to which the logo will be added.

    Returns:
    - Image: The resized logo image.

    Steps:
    1. Read the logo image.
    2. Resize the image based on the video frame size with a margin.
    3. Return the resized logo image.
    '''

    logo_mod_path = './data/logo/STREET_logo_mod.png'  # Path to the resized logo image

    # Resize the image based on the video frame size with a margin and save it
    image = Image.open(logo_path)
    image = resize_image_to_fit_with_margin(image, video)
    image.save(logo_mod_path)

    return logo_mod_path

def get_logo_clip(video, duration=1):
    '''
    This function creates a logo clip with the STREET logo.

    Inputs:
    - video (VideoEditor): The video to which the logo clip will be added.
    - duration (float): The duration of the logo clip in seconds.

    Returns:
    - VideoClip: The logo clip with the STREET logo.

    Steps:
    1. Read the logo image.
    2. Resize the image based on the video frame size with a margin.
    3. Create an ImageClip for the image, with the specified duration.
    '''

    # Path to the logo image
    logo_read_path = './data/logo/STREET_logo_large.png'  # Path to your logo image
    logo_mod_path = read_and_resize_logo(logo_read_path, video) # Returns the path to the resized logo image

    # Create an ImageClip for the image, with the specified duration
    logo_clip = ImageClip(logo_mod_path).set_duration(duration).set_fps(video.fps)

    logo_clip = concatenate_videoclips([logo_clip])
    return logo_clip

def add_logo_to_video(video, duration=1):
    '''
    This function adds the STREET logo to the video at the beginning and end.

    Steps:
    1. Read the logo image.
    2. Resize the image based on the video frame size with a margin.
    3. Create an ImageClip for the image, with the specified duration (2 seconds).
    4. Concatenate the image at the end of the video.
    '''
    # Add the STREET logo to the video

    # Create an ImageClip for the image, with the specified duration (2 seconds)
    image_clip = get_logo_clip(video, duration)
    
    # Concatenate the image at the beginning and the end of the video
    final_video = concatenate_videoclips([video.get_video_clip(), image_clip])
    
    return VideoEditor(final_video)

def get_intro_clip_filename(clip_code):
    '''
    This function returns the filename of the intro clip based on the clip code.

    Steps:
    1. Create a dictionary mapping the clip codes to the filenames.
    2. Return the filename based on the clip code.
    '''
    game_recordings_folder = './data/game-recordings/'
    clip_code_to_filename = {
        'ball_to_cam': game_recordings_folder + 'Game6_0831/Game6_0831_p2.mp4',
        'hello_albert': game_recordings_folder + 'Game16_0916/Game16_0916_p1.mp4',
        'hello_stanford': game_recordings_folder + 'Game15_0918/Game15_0918_p1.mp4',
        'trafford_celebration': game_recordings_folder + 'Game23_1004/Game23_1004_p1.mp4',
        'bellandur_blast': game_recordings_folder + 'Game27_1006/Game27_1006_p1.mp4',
        'bellandur_save': game_recordings_folder + 'Game30_1006/Game30_1006_p3.mp4',
        'bellandur_celebration': game_recordings_folder + 'Game30_1006/Game30_1006_p3.mp4',
        'stanford_sniper': game_recordings_folder + 'Game9_0911/Game9_0911_p1.mp4',
        'reflex_save': game_recordings_folder + 'Game42_1013/Game42_1013_p1.mp4',
        'nutmeg_save': game_recordings_folder + 'Game52_1020/Game52_1020_p1.mp4',
        'bellandur_winner': game_recordings_folder + 'Game62_1027/Game62_1027_p2.mp4',
        'net_ripper': game_recordings_folder + 'Game63_1028/Game63_1028_p1.mp4',
        'boyfun_cartwheel': game_recordings_folder + 'Game64_1028/Game64_1028_p3.mp4',
        'face_of_vyasa': game_recordings_folder + 'Game65_1030/Game65_1030_p2.mp4',
        'real_blr_fc_intro': game_recordings_folder + 'Game84_0113/Game84_0113_p1.mp4',
        'boyfun_power': game_recordings_folder + 'Game130_0210/Game130_0210_p2.mp4'
    }

    return clip_code_to_filename[clip_code]

def get_intro_clip_time(intro_clip_name = 'ball_to_cam'):
    
    clip_name_to_cut_time = {}
    
    clip_code = 'ball_to_cam'
    clip_start = 41*60 + 34
    clip_end = clip_start + 2
    clip_name_to_cut_time[clip_code] = (clip_start, clip_end)

    clip_code = 'hello_albert'
    clip_start = 3*60 + 6
    clip_end = clip_start + 1
    clip_name_to_cut_time[clip_code] = (clip_start, clip_end)

    clip_code = 'hello_stanford'
    clip_start = 74*60 + 21
    clip_end = clip_start + 2
    clip_name_to_cut_time[clip_code] = (clip_start, clip_end)

    clip_code = 'trafford_celebration'
    clip_start = 74*60 + 48
    clip_end = clip_start + 4
    clip_name_to_cut_time[clip_code] = (clip_start, clip_end)

    clip_code = 'bellandur_blast'
    clip_start = 5*60 + 42
    clip_end = clip_start + 3
    clip_name_to_cut_time[clip_code] = (clip_start, clip_end)

    clip_code = 'bellandur_save'
    clip_start = 2*60 + 34
    clip_end = clip_start + 3
    clip_name_to_cut_time[clip_code] = (clip_start, clip_end)

    clip_code = 'bellandur_celebration'
    clip_start = 2*60 + 43
    clip_end = clip_start + 3
    clip_name_to_cut_time[clip_code] = (clip_start, clip_end)

    clip_code = 'stanford_sniper'
    clip_start = 41*60 + 39
    clip_end = clip_start + 4
    clip_name_to_cut_time[clip_code] = (clip_start, clip_end)

    clip_code = 'reflex_save'
    clip_start = 8*60 + 27
    clip_end = clip_start + 3
    clip_name_to_cut_time[clip_code] = (clip_start, clip_end)

    clip_code = 'nutmeg_save'
    clip_start = 21*60 + 55
    clip_end = clip_start + 3
    clip_name_to_cut_time[clip_code] = (clip_start, clip_end)

    clip_code = 'bellandur_winner'
    clip_start = 11*60 + 8
    clip_end = clip_start + 4
    clip_name_to_cut_time[clip_code] = (clip_start, clip_end)

    clip_code = 'net_ripper'
    clip_start = 36*60 + 28
    clip_end = clip_start + 4
    clip_name_to_cut_time[clip_code] = (clip_start, clip_end)

    clip_code = 'boyfun_cartwheel'
    clip_start = 1*60 + 0
    clip_end = clip_start + 3
    clip_name_to_cut_time[clip_code] = (clip_start, clip_end)

    clip_code = 'face_of_vyasa'
    clip_start = 48*60 + 13
    clip_end = clip_start + 3
    clip_name_to_cut_time[clip_code] = (clip_start, clip_end)

    clip_code = 'real_blr_fc_intro'
    clip_start = 0*60 + 5
    clip_end = clip_start + 4
    clip_name_to_cut_time[clip_code] = (clip_start, clip_end)

    clip_code = 'boyfun_power'
    clip_start = 25*60 + 25
    clip_end = clip_start + 3
    clip_name_to_cut_time[clip_code] = (clip_start, clip_end)

    return clip_name_to_cut_time[intro_clip_name]

def get_intro_clip_from_file(intro_clip_name):

    # Read from intro_clip_name+'.mp4 if the file exists
    intro_clips_folder = './data/intro_clips/'
    intro_clip_path = intro_clips_folder + intro_clip_name + '.mp4'

    # Check if the intro clip file exists
    if os.path.isfile(intro_clip_path):
        intro_clip = VideoFileClip(intro_clip_path)
    else:
        # Get the start and end times for the intro clip
        clip_start, clip_end = get_intro_clip_time(intro_clip_name)

        # Read the intro clip video file
        intro_video = VideoFileClip(get_intro_clip_filename(intro_clip_name))

        # Get the intro clip based on the start and end times
        intro_clip = intro_video.subclip(clip_start, clip_end)

        
        # Save the intro clip to a new video file
        # Post-process the intro clip
        post_proc_logo = False

        if post_proc_logo == True:
            intro_clip = intro_clip.fl_image(enhance_colors).fl_image(reduce_glare_and_haziness).fl_image(sharpen_image)
            # Write the final video to the output file
            intro_clip.write_videofile(intro_clip_path, codec='libx264', bitrate="12067k", audio_codec='aac')
        else:
            VideoEditor(intro_clip).save_video(intro_clip_path)
        
    intro_clip = concatenate_videoclips([intro_clip])
    return intro_clip

def add_intro_to_video(video, intro_clip_name = 'ball_to_cam'): # intro_clip_path, clip_start_time, clip_end_time):
    '''

    This function adds an intro clip to the video.

    Inputs:
    - video (VideoEditor): The video to which the intro clip will be added.
    - intro_clip_name (str): The name of the intro clip to be added.

    Returns:
    - VideoEditor: The video with the intro clip added.

    Steps:
    1. Read the intro clip video file.
    2. Get the duration of the intro clip.
    3. Add the logo to the intro clip
    4. Concatenate the intro clip with the video.
    '''
    
    # Duration of the logo clip
    logo_duration = 1
    # intro_clip_name = 'hello_stanford'
    # Create an ImageClip for the image, with the specified duration (2 seconds)
    logo_clip = get_logo_clip(video, logo_duration)

    # Read the intro clip video file
    intro_clip = get_intro_clip_from_file(intro_clip_name) # VideoFileClip object

    # Watermark the video
    video_with_watermark = add_watermark(video.get_video_clip())

    # Assert the videos being concatenated are of the same frame size
    print(video_with_watermark.size)
    print(intro_clip.size)
    print(logo_clip.size)
    # Resize the intro clip to (1920, 1080)
    intro_clip = intro_clip.resize((1920, 1080))
    assert video_with_watermark.size == intro_clip.size == logo_clip.size, "All videos must have the same frame size"


    # Concatenate the image at the beginning and the end of the video
    final_video = concatenate_videoclips([intro_clip, logo_clip, video_with_watermark])

    return VideoEditor(final_video)
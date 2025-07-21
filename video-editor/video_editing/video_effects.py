import os
import cv2 as cv
import numpy as np
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

from .image_effects import create_text_image, create_img_clip



def sharpen_image(image):
    '''
    kernel = np.array([[0, -1, 0], 
                       [-1, 5,-1], 
                       [0, -1, 0]])
    '''
    
    # softer sharpening kernel than previous
    kernel = np.array([[0, -0.5, 0],
                       [-0.5, 3, -0.5],
                       [0, -0.5, 0]])
    final = cv.filter2D(src=image, ddepth=-1, kernel=kernel)
    return cv.addWeighted(final, 0.6, image, 0.4, 0)
    
def smooth_image(image):
    return cv.GaussianBlur(image, (5, 5), 0)

def reduce_glare_and_haziness(image):

    gamma = 1.2
    clip_limit = 1.0

    
    lab = cv.cvtColor(image, cv.COLOR_RGB2LAB)
    l_channel, a, b = cv.split(lab)
    clahe = cv.createCLAHE(clipLimit=clip_limit, tileGridSize=(8,8))
    cl = clahe.apply(l_channel)
    limg = cv.merge((cl,a,b))
    final = cv.cvtColor(limg, cv.COLOR_LAB2RGB)
    look_up_table = np.empty((1,256), np.uint8)
    for i in range(256):
        look_up_table[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
    final = cv.LUT(final, look_up_table)
    # Blend with the original image
    return cv.addWeighted(final, 0.6, image, 0.4, 0)

def enhance_colors(image):
    hsv = cv.cvtColor(image, cv.COLOR_RGB2HSV)
    h, s, v = cv.split(hsv)
    s = cv.multiply(s, 1.5)
    s = np.clip(s, 0, 255)
    hsv_enhanced = cv.merge([h, s, v])
    return cv.cvtColor(hsv_enhanced, cv.COLOR_HSV2RGB)




def get_scoreline_watermark(game_info, duration):
    """
    Creates a watermark displaying the scoreline of a soccer game.

    Parameters:
    - game_info (dict): A dictionary containing the game information.
        The dictionary should have the following keys:
        - left_name (str): The name of the team on the left.
        - left_score (int): The score of the team on the left.
        - right_name (str): The name of the team on the right.
        - right_score (int): The score of the team

    Returns:
    - watermark (CompositeVideoClip): A clip that can be overlaid on a video.
    """
    team1_name = game_info['left_team']
    team1_goals = game_info['left_score']
    team2_name = game_info['right_team']
    team2_goals = game_info['right_score']

    game_code = game_info['game_code']

    # Create TextClips for team names and goals
    #font = 'Arial'  # Ensure the font is installed on your system
    #fontsize = 40
    #color = 'black'

    score_text = f"{team1_name} {team1_goals} - {team2_goals} {team2_name}"
    print('\n\n=======',score_text,'=======\n\n')

    score_image = create_text_image(score_text)
    score_clip = create_img_clip(score_image, duration)

    # score_clip = TextClip(score_text, fontsize=fontsize, color=color, font=font)
    # TextClip did not work for weird reasons

    # Calculate background size based on text sizes
    text_w, text_h = score_clip.size

    padding = 10
    bg_width = text_w + 2 * padding
    bg_height = text_h + 3 * padding

    # Create a semi-transparent background
    bg_color = (255, 255, 255)  # White background
    background = ColorClip(size=(int(bg_width), int(bg_height)), color=bg_color)
    background = background.set_opacity(1.0)

    # Position the TextClips on the background
    score_clip = score_clip.set_position((padding, padding))

    # Composite the background and the TextClips
    watermark = CompositeVideoClip([background, score_clip])

    return watermark

def get_game_clock_watermark(time_min, time_sec, duration):
    """
    Creates a watermark displaying the game clock.

    Parameters:
    - time_min (int): The minutes to display on the game clock.
    - time_sec (int): The seconds to display on the game clock.

    Returns:
    - watermark (CompositeVideoClip): A clip that can be overlaid on a video.
    """
    # Format time as MM:SS
    time_text = f"{time_min:02d}:{time_sec:02d}"

    # Create a TextClip for the game clock
    font = 'Arial'  # Ensure the font is installed on your system
    fontsize = 40
    color = 'black'

    time_img = create_text_image(time_text)
    time_clip = create_img_clip(time_img, duration)
    # Calculate background size based on text size
    time_w, time_h = time_clip.size

    padding = 10
    bg_width = time_w + 2 * padding
    bg_height = time_h + 2 * padding

    # Create a semi-transparent background
    bg_color = (255, 255, 255)  # White background
    background = ColorClip(size=(int(bg_width), int(bg_height)), color=bg_color)
    background = background.set_opacity(0.5)

    # Position the TextClip on the background
    time_clip = time_clip.set_position((padding, padding))

    # Composite the background and the TextClip
    watermark = CompositeVideoClip([background, time_clip])

    return watermark


def get_camera_views():
    '''
    Function to provide the camera views and their corresponding bounding boxes.

    Returns:
    Dictionary: A dictionary containing the camera views and their corresponding bounding boxes.
    '''
    view_name_to_bbox = dict()

    # Full screen
    left = 0.0
    right = 1.0
    top = 0.0
    bottom = 1.0
    view_name_to_bbox['full_screen'] = (left, top, right, bottom)
    view_name_to_bbox['full'] = (left, top, right, bottom)

    # Top half ot the screen, centered
    left = 0.25
    right = 0.75
    top = 0.0
    bottom = 0.5
    view_name_to_bbox['top_half_centered'] = (left, top, right, bottom)

    # Bottom half ot the screen, centered
    left = 0.25
    right = 0.75
    top = 0.5
    bottom = 1.0
    view_name_to_bbox['bottom_half_centered'] = (left, top, right, bottom)

    # Top two third of the screen, centered
    left = 0.18
    right = 0.83
    top = 0.0
    bottom = 0.66
    view_name_to_bbox['top_two_third_centered'] = (left, top, right, bottom)
    view_name_to_bbox['top_mid_two_third'] = (left, top, right, bottom)
    

    # Bottom two third of the screen, centered
    left = 0.18
    right = 0.83
    top = 0.33
    bottom = 1.0
    view_name_to_bbox['bottom_two_third_centered'] = (left, top, right, bottom)


    # Top left, two third
    left = 0.0
    right = 0.66
    top = 0.0
    bottom = 0.66
    view_name_to_bbox['top_left_two_third'] = (left, top, right, bottom)

    # Top right, two third
    left = 0.33
    right = 1.0
    top = 0.0
    bottom = 0.66
    view_name_to_bbox['top_right_two_third'] = (left, top, right, bottom)

    # Bottom left, two third
    left = 0.0
    right = 0.66
    top = 0.33
    bottom = 1.0
    view_name_to_bbox['bottom_left_two_third'] = (left, top, right, bottom)

    # Bottom right, two third
    left = 0.33
    right = 1.0
    top = 0.33
    bottom = 1.0
    view_name_to_bbox['bottom_right_two_third'] = (left, top, right, bottom)

    # Middle, left two third
    left = 0.0
    right = 0.66
    top = 0.17
    bottom = 0.83
    view_name_to_bbox['mid_left_two_third'] = (left, top, right, bottom)
    view_name_to_bbox['left_two_third'] = (left, top, right, bottom)


    # Middle, right two third
    left = 0.33
    right = 1.0
    top = 0.17
    bottom = 0.83
    view_name_to_bbox['mid_right_two_third'] = (left, top, right, bottom)
    view_name_to_bbox['right_two_third'] = (left, top, right, bottom)

    # Middle, middle two third
    left = 0.17
    right = 0.83
    top = 0.17
    bottom = 0.83
    view_name_to_bbox['mid_two_third'] = (left, top, right, bottom)

    # Middle, left half
    left = 0.0
    right = 0.5
    top = 0.17
    bottom = 0.83
    view_name_to_bbox['mid_left_half'] = (left, top, right, bottom)

    # Middle, right half
    left = 0.5
    right = 1.0
    top = 0.17
    bottom = 0.83
    view_name_to_bbox['mid_right_half'] = (left, top, right, bottom)



    return view_name_to_bbox


def crop_and_resize_video_clip(video_clip, bbox_name = None):

    name_to_bbox = get_camera_views()

    video_original_width = video_clip.size[0]
    video_original_height = video_clip.size[1]
    # Crop video frame based on boundinb box
    if bbox_name is None or bbox_name not in name_to_bbox:
        bbox = name_to_bbox['full_screen']
    else:
        try:
            bbox = name_to_bbox[bbox_name]
        except:
            print('\n\n==================Invalid camera view name. Using default camera view.==================\n\n')
            bbox = name_to_bbox['full_screen']
        
    bbox_left   = bbox[0] * video_original_width
    bbox_top    = bbox[1] * video_original_height
    bbox_right  = bbox[2] * video_original_width
    bbox_bottom = bbox[3] * video_original_height

    video_clip_cropped = video_clip.crop(
        x1=bbox_left, 
        y1=bbox_top, 
        x2=bbox_right, 
        y2=bbox_bottom)
    
    #print('\n\nIN CROP AND RESIZE VIDEO CLIP')
    '''
    # Write audio of video_clip_cropped to a file
    video_clip_cropped.audio.write_audiofile('./test_and_delete/temp_game_files/test_audio_after_crop_temp.mp3')
    video_clip_cropped.write_videofile('./test_and_delete/temp_game_files/test_video_after_crop_temp.mp4')
    '''

    # Resize cut video clip to original video frame size
    video_clip_resized = video_clip_cropped.resize((video_original_width, 
                                                    video_original_height))

    '''
    # Write audio of video_clip_resized to a file
    video_clip_resized.audio.write_audiofile('./test_and_delete/temp_game_files/test_audio_after_resize_temp.mp3')
    video_clip_resized.write_videofile('./test_and_delete/temp_game_files/test_video_after_resize_temp.mp4')

    print('\n\nDONE IN CROP AND RESIZE VIDEO CLIP')
    x = 5 + 's'
    # '''
    
    
    return video_clip_resized

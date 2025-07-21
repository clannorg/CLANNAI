'''
Functions to add a watermark to a video.
'''

import cv2
import numpy as np
from moviepy.editor import ImageClip, CompositeVideoClip, concatenate_videoclips


def add_watermark(video_clip, opacity=0.8, scale=0.2, logo_path = './data/logo/STREET_logo_large.png'):

    # Load and resize the logo
    logo = ImageClip(logo_path)

    video_width, video_height = video_clip.size

    print('VIDEO SIZE:', video_width, video_height)


    if video_width >= video_height:
        print('PAN WATERMARK')
        logo = logo.resize(width=video_width * scale).set_duration(video_clip.duration)
    else:
        print('PORTRAIT WATERMARK')
        logo = logo.resize(width=video_width * 0.35).set_duration(video_clip.duration)
    
    if video_width == 576 and video_height == 720:
        logo = logo.resize(width=video_width * 0.3).set_duration(video_clip.duration)

    # Set opacity [Set Below during inversion]
    #if opacity < 1.0:
    #    logo = logo.set_opacity(opacity)
    

    # Bottom left position
    #x = 0
    #y = video_height - logo.size[1]

    # Bottom right position
    x = video_width - logo.size[0]

    # For moving watermark left from bottom right corner
    x = video_width - int(1.5*logo.size[0])
    y = video_height - logo.size[1]

    # Top right position
    #x = video_width - logo.size[0]
    #y = 0

    print('CLIP SIZE:', video_clip.size)
    print('LOGO SIZE:', logo.size)
    print('LOGO POSITION:', x, y)
    

    # Convert ImageClip to NumPy array (frame)
    logo_watermark = logo.get_frame(0)  # Get the first frame as NumPy array

    #logo_watermark = logo
    # Convert to grayscale
    gray = cv2.cvtColor(logo_watermark, cv2.COLOR_BGR2GRAY)

    # Set alpha for black areas to 50% opacity, and white areas to fully transparent
    alpha = np.where(gray <= 128, int(255 * opacity), 0).astype(np.uint8)  # Black -> 50% opacity, other -> fully transparent
    
    # Make the black parts of the watermark white and set their alpha to 50% opacity
    logo_watermark[gray <= 128] = [255, 255, 255]
    
    # Merge the RGB channels with the alpha channel to get the final processed watermark
    processed_logo_watermark = cv2.merge((*cv2.split(logo_watermark), alpha))

    logo = ImageClip(processed_logo_watermark).set_duration(video_clip.duration)

    # Position the logo at specific coordinates
    logo = logo.set_position((x, y))

    # Composite the logo onto the video
    video_with_logo = concatenate_videoclips([CompositeVideoClip([video_clip, logo])])
    print('Video with logo TYPE',type(video_with_logo))

    return video_with_logo
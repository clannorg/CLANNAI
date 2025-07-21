from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip
import numpy as np
import os

def get_available_fonts():
    """
    Returns a list of available font paths on the system.
    
    Returns:
    - list: A list of font file paths.
    """
    from matplotlib.font_manager import findSystemFonts
    font_paths = findSystemFonts()
    return font_paths

def create_text_image(score_text, font_size=40, font_color=(0, 0, 0), 
                       bg_color=(255, 255, 255, 255), font_path=None, 
                       padding=20):
    """
    Creates an image of the score with a semi-transparent background.
    
    Parameters:
    - score_text (str): The text to render.
    - font_size (int): The size of the font.
    - font_color (tuple): The color of the text in RGB.
    - bg_color (tuple): The background color in RGBA (with alpha for transparency).
    - font_path (str): Path to the .ttf font file. If None, the default font is used.
    - padding (int): The padding around the text.
    
    Returns:
    - PIL.Image: An image object with the rendered text and background.
    """
    # Replace spaces in the score text with underscores
    score_text_for_fname = score_text.replace(' ', '_')
    scoreline_filename = f"./test_and_delete/temp_game_files/scoreline_{score_text_for_fname}.png"

    if os.path.exists(scoreline_filename):
        return Image.open(scoreline_filename)
    
    # Define the font path
    # fonts_available = get_available_fonts()
    # print(fonts_available)
    font_paths = ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 
                  # A bold, clean sans-serif font that is highly legible and ideal for on-screen display.

                  '/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf', # This font is good for scorelines
                  # Similar in style to Helvetica or Arial, this bold sans-serif font offers excellent readability.

                  '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf' # No
                  # A bold sans-serif font with a modern look, suitable for making the scoreline stand out.
                  ]
    # Load bold font
    font_path = font_paths[1]
    if font_path:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            print(f"Font file not found at {font_path}. Using default font.")
            font = ImageFont.load_default()
    else:
        # font = ImageFont.load_default()

        font = ImageFont.truetype("Times New Roman", font_size)

    # Create a dummy image to calculate text size
    dummy_img = Image.new('RGBA', (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    
    # Calculate text size
    bbox = draw.textbbox((0, 0), score_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Calculate background size
    bg_width = text_width + 2 * padding
    bg_height = text_height + 2 * padding

    # Create the background image with transparency
    img = Image.new('RGBA', (bg_width, bg_height), color=bg_color)

    draw = ImageDraw.Draw(img)
    text_position = ((bg_width - text_width) // 2, (bg_height - text_height) // 2)
    draw.text(text_position, score_text, font=font, fill=font_color)

    # Save the image
    img.save(scoreline_filename)
    return img

def create_img_clip(img, duration):
    """
    Creates a video clip from a PIL image.

    Parameters:
    - img (PIL.Image): The image to convert into a video clip.
    - duration (int): The duration of the clip in seconds.

    Returns:
    - moviepy.editor.ImageClip: A video clip object.
    """
    # Convert PIL image to a NumPy array
    img_array = np.array(img)

    # Create an ImageClip from the array
    clip = ImageClip(img_array, transparent=True).set_duration(duration)
    
    return clip


#img = create_text_image("AB FC 1 : 0 CD FC", padding=10, font_size=24, font_color=(255, 255, 255), bg_color=(0, 0, 0))
#img.save("text_image.png")

# Sample game_info dictionary
game_info = {
    'left_team': 'AB FC',
    'left_score': 2,
    'right_team': 'CD FC',
    'right_score': 3
}

# Extract game information
team1_name = game_info['left_team']
team1_goals = game_info['left_score']
team2_name = game_info['right_team']
team2_goals = game_info['right_score']

# Define font and colors
# Use a bold font file
font_path = None #'path/to/Arial Bold.ttf'  # Replace with the actual path to your bold font file
font_size = 200  # Increase font size for bigger text
font_color = (0, 0, 0)  # Black text
bg_color = (255, 255, 255, 255)  # Full white background
padding = 10  # Increase padding for larger image

# Create the score text
score_text = f"{team1_name} {team1_goals} : {team2_goals} {team2_name}"
#print('\n\n=======', score_text, '=======\n\n')

# Create the score image
#score_img = create_text_image(score_text)

# Save the image (optional)
#score_img.save('score_image.png')
import os
from moviepy.editor import AudioFileClip, CompositeAudioClip
from moviepy.editor import concatenate_audioclips
from moviepy.editor import vfx
import numpy as np


from .video_effects import sharpen_image, reduce_glare_and_haziness, enhance_colors
from .post_process import add_intro_to_video, add_logo_to_video
from .watermark import add_watermark
from .video_editor import VideoEditor

def add_beat_to_video(video_editor_with_no_logo, audio_path, output_path, 
                      post_proc, include_logo, intro_clip_name):
    # Verify audio file exists and is readable
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Music file not found: {audio_path}")
        
    # Load and verify audio
    audio = AudioFileClip(audio_path)
    if audio.duration <= 0:
        raise ValueError(f"Invalid audio duration: {audio.duration}")

    if include_logo:
        # Add 2 seconds of the STREET logo at the beginning and end of the video
        # video_editor = add_logo_to_video(video_editor_with_no_logo) # Video going in and object being returned here is a VideoEditor object

        # Add the intro clip to the video
        video_editor = add_intro_to_video(video_editor_with_no_logo, intro_clip_name)
        # video_editor            = add_logo_to_video(video_editor_with_intro)


    else:
        video_editor = VideoEditor(add_watermark(video_editor_with_no_logo.get_video_clip()))

    # Get the VideoFileClip object from the VideoEditor object
    video = video_editor.get_video_clip()

    
    # Trim the audio to the length of the video if it's longer
    if audio.duration > video.duration:
        audio = audio.subclip(0, video.duration)

    # Loop the audio if it's shorter than the video
    if audio.duration < video.duration:
        audio_loops = int(video.duration // audio.duration)
        audio_remainder = video.duration % audio.duration
        audio_music = concatenate_audioclips([audio] * audio_loops + [audio.subclip(0, audio_remainder)])
    
    original_audio = video.audio

    # For games with commentary, use the original audio
    audio_combined = original_audio
    #audio_combined = audio_music

    # For games without commentary, add music
    audio_combined = CompositeAudioClip([original_audio, audio_music])
    
    #audio_combined.write_audiofile("./test_and_delete/test_audio.mp3")

    print(f"Audio duration: {audio_combined.duration}")
    print(f"Video duration: {video.duration}")

    # Set the audio to the video clip
    video_with_audio = video.set_audio(audio_combined)

    '''video_with_audio = (video_with_audio
                        #.fl_image(sharpen_image)
                        .fl_image(reduce_glare_and_haziness)
                        .fl_image(enhance_colors))
    #'''
    if post_proc == True:
        video_with_audio = video_with_audio.fl_image(enhance_colors)
        video_with_audio = video_with_audio.fl_image(reduce_glare_and_haziness)
        video_with_audio = video_with_audio.fl_image(sharpen_image)
        # Write the final video to the output file
        video_with_audio.write_videofile(output_path, codec='libx264', bitrate="12067k", audio_codec='aac') 
    else:
        #video_with_audio = video_with_audio#.fl_image(reduce_glare_and_haziness).fl_image(sharpen_image)
        video_with_audio.write_videofile(output_path, codec='libx264', audio_codec='aac')
    '''video_with_audio.write_videofile(
        output_path,
        codec='libx265',                # Use 'libx265' for HEVC (H.265) codec
        audio_codec='aac',              # Use 'aac' for audio codec (same as before)
        bitrate="15067k",               # Set the bitrate to match the input video's bitrate (approx. 15 Mbps)
        fps=29.97,                      # Set the frame rate to match the input video's frame rate
        preset='medium',                # Optional: Set the encoding preset for better compression balance
        ffmpeg_params=['-crf', '18']    # Optional: Set the CRF (Constant Rate Factor) for quality control
        )#'''

def run_music_effects(music_folder, music_file, video, output_video_path, 
                      post_proc=True, include_logo=True, intro_clip_name = None):
    

    # input_video_path = folder_path + game_code +'_all_only_video_vm003.mp4'
    audio_path = music_folder + music_file # Path to your audio file (the beat)

    # Show working directory
    print('\n\nWorking directory:', os.getcwd())
    
    add_beat_to_video(video, 
                      audio_path, 
                      output_video_path, 
                      post_proc, 
                      include_logo, 
                      intro_clip_name)

    return None


def main():
    return None

if __name__ == "__main__":
    main()

from moviepy.editor import VideoFileClip, vfx

# Specify the path to your .m2ts video file

folder_path = './data/game-recordings/Game72_1130/'
input_video_path = folder_path + 'Game72_1130_p1.m2ts'

# Load the .m2ts video file
clip = VideoFileClip(input_video_path)

clip = clip.set_fps(50)

print('BEFORE Clip duration:', clip.duration)
# m2ts 
corrected_clip = clip.fx(vfx.speedx, factor=0.5)

print('AFTER Clip duration:', corrected_clip.duration)

# Specify the output path for the .mp4 file
output_video_path = folder_path + 'Game72_1130_p1.mp4'

print('Writing file to ',output_video_path)
# Write the video clip to an .mp4 file
corrected_clip.write_videofile(output_video_path, 
                               codec='libx264',
                               audio_codec='aac',
                               bitrate='5000k',         # Increase video bitrate
                               audio_bitrate='192k',    # Increase audio bitrate
                               preset='slow',           # Use a slower preset for better compression
                               ffmpeg_params=['-crf', '18']  # Set constant rate factor for quality
                               )
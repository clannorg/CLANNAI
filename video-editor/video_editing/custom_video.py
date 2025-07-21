
from moviepy.editor import AudioFileClip, concatenate_audioclips
from moviepy.editor import VideoFileClip, concatenate_videoclips

from street.data_transfer.put_data_into_gcp_bucket import upload_file_to_gcp_bucket
from .post_process import get_intro_clip_from_file, get_logo_clip, add_watermark
from .video_editor import VideoEditor

def read_pitch_zoom(start, end):
    pitch_file = './data/game-recordings/GameX/pitch.mp4'
    pitch_clip = VideoFileClip(pitch_file).subclip(start, end)
    return pitch_clip

def get_highlight_cut(video):
    
    goal_clip_1 = add_watermark(get_intro_clip_from_file('bellandur_blast'), opacity=0.5, scale=0.1)
    goal_clip_2 = add_watermark(get_intro_clip_from_file('bellandur_save'), opacity=0.5, scale=0.1)
    goal_clip_3 = add_watermark(get_intro_clip_from_file('bellandur_celebration'), opacity=0.5, scale=0.1)
    goal_clip_4 = add_watermark(get_intro_clip_from_file('stanford_sniper'), opacity=0.5, scale=0.1)
    logo_clip = get_logo_clip(video)

    street_clip = concatenate_videoclips([goal_clip_1, goal_clip_2, goal_clip_3, goal_clip_4, logo_clip])
    
    return street_clip

def creat_pitch_video():

    pitch_clip_1 = read_pitch_zoom(311, 326)
    pitch_clip_2 = get_highlight_cut(VideoEditor(pitch_clip_1))
    pitch_clip_3 = read_pitch_zoom(13*60 + 10, 13*60 + 48)
    pitch_clip_4 = read_pitch_zoom(16*60 + 58.3, 17*60 + 13)
    pitch_clip_5 = read_pitch_zoom(19*60 + 27, 19*60 + 45)
    pitch_clip_6 = read_pitch_zoom(22*60 + 8, 22*60 + 28)
    logo_clip = get_logo_clip(VideoEditor(pitch_clip_1), 0.5)

    final_clip = concatenate_videoclips([pitch_clip_1, pitch_clip_2, pitch_clip_3, pitch_clip_4, pitch_clip_5, pitch_clip_6, logo_clip])
    final_clip.write_videofile('./data/game-recordings/GameX/output/GameX_goals_music_video_vm004.mp4', codec='libx264', audio_codec="aac", fps=30)

    bucket_name = "street-bucket"
    destination_folder = 'game-recordings/GameX/output/'
    local_file_folder = './data/game-recordings/GameX/output/'
    local_file_name = "GameX_goals_music_video_vm004.mp4"
    destination_blob_name = destination_folder + local_file_name
    local_file_path = local_file_folder + local_file_name
    upload_file_to_gcp_bucket(bucket_name, local_file_path, destination_blob_name)

    return None

def main():
    creat_pitch_video()

    pass

if __name__ == "__main__":
    main()
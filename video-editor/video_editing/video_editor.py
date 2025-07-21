'''
Class VideoEditor:

    Methods:
    - __init__(self, video = None)
    Initializes class object from a video file path or VideoFileClip object.


    - merge_videos(self, video_editors)
    Merge a list of VideoEditor objects into one VideoEditor object.

    - get_total_length(self)
    Get the total length of the video in seconds.

    - get_frame_size(self)
    Get the frame size of the video.

    - get_video_clip(self)
    Get the video clip.

    - cut_video_by_timebands(self, timebands)
    Cut the video based on timestamps of interest with offset buffers.

    - save_video(self, output_path, video_clip = None)
    Save the video clip to a file.

'''
import random
import time
import shutil

from moviepy.editor import VideoFileClip, CompositeVideoClip
from moviepy.editor import concatenate_videoclips
from moviepy.editor import vfx

from street.video_editing.file_info_fn import get_video_time_utc, get_utc_timestamp_in_milliseconds
from street.video_editing.file_info_fn import get_location_lat_long
from street.video_editing.file_info_fn import get_timestamp_by_game_code
from street.video_editing.file_info_fn import get_game_info_from_game_code

from street.video_editing.video_effects import crop_and_resize_video_clip
from street.video_editing.video_effects import get_scoreline_watermark
#from street.video_editing.video_effects import get_game_clock_watermark

from street.video_editing.zoom import CropResizeImage
from street.video_editing.zoom import MovingZoom

from street.video_editing.software_camera import SoftwareCam

def add_transition(clip, fade_duration = 0.3):
    # Clip transitions
    print('Adding transitions to clips')
    transition_choice = 1#random.choice([0,1])
    if transition_choice == 0:
        clip = clip.crossfadein(fade_duration)
        clip = clip.crossfadeout(fade_duration)
    else:
        clip = clip.fadein(fade_duration)
        clip = clip.fadeout(fade_duration)
    return clip

def sort_clips_by_timestamps(clips, timestamps, descriptions):
    """
    Sorts the clips and timestamps lists based on ascending order of timestamps.

    Parameters:
    - clips (list): A list of video clips.
    - timestamps (list): A list of timestamps in milliseconds corresponding to each clip.
    - descriptions (list): A list of descriptions corresponding to each clip.

    Returns:
    - tuple: A tuple containing the sorted clips, sorted timestamps, and sorted descriptions.
    """
    # Combine the clips and timestamps into a list of tuples
    combined = list(zip(timestamps, clips, descriptions))

    print('\n\nTIMESTAMPS')
    print(timestamps)

    # Sort the combined list based on the timestamps
    combined.sort(key=lambda x: x[0])

    # Unzip the sorted list back into separate lists
    sorted_timestamps, sorted_clips, sorted_descriptions = zip(*combined)

    # Convert back to lists (zip returns tuples)
    sorted_ts = list(sorted_timestamps)
    sorted_cs = list(sorted_clips)
    sorted_ds = list(sorted_descriptions)

    return sorted_cs, sorted_ts, sorted_ds


class VideoEditor:
    def __init__(self, video = None):
        if video is not None:
            if isinstance(video, str):              # If video is a file path
                print('\n\nLOADING VIDEO FILE INTO VIDEO EDITOR')
                self.video = VideoFileClip(video)# , fps_source='tbr')

                print('\n\nVideo Size',self.video.size)
                print('Type',type(self.video))
                print('...Resizing...')
                self.video = self.video.resize((1920, 1080))
                print('After Resizing\nVideo Size',self.video.size)
                print('Type',type(self.video))

                # Get game info
                self.game_info = get_game_info_from_game_code(video)
                
                # Get UTC timestamp (in milliseconds) of the video creation time
                utc_time_ms = get_timestamp_by_game_code(video)
                if utc_time_ms is None:
                    print('No UTC timestamp found for the game code.')
                    utc_time = get_video_time_utc(video)
                    utc_time_ms = get_utc_timestamp_in_milliseconds(utc_time)
                    print('Video creation timestamp (UTC):', utc_time)
                self.creation_timestamp = utc_time_ms
                print('File name: ', video)
                print('Video creation timestamp (ms):', utc_time_ms)
                # Get the latitude and longitude of the video
                self.latitude, self.longitude = get_location_lat_long(video)

            else:                                   # If video is a VideoFileClip object
                self.video = video
                
                # Set the creation timestamp and location to None
                self.creation_timestamp = 0
                self.latitude = None
                self.longitude = None
                self.game_info = None

            self.fps = self.video.fps
            print('VIDEO LOADED INTO VIDEO EDITOR')
        else:

            self.video = None
            self.fps = None

            print('\n\n=============NO VIDEO LOADED=============\n\n')

    def merge_videos(self, video_clips_with_timestamps, use_timestamps = True):
        """
        Merge a list of VideoEditor objects into one VideoEditor object.
        
        Args:
        - video_editors: List of VideoEditor objects to be merged.
        
        Returns:
        - A new VideoEditor object containing the merged video.
        """
        # Extract the video clips from each VideoEditor object
        clips = [ve[0] for ve in video_clips_with_timestamps]
        timestamps = [ve[1] for ve in video_clips_with_timestamps]
        descriptions = [ve[2] for ve in video_clips_with_timestamps]

        if not clips:
            print("\n\n====================No valid videos to merge.====================\n\n")
            return None  # Return an empty VideoEditor object if no valid videos
    
        # Sort the clips and timestamps based on the timestamps
        if use_timestamps:
            clips_sorted, ts_sorted, ds_sorted = sort_clips_by_timestamps(clips, timestamps, descriptions)
            #clips_sorted, ts_sorted, ds_sorted = clips, timestamps, descriptions

            # Get timestamps in seconds, starting with the first one set to 0
            timestamp_for_game_clock = [(ts)/1000 for ts in ts_sorted]#[(ts - ts_sorted[0])/1000 for ts in ts_sorted]
            
            final_clips = []
            i = 0
            for clip, game_time_in_s, description in zip(clips_sorted, timestamp_for_game_clock, ds_sorted):

                # Add Game clock watermark to the video
                # game_time_min = int(game_time_in_s // 60)
                # game_time_sec = int(game_time_in_s % 60)

                #game_clock_watermark = get_game_clock_watermark(game_time_min, game_time_sec, clip.duration)
                # Add watermark to the video
                # Set the watermark position and duration
                #watermark = game_clock_watermark.set_position(('left', 'top')).set_duration(clip.duration)
                # Check description to change score

                # 'left' in description means - the goal is on the left of the frame
                # This means the team playing from the right side of the field scores there
                if 'left' in description.lower():
                    self.game_info['right_score'] += 1

                # 'right' in description means - the goal is on the right of the frame
                # This means the team playing from the left side of the field scores there
                if 'right' in description.lower():
                    self.game_info['left_score'] += 1

                
                # Score is changed at the beginning of the clip
                scoreline_watermark = None
                print('Left:',self.game_info['left_team'],'\nRight:', self.game_info['right_team'])
                if self.game_info['left_team'] is not None and self.game_info['right_team'] is not None:
                    print('\n==GETTING IN HERE==\n')
                    # Add scoreline and other info to the video
                    scoreline_watermark = get_scoreline_watermark(self.game_info, clip.duration)

                    # Add watermark to the video
                    # Set the watermark position and duration
                    scoreline_watermark  = scoreline_watermark.set_position(('left', 'top')).set_duration(clip.duration)
                    #scoreline_watermark.write_videofile('scoreline_2.mp4', codec='libx264', fps=24)
                    
                # Overlay the watermark on the video
                if scoreline_watermark is not None:
                    print('\n==ADDING WATERMARK==\n')
                    clip = CompositeVideoClip([clip, scoreline_watermark])
                
                # Write clip to file with game_time_in_s as the file name
                tfname = str(game_time_in_s).split('.')[0]
                print('Game time (Not added anywhere at the moment:)',tfname)
                #clip.write_videofile(f'./data/game-recordings/Game64_1028/output/'+tfname+'.mp4', codec='libx264', audio_codec='aac')
                
                # For .m2ts
                '''
                clip = clip.set_fps(50)
                clip = clip.fx(vfx.speedx, factor=0.5)
                clip = clip.subclip(0,int(0.5*clip.duration))
                '''

                clip = add_transition(clip)
                
                # Print clip size
                print('Clip size:', clip.size)

                final_clips.append(clip)

                '''
                print('i:',i)
                print('game_time_in_s:',game_time_in_s)
                if i > 0:
                    print('i in the if:',i)
                    clip.audio.write_audiofile('./test_and_delete/test_audio_'+str(i)+'.mp3')
                clip.write_videofile('./test_and_delete/test_video_'+str(i)+'.mp4')
                i += 1
                x = 5 + 's'
                #'''



        else:
            final_clips = [add_transition(clip) for clip in clips]
        
        # Return a new VideoEditor object with the merged video
        return VideoEditor(concatenate_videoclips(final_clips))
    
    
    def get_game_info(self, game_code):
        """
        Get the game information from the game code.
        """
        self.game_info = get_game_info_from_game_code(game_code)
        return None
    
    def get_total_length(self):
        """
        Get the total length of the video in seconds.
        """
        return self.video.duration

    def get_frame_size(self):
        """
        Get the frame size of the video.
        """
        return self.video.size

    def get_video_clip(self):
        """
        Get the video clip.
        """
        return self.video

    def get_video_creation_timestamp(self):
        """
        Get the creation timestamp of the video.
        """
        return self.creation_timestamp
    
    def get_video_location(self):
        """
        Get the latitude and longitude of the video.
        """
        return self.latitude, self.longitude
    
    def add_moving_zoom_to_video(self, video_clip, ball_path = None):
        """
        Add zoom and slow motion effects to the video
        """
        end_time = video_clip.duration
        original_width, original_height = video_clip.size
        
        #mod_video_clip = video_clip.fl_image(CropResizeImage(480, 480))
        
        if ball_path is None:

            ball_path = [{'timestamp': 0, 'x': 0, 'y': 0},
                        { 'timestamp': end_time*1000, 'x': original_width, 'y': original_height}]
        
        width, height = 400, int((16*400)/9)
        zoom_frame_size = (width, height)
        
        zoomer = MovingZoom(ball_path, zoom_frame_size)

        start = time.time()
        mod_video_clip = zoomer(video_clip)
        print('Time taken to apply zoom effect:', round(time.time() - start), 'seconds')

        return mod_video_clip
    
    def add_software_camera(self, video_clip):
        """
        Add software camera to the video
        """
        video_clip_path = './test_and_delete/software_cam_clip.mp4'

        video_clip.write_videofile(video_clip_path)
        print('Video clip for software camera saved to:', video_clip_path)

        software_cam = SoftwareCam()
        # Add camera effects to the video clip
        start = time.time()
        video_clip_with_effects = software_cam.add_camera_effects(video_clip_path)
        print(f"Time taken to add software camera effects: {round(time.time() - start):.2f} seconds")

        return video_clip_with_effects
    
    def add_replay(self, video_clip):
        """
        Create replay with the video
        """
        video_clip_path = './test_and_delete/replay_clip.mp4'

        video_clip.write_videofile(video_clip_path)
        print('Video clip for software camera saved to:', video_clip_path)

        software_cam = SoftwareCam()
        # Add camera effects to the video clip
        start = time.time()
        video_clip_with_effects = software_cam.create_replay(video_clip_path)
        print(f"Time taken to add software camera effects: {round(time.time() - start):.2f} seconds")

        #video = video_clip_with_effects
        #video.write_videofile('./test_and_delete/clip_check.mp4')
        #user_input = input('CLIP WITH EFFECTS IN VE: Check clip and press enter to continue: ')
        # Normal video with sound - no extra in write file


        return video_clip_with_effects
    
    def write_ripley_data_to_files(self):
        # Add Ripley reel to a dataset and reel collection
        game_info = self.game_info
        game_code = game_info['game_code']

        # Find the next available ripley file number
        i = 0
        file_found = True
        while file_found:
            if not os.path.isfile('./data/reel_clips/'+ game_code +'/ripley_' + str(i) + '.mp4'):
                file_found = False
                break
            else:
                i += 1
        reel_number = i
        
        ripley_clip_path = './test_and_delete/temp_game_files/ig_output_'+str(reel_number)+'.mp4'

        # Write ripley reel to reel collection
        reel_path_name = './data/reel_clips/'+ game_code +'/ripley_' + str(reel_number) + '.mp4'
        # Copy the ripley clip to the dataset
        shutil.copy(ripley_clip_path, reel_path_name)

        # Creating ripley dataset

        # Folder for ripley reel dataset
        ripley_reel_dataset_folder = './data/ripley_dataset/' + game_code + '/'

        # Write ripley reel to a file in the dataset
        ripley_reel_dataset_folder_path = ripley_reel_dataset_folder + 'ripley_' + str(reel_number) + '.mp4'
        shutil.copy(ripley_clip_path, ripley_reel_dataset_folder_path)

        # Write original_clip to file
        #original_clip = VideoFileClip('./test_and_delete/replay_clip.mp4')
        original_clip_initial_path = './test_and_delete/replay_clip.mp4'
        original_clip_copy_path = ripley_reel_dataset_folder + 'original_clip_'+str(reel_number)+'.mp4'
        shutil.copy(original_clip_initial_path, original_clip_copy_path)

        # Write all_people_tracks.mp4 to file
        all_people_tracks_initial_path = './test_and_delete/all_people_tracks.mp4'
        all_people_tracks_copy_path = ripley_reel_dataset_folder + 'clip_with_tracks_'+str(reel_number)+'.mp4'
        shutil.copy(all_people_tracks_initial_path, all_people_tracks_copy_path)

        # Read people_track_timeline_string from file
        people_track_timeline_file_path = './test_and_delete/temp_game_files/people_track_timeline_'+str(reel_number)+'.txt'
        people_track_timeline_copy_path = ripley_reel_dataset_folder + 'people_track_timeline_'+str(reel_number)+'.txt'
        shutil.copy(people_track_timeline_file_path, people_track_timeline_copy_path)
        
        
        # Copy track_boxes.json to file
        track_boxes_file_path = './test_and_delete/temp_game_files/track_boxes_'+str(reel_number)+'.pkl'
        track_boxes_copy_path = ripley_reel_dataset_folder + 'track_boxes_'+str(reel_number)+'.pkl'
        shutil.copy(track_boxes_file_path, track_boxes_copy_path)
        
        return None
    
    def add_camera_effects_to_single_clip(self, clip, camera_view_name = None):
        
        clip_before_camera_effects = clip
        clip_with_camera_effects = None
        clip_with_software_cam = None

        if camera_view_name == 'software_cam':
            # Add moving software camera here
            clip_with_software_cam = self.add_software_camera(clip)
            print('SOFTWARE CAM ADDED')


        if camera_view_name == 'ripley': # Replay + Ripoff of clippy
            # Add moving software camera here
            accept = False
            while accept is not True:
                
                clip_with_software_cam = self.add_replay(clip_before_camera_effects)
                if clip_with_software_cam is None:
                    accept = True
                    break

                print('Watch the replay and decide if you want to keep it')
                accept_string = input('Do you want to keep the replay? (y/any key to re create): ')

                if accept_string == 'y' or accept_string == 'Y' or accept_string == 'yes' or accept_string == 'Yes':
                    accept = True
                    print('Entered acceptance - Writing files',accept)

                    if clip_with_software_cam is not None:
                        self.write_ripley_data_to_files()
                else:
                    # Remove latest replay files
                    # Find the latest ripley file number
                    i = 0
                    file_found = True
                    while file_found:
                        if not os.path.isfile('./test_and_delete/temp_game_files/replay_output_' + str(i) + '.mp4'):
                            file_found = False
                            i -= 1
                            break
                        else:
                            i += 1
                    if i > -1:
                        if clip_with_software_cam is not None:
                            print('LATEST REPLAY REMOVED')
                            os.remove('./test_and_delete/temp_game_files/replay_output_'+str(i)+'.mp4')
                            os.remove('./test_and_delete/temp_game_files/ig_output_'+str(i)+'.mp4')
                            os.remove('./test_and_delete/temp_game_files/people_track_timeline_'+str(i)+'.txt')
                            os.remove('./test_and_delete/all_people_tracks.mp4')
                            os.remove('./test_and_delete/temp_game_files/track_boxes_'+str(i)+'.pkl')
                            print('REPLAY REMOVED')
                    
                    # Ripley reel written to reel collection and dataset after acceptance
            # While loop done
            #print('RIPLEY ADDED AND WRITTEN TO FILE - WHILE LOOP DONE')

        # IF Ripley done
        
        if clip_with_software_cam is not None:
            clip_with_camera_effects = clip_with_software_cam
        else:
            clip_with_camera_effects = crop_and_resize_video_clip(clip, camera_view_name)
            print('CROP AND RESIZE DONE')
            '''
            clip_with_camera_effects.audio.write_audiofile('./test_and_delete/temp_game_files/test_audio_after_crop_and_resize_temp.mp3')
            clip_with_camera_effects.write_videofile('./test_and_delete/temp_game_files/test_video_after_crop_and_resize_temp.mp4')
            x = 5 + 's'
            # '''

        '''
        print('CLIP RETURNING FROM ADD CAMERA EFFECTS')

        print('TYPE OF CLIP WITH CAMERA EFFECTS:',type(clip_with_camera_effects))
        print('TYPE OF CONCATENATE VIDEO CLIPS:',type(concatenate_videoclips([clip_with_camera_effects])))
        #'''
            
        return concatenate_videoclips([clip_with_camera_effects])

    
    def cut_video_by_timebands(self, timebands_and_info):
        """
        Cut the video based on timestamps of interest with offset buffers.
        Args:
        - timebands: List of [start, end] timebands to cut the video
        Note: start, end are in seconds
        """

        timebands = timebands_and_info['timebands']
        descriptions = timebands_and_info['descriptions']
        camera_views = timebands_and_info['camera_views']

        clips = []
        creation_timestamp = self.get_video_creation_timestamp()

        clips_with_timestamps = []

        for (start_time, end_time), camera_view_name, description in zip(timebands, camera_views, descriptions):
            
            # clip = self.cut_video_by_timestamp(start_time, end_time) DEPRECATED: Code was for VideoFrames objects
            clip            = self.video.subclip(start_time, end_time)
            clip_timestamp  = creation_timestamp + start_time*1000 # Convert seconds to milliseconds

            '''
            print('clip_timestamp:',clip_timestamp)
            print('start_time:',start_time)
            print('end_time:',end_time)
            clip.write_videofile('./test_and_delete/temp_game_files/test_video_before_camera_effects_'+str(int(clip_timestamp))+'.mp4')
            clip.audio.write_audiofile('./test_and_delete/temp_game_files/test_audio_'+str(int(clip_timestamp))+'.mp3')
            '''

            clip = self.add_camera_effects_to_single_clip(clip, camera_view_name)

            '''
            print('CLIP AFTER CAMERA EFFECTS LINE 509')

            clip.write_videofile('./test_and_delete/temp_game_files/test_video_after_camera_effects_'+str(int(clip_timestamp))+'.mp4')
            clip.audio.write_audiofile('./test_and_delete/temp_game_files/test_audio_after_camera_effects_'+str(int(clip_timestamp))+'.mp3')
            '''

            # Good place to add the game clock watermark - Code below has starter code

            '''
            if self.game_info['left_team'] is not None and self.game_info['right_team'] is not None:
                # Add scoreline and other info to the video
                scoreline_watermark = get_scoreline_watermark(self.game_info, clip.duration)

                # Add watermark to the video
                # Set the watermark position and duration
                watermark = scoreline_watermark.set_position(('center', 'bottom')).set_duration(clip.duration)

                # Overlay the watermark on the video
                clip = CompositeVideoClip([clip, watermark])

                # Check description to change score

                # 'left' in description means - the goal is on the left of the frame
                # This means the team playing from the right side of the field scores there
                if 'left' in description.lower():
                    self.game_info['right_score'] += 1

                # 'right' in description means - the goal is on the right of the frame
                # This means the team playing from the left side of the field scores there
                if 'right' in description.lower():
                    self.game_info['left_score'] += 1
            #'''

            clips.append(clip)
            clips_with_timestamps.append((clip, clip_timestamp, description))

            #video = clip
            #video.write_videofile('./test_and_delete/clip_check.mp4')
            #user_input = input('CLIP in CUT BY TIMEBANDS AFTER EFFECTS ADDED: Check clip and press enter to continue: ')
            # Normal video with sound with no extra stuff in video write file

            #print('CLIP IN LOOP DONE, MOVING TO NEXT')
        # End for loop
        
        if len(clips) == 0:
            print("\n\n====================No clips to concatenate.====================\n\n")
            return None
        else:
            # return VideoEditor(concatenate_videoclips(clips)) DEPRECATED: Returning VideoFileClips now as seen in line below
            return clips_with_timestamps 

    def save_video(self, output_path, video_clip = None):
        """
        Save the video clip to a file.
        """
        if video_clip is None:
            video_clip = self.video
        video_clip.write_videofile(output_path)





import os

def main():
    '''
    print('Current working directory:', os.getcwd())
    
    # Usage example
    file_path = './data/game-recordings/Game12_0918/Game12_0918_p1.mp4'
    lat, long = get_location_lat_long(file_path)
    print('Latitude:', lat)
    print('Longitude:', long)

    print('\n\n')
    file_path = './data/game-recordings/Game12_0918/Game12_0918_p2.mp4'
    lat, long = get_location_lat_long(file_path)
    print('Latitude:', lat)
    print('Longitude:', long)

    # '''
    pass

if __name__ == "__main__":
    main()
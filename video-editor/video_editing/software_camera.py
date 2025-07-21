'''
Class that contains the software camera functionality

Goal: Make static camera footage exciting by adding camera movement and dynamic effects

'''
import time, os, json, pickle
from moviepy.editor import VideoFileClip

# Import MovingZoom from zoom.py
from street.video_editing.zoom import MovingZoom
from street.video_editing.ball_tracking import track_ball_in_clip

from street.video_editing.people_tracking import track_people_in_clip, track_multiple_people_in_clip

from street.video_editing.watermark import add_watermark

def get_ball_path_from_ball_tracking(video_clip):
    '''
    Get the ball path from ball tracking

    Args:
        video_clip: Video file to get the ball path from

    Returns:
        ball_path: Path of the ball as a list of dictionaries with timestamp, x and y coordinates
        ball_path = [{'timestamp': 0, 'x': 0, 'y': 0},
                    {'timestamp': 1000, 'x': 100, 'y': 100}]
    '''

    # Get the ball path from ball tracking
    print("Getting ball path from ball tracking...")
    ball_path = track_ball_in_clip(video_clip)

    return ball_path

class SoftwareCam():

    def __init__(self):
        pass

    def path_following_cam(self, video_path = './test_and_delete/cut_clip.mp4'):
            
            '''
            Add ball following camera effect to the video clip
    
            Args:
                video_clip: Video file to add ball following camera effect to
    
            Returns:
                Video file with ball following camera effect
            '''
    
            # Add ball following camera effect to the video clip
            print("Adding people following camera effect...")

            # Get the ball path from ball tracking
            # Not fully automated at the moment - ball_tracking.py has code that requires manual intervention on runtime
            # ball_path = get_ball_path_from_ball_tracking(video_path) # This function is a wrapped implemented above

            # Get the ball path from people tracking
            # People path x, y coordinates are normalized to the frame size
            people_path = track_people_in_clip(video_path)

            camera_path = people_path

            reel_info = None

            video_clip_with_moving_camera = None

            print('\n\n\n===========CAMERA PATH READY===========\n\n')
            #print(camera_path)
            #print('\n\n\n')

            if camera_path is not None: # No path was selected by the user (i.e. no person track was selected)

                clip_for_reference = VideoFileClip(video_path)
                clip_audio = clip_for_reference.audio
                # Select frame size
                zoom_factor = 0.66
                original_frame_width = clip_for_reference.size[0]
                original_frame_height = clip_for_reference.size[1]

                frame_size = (original_frame_width * zoom_factor, 
                              original_frame_height * zoom_factor)

                # Create a MovingZoom object and initialize ball path and frame size
                moving_camera = MovingZoom(camera_path, frame_size)

                video_clip = VideoFileClip(video_path)
                # Add moving camera effect to the video clip
                video_clip_with_moving_camera = moving_camera(video_clip)

                # Resize the video clip to the original frame size
                video_clip_with_moving_camera = video_clip_with_moving_camera.resize((original_frame_width, original_frame_height))

                # Add audio to the video clip
                video_clip_with_moving_camera = video_clip_with_moving_camera.set_audio(clip_audio)

                # create_reels(video_clip, camera_path)
                reel_info = (clip_for_reference, camera_path)
                # Write reel info to temporary file

                i = 0
                file_found = True
                while file_found:
                    if not os.path.isfile('./test_and_delete/reel_info/ref_clip_' + str(i) + '.mp4'):
                        file_found = False
                        break
                    else:
                        i += 1
                
                # Write clip_for_reference to temporary file
                clip_for_reference.write_videofile('./test_and_delete/reel_info/ref_clip_'+str(i)+'.mp4')
                
                with open('./test_and_delete/reel_info/ball_path_'+str(i)+'.json', 'w') as file:
                    json.dump(camera_path, file)

                video_clip_with_moving_camera.write_videofile('./test_and_delete/reel_info/reel_clip_'+str(i)+'.mp4')
                
                video_clip_from_file = VideoFileClip('./test_and_delete/reel_info/reel_clip_'+str(i)+'.mp4')
                video_clip_with_moving_camera = video_clip_from_file

            else:
                video_clip_with_moving_camera =  None

            return video_clip_with_moving_camera

    def add_camera_effects(self, video_clip_path, output_file = './test_and_delete/software_cam_output.mp4'):

        '''
        Add camera effects to the video clip

        Currently available camera effects:
        - Path following camera effect

        Args:
            video_clip: Video file to add camera effects to
            effects: List of camera effects to add
            output_file: Output file path to save the video with effects

        Returns:
            Video file with camera effects
        '''

        # Add camera effects to the video clip
        print(f"Adding camera effects to {video_clip_path}...")

        print("Adding ball following camera effect...")
        video_clip = self.path_following_cam(video_clip_path)

        return video_clip
    
    def apply_replay_effects(self, video_clip_path):
        '''
        Apply Ripley effects to the video clip

        Args:
            video_clip: Video file to apply Ripley effects to

        Returns:
            Video file with Ripley effects
        '''

        # Apply Ripley effects to the video clip
        print(f"Applying Replay effects to {video_clip_path}...")

        # Add camera effects to the video clip

        '''
        First get the people paths

        Write the video with bboxes

        Input [bbox_name, start, end; bbox_name, start, end; ...]

        Implement dynamic replay_cam with multiple bounding boxes captured
        - Create timeline of chosen bounding boxes, zooms, and slow mos
        - Implement frame creation for replay_cam with multiple bounding boxes captured
        - Create new video based on replay_cam and reframe to original size

        '''

        # Get the people path from people tracking
        frame_path, max_frame_path, track_boxes = track_multiple_people_in_clip(video_clip_path)

        if frame_path is None and max_frame_path is None and track_boxes is None:
            return None, None
        
        # Frame path is the moving bounding box around the multiple persons detected
        # Max frame path is the maximmum static bounding box around the multiple persons detected
        
        # People path timeline string is string in the format "[start_time, [p1, p2, ...], time, [p1, p2, ...], end_time]"
        
        video_clip_with_replay_camera =  None
        #frame_path = max_frame_path
        if frame_path is not None:

            clip_for_reference = VideoFileClip(video_clip_path)
            clip_audio = clip_for_reference.audio

            replay_camera = MovingZoom(frame_path)

            video_clip = VideoFileClip(video_clip_path)

            # Add moving camera effect to the video clip
            video_clip_with_replay_camera = replay_camera(video_clip)


            # Add audio to the video clip
            video_clip_with_replay_camera   = video_clip_with_replay_camera.set_audio(clip_audio)


        '''
        Next replay cam effects
        Input [zoom, start, end; zoom, start, end; ...]
        Implement zoom

        Input [slow_mo, start, end; slow_mo, start, end; ...]
        Implement slow_mo
        '''
        
        return video_clip_with_replay_camera, track_boxes
    
    def create_replay(self, video_clip_path):
        '''
        Create a Ripley reel from the video clip

        Args:
            video_clip: Video file to create a Ripley reel from
            output_file: Output file path to save the Ripley reel

        Returns:
            Replay clip
        '''
        # Create a replay reel from the video clip
        print(f"Creating Replay from {video_clip_path}...")
        output_file = ''

        # Add camera effects to the video clip
        video_clip, track_boxes = self.apply_replay_effects(video_clip_path)

        if video_clip is None and track_boxes is None:
            return None

        # Save the Ripley clip
        if video_clip:
            # Find the next available ripley file number
            i = 0
            file_found = True
            while file_found:
                if not os.path.isfile('./test_and_delete/temp_game_files/replay_output_' + str(i) + '.mp4'):
                    file_found = False
                    break
                else:
                    i += 1
            
            clip_number = i
            
            output_file = './test_and_delete/temp_game_files/replay_output_' + str(clip_number) + '.mp4'
            if output_file:
                video_clip.write_videofile(output_file)
            
            track_boxes_file = './test_and_delete/temp_game_files/track_boxes_' + str(clip_number) + '.pkl'
            # Write to a binary file

            with open(track_boxes_file, 'wb') as file:
                pickle.dump(track_boxes, file)
            
        return VideoFileClip(output_file)
    
def main():
    # Create a SoftwareCam object
    software_cam = SoftwareCam()

    # Read the video clip
    file_path = './data/game-recordings/Game79_0511/Game79_0511_p1.mp4'
    clip_start = 118*60 + 52
    clip_end = clip_start + 11
    video_clip = VideoFileClip(file_path).subclip(clip_start, clip_end)

    # Write clip to temporary file
    video_clip_path = './test_and_delete/cut_clip.mp4'
    video_clip.write_videofile(video_clip_path)
    
    # Add camera effects to the video clip
    start = time.time()
    #video_clip_with_effects = software_cam.add_camera_effects(video_clip_path)

    # Create a Ripley reel from the video clip
    video_clip_with_replay = software_cam.create_replay(video_clip_path)
    print(f"Time taken: {round(time.time() - start):.2f} seconds")



    return None

if __name__ == "__main__":
    main()
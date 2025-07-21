import ffmpeg
import json

def get_video_details(video_filename, output_json_filename):
    try:
        # Run ffmpeg probe to get video details
        probe = ffmpeg.probe(video_filename)
        
        # Extract video stream details
        video_stream = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
        
        # Extract details
        details = {
            'codec_name': video_stream.get('codec_name'),
            'width': int(video_stream['width']),
            'height': int(video_stream['height']),
            'r_frame_rate': eval(video_stream['r_frame_rate']),  # Frame rate as a float
            'bit_rate': int(video_stream['bit_rate']) if 'bit_rate' in video_stream else None,
            'duration': float(video_stream['duration']) if 'duration' in video_stream else None
        }
        # Write details to JSON file
        with open(output_json_filename, 'w') as json_file:
            json.dump(details, json_file, indent=4)
        
        print(f"Video details written to {output_json_filename}")
        
        return details
    
    except ffmpeg.Error as e:
        print(f"Error: {e}")
        return None

# Example usage

video_filename = "./data/game-recordings/Game6_0831/Game6_0831_p1.mp4"
output_filename = "./data/game-recordings/Game6_0831/Game6_0831_p1_video_details.json"
video_details = get_video_details(video_filename, output_filename)
print('Input video details')
for key, value in video_details.items():
    print(f"{key}: {value}")
print('\n')

video_filename = "./data/game-recordings/Game6_0831/output/Game6_0831_goals_music_video_vm003.mp4"
output_filename = "./data/game-recordings/Game6_0831/output/Game6_0831_goals_music_video_details.json"
video_details = get_video_details(video_filename, output_filename)

print('\n\nOutput video details')
for key, value in video_details.items():
    print(f"{key}: {value}")
print('\n')

video_filename = "./data/game-recordings/Game6_0831/output/clip_1.mp4"
output_filename = "./data/game-recordings/Game6_0831/output/clip_1_video_details.json"
video_details = get_video_details(video_filename, output_filename)

print('\n\nOutput video details')
for key, value in video_details.items():
    print(f"{key}: {value}")
print('\n')

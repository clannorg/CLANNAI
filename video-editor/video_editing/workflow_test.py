from street.data_transfer.get_data_from_gcp_bucket import run_get_game_data_from_gcp_bucket_to_vm
from street.data_transfer.put_data_into_gcp_bucket import run_put_data_into_gcp_bucket_from_vm

from .cut_video import run_cut_video
from .music_effects import run_music_effects

import time
import os

from street.video_editing.video_editor import VideoEditor

def main():

    start = time.time()

    game_code_list = ['Game1_0804', 'Game2_0805', 'Game3_0807', 'Game4_0825', 'Game5_0825']
    game_code = game_code_list[4]

    # To be replaced by checking the max p{n} files in the folder
    number_of_files = 2
    if game_code == 'Game1_0804':
        number_of_files = 3
    if game_code == 'Game5_0825':
        number_of_files = 1
    
    include_logo = False

    # VM folder path details
    vm_game_code_folder_path = './data/game-recordings/'+game_code+'/'
    
    # Music file details
    vm_music_folder_path = './data/music/'
    
    # Select music
    music_file_list = ['Aylex_Building_Dreams.mp3','Beat_Your_Competition.mp3']
    music_file = music_file_list[1]

    # Output file details
    vm_output_path = vm_game_code_folder_path + 'output/'

    # Check if the directory exists, and if not, create it
    if not os.path.exists(vm_output_path):
        os.makedirs(vm_output_path)
        print(f"Directory '{vm_output_path}' created.")
    else:
        print(f"Directory '{vm_output_path}' already exists.")


    video_only_postfix = '_video_only_vm003.mp4'
    music_video_postfix = '_music_video_vm003.mp4'

    # Labels to cut from the timestamp list
    highlight_names = ['goals', 
                       'all']
    highlight_labels = [ ['Goal!'], 
                        None]
    
    # Get the game data from the bucket [GCP bucket ==> VM]
    # run_get_game_data_from_gcp_bucket_to_vm(game_code)


    # Loop through the lists together using zip
    for highlight_name, label_list in zip(highlight_names, highlight_labels):
        print(f"\n\nHighlight Name: {highlight_name}")
        print(f"Highlight Label: {label_list}")

        labels_of_interest = label_list

        output_music_video_path = vm_output_path + \
            game_code + '_' + highlight_name + music_video_postfix  # Highlight with music file name, path above

        # Cut the videos based on timestamps, and returns a list of cut video editor objects
        video_cuts_list = run_cut_video(game_code, number_of_files, vm_game_code_folder_path, labels_of_interest)

        # Merge the videos and write to file
        highlight_video = VideoEditor().merge_videos(video_cuts_list)
        # Add logo at the end and music effects to the final video
        run_music_effects(vm_music_folder_path,  music_file, highlight_video, output_music_video_path, include_logo)

        # Put the final video in the bucket [VM ==> GCP bucket]
        files_to_write_to_gcp = [game_code + '_' + highlight_name + music_video_postfix]

        # Write the output files to the GCP bucket
        for file_to_write in files_to_write_to_gcp:
            run_put_data_into_gcp_bucket_from_vm(game_code, file_to_write)

    print('Total time taken:', round((time.time()-start)/60,1), 'minutes')
    return None

if __name__ == "__main__":
    main()


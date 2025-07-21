from street.data_transfer.get_data_from_gcp_bucket import run_get_game_data_from_gcp_bucket_to_vm
from street.data_transfer.put_data_into_gcp_bucket import run_put_data_into_gcp_bucket_from_vm

from street.data_transfer.get_data_from_gcp_bucket import download_single_file_from_gcp_bucket

from street.video_editing.create_reel_workflow import make_reels
from street.video_editing.create_reel_workflow import put_reels_into_gcp_bucket
from street.video_editing.create_reel_workflow import put_ripley_dataset_into_gcp_bucket
from street.video_editing.create_reel_workflow import create_goal_highlight_reels


from .cut_video import run_cut_video
from .music_effects import run_music_effects

import time
import os, glob

from street.video_editing.video_editor import VideoEditor

# Folder checks
def create_folder_if_not_exist(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Directory '{folder_path}' created.")
    else:
        print(f"Directory '{folder_path}' already exists.")
    return None

def clear_folder(folder_path):
    for f in glob.glob(folder_path + '*'):
        os.remove(f)
    print(f'Cleared the folder {folder_path}')
    return None
    

def main():

    start = time.time()

    game_code_list = ['Game1_0804', # Bangalore Play 365 FPS 60
                      'Game2_0805', 'Game3_0807', # Bangalore Play 365
                      'Game4_0825', # Bangalore Play 365
                      'Game5_0825', # Germany
                      'Game6_0831', # Bangalore Rush Arena
                      'Game7_0901', # Bangalore Trafford Arena
                      'Game8_0803', # Germany
                      'Game9_0911', # Stanford IM South
                      'Game10_0913',    # Bnagalore Tiger Arena
                      'Game11_0913',    # Stanford IM South
                      'Game12_0918',    # Bangalore Play 365
                      'Game13_0919',    # TSV Konigsbrunn vs (Großaitingen?) - Drone
                      'Game14_0919',    # TSV Konigsbrunn vs (?) - Drone
                      'Game15_0918',    # Stanford IM South
                      'Game16_0916',    # Spain
                      'Game17_0921',    # Bangalore Play 365
                      'Game18_0920',    # Stanford IM South
                      'Game19_0925',    # Bangalore Play 365
                      'Game20_1001',    # Bangalore Kick n Flick
                      'Game21_0921',    # TSV Konigsbrunn vs Harluch - Drone
                      'Game22_1003',    # Bangalore Tiger Arena
                      'Game23_1004',    # Bangalore Trafford Arena

                      # Aufside Tourament 9 games
                      'Game24_1006',    # 3 files
                      'Game25_1006',    # 3 files
                      'Game26_1006',    # 2 files
                      'Game27_1006',    # 2 files
                      'Game28_1006',    # 3 files
                      'Game29_1006',    # 2 files
                      'Game30_1006',    # 3 files
                      'Game31_1006',    # 2 files
                      'Game32_1006',    # 2 files

                      'Game33_0929',    # TSV Konigsbrunn vs Kaufering - Drone

                      # Aufside Tourament 9 games
                      'Game34_1013',    # 2 files
                      'Game35_1013',    # 2 files
                      'Game36_1013',    # 2 files
                      'Game37_1013',    # 2 files
                      'Game38_1013',    # 2 files
                      'Game39_1013',    # 2 files
                      'Game40_1013',    # 2 files
                      'Game41_1013',    # 2 files
                      'Game42_1013',    # 2 files

                      # Rabona Final
                      'Game43_1019',    # 2 files

                      # Aufside Tourament 9 games
                      'Game44_1020',    # 7 files
                      'Game45_1020',
                      'Game46_1020',
                      'Game47_1020',
                      'Game48_1020',
                      'Game49_1020',
                      'Game50_1020',
                      'Game51_1020',
                      'Game52_1020',     # 7 files
                      
                      'Game53_0921',     # TAL - Mu Sigma vs Decathlon

                      # Aufside Tourament 9 games
                      'Game54_1027',
                      'Game55_1027',
                      'Game56_1027',
                      'Game57_1027',
                      'Game58_1027',
                      'Game59_1027',
                      'Game60_1027',
                      'Game61_1027',
                      'Game62_1027',

                      'Game63_1028',     # Stanford Fair Oaks
                      'Game64_1028',     # Boyfun FC Atlanta 
                      'Game65_1030',     # Bangalore Play 365
                      'Game66_1104',     # Boyfun FC Atlanta
                      'Game67_1109',     # Bangalore Play 365
                      'Game68_1113',     # Bangalore Play 365
                      'Game69_1111',     # Boyfun FC Atlanta
                      'Game70_1117',     # Bangalore Play 365
                      'Game71_1118',     # Boyfun FC Atlanta
                      'Game72_1130',     # Williams Soccer Academy
                      'Game73_1124',     # Williams Soccer Academy
                      'Game74_1205',     # Williams Soccer Academy
                      'Game75_1109',     # Williams Soccer Academy
                      'Game76_1205',     # Williams Soccer Academy

                      'Game77_1209',     # Stanford Mayfield - Shahab Testimonial

                      # 2025
                      'Game78_0601',     # Dynamic Futbol Academy - Tampa, FL (vs Shock City)

                      'Game79_0511',     # DFA vs Nacional FC May 11
                      'Game80_0518',     # DFA vs Clearwater Chargers May 18
                      'Game81_0207',     # DFA vs Tampa Strikers Feb 7

                      'Game82_0327',     # DFA vs Marlex International

                      'Game83_0115',     # Play 365 Bangalore

                      'Game84_0113',     # Real BLR FC - Super Division - M7

                      'Game85_0115',     # Pune PL - Championship Match day 7 1 game
                      'Game86_0115',     # Pune PL - Championship Match day 7 Full 5 games

                      'Game90_0116',     # Pune PL - Championship Match day 8 Full 5 games
                      'Game95_0117',     # Pune PL - Match day 9 Full 5 games - Done

                      'Game100_0127',    # Boyfun FC Atlanta 0-0 - Done

                      'Game101_0121',    # Pune PL - Match day 10 Full 5 games

                      'Game106_0327',    # DFA vs Royal Palm SC

                      'Game107_0203',    # Boyfun FC Atlanta 3-3 - Done

                      'Game108_0204',    # DFA vs Orlando Rovers - Done
                      'Game109_0205',    # DFA vs Atheltico Orlando
                      'Game110_0206',    # DFA vs Nona FC

                      'Game111_1217',    # PPL - Match day #2 - 5 games 
                      'Game116_1223',    # PPL - Match day #3 - 4 games
                      'Game120_1230',    # PPL - Match day #4 - 5 games
                      'Game125_0106',    # PPL - Match day #5 - 5 games

                      'Game130_0210',    # Boyfun FC Atlanta vs KTown FC

                      'Game131_0107',    # PPL - Match day #6 - 4 games
                      'Game135_0113',    # PPL - Match day #7 - 5 games
                      'Game140_0114',    # PPL - Match day #8 - 5 games

                      'Game145_0127',   # PPL - Match day #11 - 5 games
                      'Game150_0128',   # PPL - Match day #12 - 4 games
                      'Game154_0203',   # PPL - Match day #13 - 4 games
                      'Game158_0204',   # PPL - Match day #14 - 5 games

                      'Game163_0214',   # URBANRISE | SUPER DIVISION LEAGUE 2024 - 25 | PARIKRMA FC VS SOUTH UNITED FC | 14.02.2025
                      'Game164_0212',   # URBANRISE | SUPER DIVISION LEAGUE 2024 - 25 | REAL CHIKKAMAGALURU FC VS KICKSTART FC | 12.02.2025

                      'Game165_0210',   # PPL - Match day #15 - 4 games
                      'Game169_0211',   # PPL - Match day #16 - 4 games - Possibly corrupt mp4 file (audio problems)
                      'Game173_0217',   # PPL - Match day #17 - 5 games
                      'Game178_0218',   # PPL - Match day #18 - 5 games

                      'Game183_0211',   # URBANRISE | SUPER DIVISION LEAGUE 2024 - 25 | SOUTH UNITED FC VS ASC & CENTER FC | 11.02.2025
                      'Game184_0211',   # URBANRISE | SUPER DIVISION LEAGUE 2024 - 25 | ROOTS FC VS REBELS FC | 11.02.2025
                      'Game185_0210',   # URBANRISE | SUPER DIVISION LEAGUE 2024 - 25 | BENGALURU FC VS FC AGNIPUTHRA | 10.02.2025
                      'Game186_0210',   # URBANRISE | SUPER DIVISION LEAGUE 2024 - 25 | HAL FC VS SPORTING CLUB BENGALURU | 10.02.2025
                      'Game187_0207',    # URBANRISE   SUPER DIVISION LEAGUE 2024 - 25   BANGALORE UNITED FC VS KODAGU FC   07.02.2025
                      'Game188_0207',    # URBANRISE   SUPER DIVISION LEAGUE 2024 - 25   FC REAL BENGALURU VS ASC & CENTER FC   07.02.2025

                      'Game189_0223',    # Peachtree FC vs KWG FC
                      'Game190_0223',    # Peachtree FC vs Leopard FC

                      'Game191_0219',    # Play 365 Bangalore

                      'Game192_0224'    # Boyfun FC Atlanta vs AC Atlanta
                      
                      ]
    # Continue reels at index 21 and going to 0
    game_code = game_code_list[-2]
    print(f"\n\nGame Code: {game_code}")

    # Select music
    music_file_list = ['Aylex_Building_Dreams.mp3',
                       'Beat_Your_Competition.mp3',
                       'Lake_Of_The_Honesty.mp3',
                       'Pixel_Pig.mp3',
                       'Earth.mp3',
                       'Neon.mp3',

                       'Read_My_Lips.mp3', # Final

                       'A_Huevo.mp3', # Group 1
                       'Fin_De_La_Noche.mp3', # Group 2
                       'I_Had_A_Feeling.mp3', # SF1
                       'Tasty_Waves.mp3'# SF2
                       ]
    
    
    music_choice = 7
    if game_code == 'Game79_0511':
        music_choice = 7
    if game_code == 'Game80_0518':
        music_choice = 8
    if game_code == 'Game81_0207':
        music_choice = 10
    
    music_file = music_file_list[music_choice]

    intro_clips_list = ['ball_to_cam','ball_to_cam_post',
                        'hello_albert', 
                        'hello_stanford',
                        'trafford_celebration',
                        'bellandur_blast',
                        'reflex_save',
                        'nutmeg_save',
                        'bellandur_winner',
                        'net_ripper',
                        'boyfun_cartwheel',
                        'face_of_vyasa',
                        'real_blr_fc_intro',
                        'boyfun_power']
    
    intro_choice = 1
    intro_clip_name = intro_clips_list[intro_choice]

    reels_on = False
    get_data_from_bucket = True
    include_logo = True
    post_process = True                # True for iOS videos
    multi_cam = True                   # If True, uses UTC timestamps to merge the video clips
                                        # Set True for multi camera timestamp based merging
    
    # Labels to cut from the timestamp list
    goal_highlights = ['goals']
    goal_highlights_labels = [['Goal!','Celebration','Break']]#,'Intro']]
    # [['Goal!', 'Dribble', 'Skill']] #[['Goal!']]# [['Goal!', 'Dribble', 'Skill']]

    gk_highlights = ['gk']
    gk_highlights_labels = [['GK']]

    all_highlights = ['all']
    all_highlights_labels = [None]

    highlight_names = all_highlights #goal_highlights
    highlight_labels = all_highlights_labels #goal_highlights_labels

    '''
    highlight_names = goal_highlights
    highlight_labels = goal_highlights_labels # '''
    make_goal_reels = False 
    if make_goal_reels:
        reels_on = True



    # VM folder path details
    vm_game_code_folder_path = './data/game-recordings/'+game_code+'/'
    
    # Music file details
    vm_music_folder_path = './data/music/'

    # Reel folder details
    reel_folder_path = './data/reel_clips/' + game_code + '/'
    ripley_dataset_path = './data/ripley_dataset/' + game_code + '/'

    # Output file details
    vm_output_path = vm_game_code_folder_path + 'output/'

    create_folder_if_not_exist(vm_output_path)
    create_folder_if_not_exist(reel_folder_path)
    create_folder_if_not_exist(ripley_dataset_path)

    music_file_path = vm_music_folder_path + music_file

    if not os.path.isfile(music_file_path):
        print(f"Downloading '{music_file}' from GCP bucket.")
        download_single_file_from_gcp_bucket('music/' + music_file, music_file_path)


    music_video_postfix = '_music_video_vm004.mp4'

    # Clear the files in the folder test_and_delete/reel_info before starting anything
    clear_folder('./test_and_delete/reel_info/')
    clear_folder('./test_and_delete/temp_game_files/')
    clear_folder(reel_folder_path)

    # Get the game data from the bucket [GCP bucket ==> VM]
    if get_data_from_bucket:
        run_get_game_data_from_gcp_bucket_to_vm(game_code)
    
    # Find the max p{n} in the game-recordings folder
    i = 1
    file_found = True
    while file_found:
        vid_path = './data/game-recordings/'+ game_code +'/'+ game_code + '_p' + str(i) +'.mp4'
        if not os.path.isfile(vid_path):
            file_found = False
            break
        else:
            i += 1
    number_of_files = i-1

    # Loop through the lists together using zip
    for highlight_name, label_list in zip(highlight_names, highlight_labels):
        print(f"\n\nHighlight Name: {highlight_name}")
        print(f"Highlight Label: {label_list}")

        labels_of_interest = label_list

        output_music_video_path = vm_output_path + \
            game_code + '_' + highlight_name + music_video_postfix  # Highlight with music file name, path above

        # Cut the videos based on timestamps, and returns a list of cut video editor objects
        video_cuts_list = run_cut_video(game_code, number_of_files, vm_game_code_folder_path, labels_of_interest)
        
        if make_goal_reels:
            try:
                create_goal_highlight_reels(game_code)
                print('\n\nGOAL HIGHLIGHT REELS CREATION COMPLETE\n\n')
            except Exception as e:
                print(e)
                print('\n\nGOAL HIGHLIGHT REELS CREATION FAILED\n\n')
                print('Continuing without goal highlight reels')
                

        if reels_on:
            try:
                #make_reels(game_code)
                print('\n\nREEL CREATION COMPLETE\n\n')
            except Exception as e:
                print(e)
                print('\n\nREEL CREATION FAILED\n\n')
                print('Continuing without reels')
                
        
            # Write the output ripley (and other) reels to GCP
            put_reels_into_gcp_bucket(game_code, post_process)
            put_ripley_dataset_into_gcp_bucket(game_code)

        
        # Merge the videos and write to file
        video_merger = VideoEditor()
        video_merger.get_game_info(game_code)
        highlight_video = video_merger.merge_videos(video_cuts_list, multi_cam)

        # Add logo at the end and music effects to the final video
        run_music_effects(vm_music_folder_path,  music_file, 
                          highlight_video, output_music_video_path, 
                          post_process, 
                          include_logo, intro_clip_name)

        # Put the final video in the bucket [VM ==> GCP bucket]
        files_to_write_to_gcp = [game_code + '_' + highlight_name + music_video_postfix]

        # Write the output files to the GCP bucket
        for file_to_write in files_to_write_to_gcp:
            run_put_data_into_gcp_bucket_from_vm(game_code, file_to_write)
    
    print('\n\nHIGHLIGHT CREATION COMPLETE\n\n')
    print('Total time taken:', round((time.time()-start)/60,1), 'minutes')
    
    return None

if __name__ == "__main__":
    main()


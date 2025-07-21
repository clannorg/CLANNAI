from google.cloud import storage
import os
from tqdm import tqdm

from get_data_from_gcp_bucket import download_blobs_in_folder

def download_files_from_gcp_bucket(bucket_name, file_pairs):
    """
    Downloads files from a GCP bucket to local destinations.
    
    Parameters:
    - bucket_name: Name of the GCP bucket.
    - file_pairs: List of tuples where each tuple contains (source_blob_name, destination_file_name).
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    for source_blob_name, destination_file_name in file_pairs:
        blob = bucket.blob(source_blob_name)
        os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)
        
        blob_size = blob.size if blob.size else 0
        with open(destination_file_name, 'wb') as f:
            with tqdm.wrapattr(f, 'write', total=blob_size, miniters=1, desc=source_blob_name) as file_obj:
                blob.download_to_file(file_obj)

def get_reels_from_bucket(game_code):
    bucket_name = "street-bucket"
    folder_name = 'reel_clips/'+game_code+'/'
    local_reels_folder = '../gcp-data/'

    # create local reels folder if it doesnt exist
    os.makedirs(local_reels_folder, exist_ok=True)
    download_blobs_in_folder(bucket_name, folder_name, local_reels_folder)
    return None


if __name__ == "__main__":
    # Example usage
    bucket_name = "street-bucket"

    game_code_list = ['Game1_0804', # Bangalore Play 365 FPS 60
                      'Game2_0805', 'Game3_0807', # Bangalore Play 365
                      'Game4_0825', # Bangalore Play 365
                      'Game5_0825', # Germany
                      'Game6_0831', # Bangalore Rush Arena
                      'Game7_0901', # Bangalore Trafford Arena
                      'Game8_0803', # Germany
                      'Game9_0911', # Stanford IM South
                      'Game10_0913',    # Bangalore Tiger Arena
                      'Game11_0913',    # Stanford IM South
                      'Game12_0918',    # Bangalore Play 365
                      'Game13_0919',    # TSV Konigsbrunn vs (Großaitingen?) - Drone
                      'Game14_0919',    # TSV Konigsbrunn vs (?) - Drone
                      'Game15_0918',    # Stanford IM South
                      'Game16_0916',    # Spain
                      'Game17_0921',    # Bangalore Play 365
                      'Game18_0920',    # Stanford IM South
                      'Game19_0925',    # Bangalore Play 365 - 2 camera
                      'Game20_1001',    # Bangalore Kick n Flick
                      'Game21_0921',    # TS Konigsbrunn vs Harluchs - Drone
                      'Game22_1003',    # Bangalore Tiger Arena
                      'Game23_1004',    # Bangalore Trafford Arena

                      # Aufside Tourament 9 games
                      'Game24_1006',    # 3 files Assassins FC vs Aufside FC
                      'Game25_1006',    # 3 files Assassins FC vs Kreeda FC
                      'Game26_1006',    # 2 files Aufside FC vs Kreeda FC
                      'Game27_1006',    # 2 files Borgadix FC vs Raptors FC
                      'Game28_1006',    # 3 files Borgadix FC vs Pooky Blinders FC
                      'Game29_1006',    # 2 files Raptors FC vs Pooky Blinders FC
                      'Game30_1006',    # 3 files Borgadix FC vs Kreeda FC
                      'Game31_1006',    # 2 files Assassins FC vs Poooky Blinders FC
                      'Game32_1006',    # 2 files Borgadix FC vs Assassins FC

                      'Game33_0929',    # TSV Konigsbrunn vs Kaufering - Drone

                      # Aufside Tourament 9 games
                      'Game34_1013',
                      'Game35_1013',
                      'Game36_1013',
                      'Game37_1013',
                      'Game38_1013',
                      'Game39_1013',
                      'Game40_1013',
                      'Game41_1013',
                      'Game42_1013',

                      # Rabona Tournament
                      'Game43_1019',

                      # Aufside Tourament 9 games
                      'Game44_1020',
                      'Game45_1020',
                      'Game46_1020',
                      'Game47_1020',
                      'Game48_1020',
                      'Game49_1020',
                      'Game50_1020',
                      'Game51_1020',
                      'Game52_1020',

                      'Game53_0921',    # Sports Paddock trial highlight

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

                      'Game63_1028',   # Stanford Fair Oaks
                      'Game64_1028',   # Boyfun FC Atlanta
                      'Game65_1030',     # Play 365 Bangalore - 2 camera

                      'Game66_1104',     # Boyfun FC Atlanta
                      'Game67_1109',     # Play 365 Bangalore - 2 camera
                      'Game68_1113',     # Play 365 Bangalore
                      'Game69_1111',     # Boyfun FC Atlanta
                      'Game70_1117',     # Play 365 Bangalore
                      'Game71_1118',     # Boyfun FC Atlanta
                      'Game72_1130',     # Williams Soccer Academy
                      'Game73_1124',     # Williams Soccer Academy
                      'Game74_1205',     # Williams Soccer Academy
                      'Game75_1109',     # Williams Soccer Academy
                      'Game76_1205',     # Williams Soccer Academy

                      'Game77_1209',     # Stanford Mayfield - Shahab Testimonial

                      # 2025
                      'Game78_0601',     # Dynamic Futbol Academy FL vs Shock City

                      'Game79_0511',     # DFA vs Nacional FC May 11
                      'Game80_0518',     # DFA vs Clearwater Chargers May 18
                      'Game81_0207',     # DFA Strikers vs Tampa Strikers Feb 7

                      'Game82_0327',     # DFA vs Marlex International

                      'Game83_0115',     # Play 365 Bangalore

                      'Game84_0113',     # Real BLR FC - Super Division


                      'Game85_0115',     # Pune PL - Match day 7 1 game
                      'Game86_0115',     # Pune PL - Championship Match day 7 Full 5 games

                      'Game90_0116',     # Pune PL - Championship Match day 8 Full 5 games
                      'Game95_0117',     # Pune PL - Match day 9 Full 5 games

                      'Game100_0127',    # Boyfun FC Atlanta 0-0

                      'Game101_0121',    # Pune PL - Match day 10 Full 5 games

                      'Game106_0327',    # DFA vs Royal Palm SC

                      'Game107_0203',    # Boyfun FC Atlanta 3-3 Done

                      'Game108_0204',    # DFA vs Orlando Rovers
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
                      'Game169_0211',   # PPL - Match day #16 - 4 games
                      'Game173_0217',   # PPL - Match day #17 - 5 games
                      'Game178_0218',   # PPL - Match day #18 - 5 games

                      'Game183_0211',   # URBANRISE | SUPER DIVISION LEAGUE 2024 - 25 | SOUTH UNITED FC VS ASC & CENTER FC | 11.02.2025
                      'Game184_0211',   # URBANRISE | SUPER DIVISION LEAGUE 2024 - 25 | ROOTS FC VS REBELS FC | 11.02.2025
                      'Game185_0210',   # URBANRISE | SUPER DIVISION LEAGUE 2024 - 25 | BENGALURU FC VS FC AGNIPUTHRA | 10.02.2025
                      'Game186_0210',    # URBANRISE | SUPER DIVISION LEAGUE 2024 - 25 | HAL FC VS SPORTING CLUB BENGALURU | 10.02.2025
                      'Game187_0207',    # URBANRISE   SUPER DIVISION LEAGUE 2024 - 25   BANGALORE UNITED FC VS KODAGU FC   07.02.2025
                      'Game188_0207',    # URBANRISE   SUPER DIVISION LEAGUE 2024 - 25   FC REAL BENGALURU VS ASC & CENTER FC   07.02.2025

                      'Game189_0223',    # Peachtree FC vs KWG FC
                      'Game190_0223',    # Peachtree FC vs Leopard FC

                      'Game191_0219',    # Play 365 Bangalore

                      'Game192_0224'    # Boyfun FC Atlanta vs AC Atlanta

                      #'GameX'
                      ]   
    #game_code = game_code_list[3]
    game_code_list = game_code_list[18:19] # #game_code_list[:3] + game_code_list[-1:]
    print(game_code_list)


    file_pairs = []
    for game_code in game_code_list:
        bucket_folder_path = 'ripley_dataset/'#'game-recordings/'+game_code+'/'
        local_folder_path = '../videos/'


        bucket_folder_of_interest = bucket_folder_path
        local_folder_of_interest = local_folder_path

        '''
        if game_code in n_files_from_game_code:
            n = n_files_from_game_code[game_code]
        else:
            n = 2
        
        for i in range(n):
            fnames = [game_code+'_p'+str(i+2)+'.mp4']
    
        for fname in fnames:
            file_pairs.append((bucket_folder_of_interest + fname, 
                               local_folder_of_interest + fname))
        '''
        
        #download_files_from_gcp_bucket(bucket_name, file_pairs)

        download_blobs_in_folder('street-bucket', bucket_folder_path, local_folder_path)

    game_code_list = game_code_list[-2:]
    file_pairs = []
    for game_code in game_code_list:#[:3]:

        print('\nDownloading',game_code)

        
        try:
            print('nvm reels at the moment')
            #get_reels_from_bucket(game_code)
        except:
            print('Failed to download reels for',game_code)
            #'''

        bucket_folder_path = 'game-recordings/'+game_code+'/'
        local_folder_path = '../gcp-data/game-recordings/'+game_code+'/'

        bucket_folder_of_interest = bucket_folder_path + 'output/'
        local_folder_of_interest = local_folder_path

        # Game1_0804_all_music_video_vm003.mp4
        # Game1_0804_goals_music_video_vm003.mp4

        #fnames = ['_goals_music_video_vm004.mp4','_all_music_video_vm004.mp4']
        #fnames = ['_gk_music_video_vm004.mp4','_all_music_video_vm004.mp4']
        
        fnames = ['_all_music_video_vm004.mp4']
        #fnames = ['_goals_music_video_vm004.mp4']
        #fnames = ['_p1.mp4']
        for fname in fnames:
            file_pairs.append((bucket_folder_of_interest + game_code + fname, 
                            local_folder_of_interest + game_code + fname))
    
    #download_files_from_gcp_bucket(bucket_name, file_pairs)

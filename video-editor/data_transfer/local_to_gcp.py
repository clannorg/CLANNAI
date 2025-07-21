from google.cloud import storage
import os
from tqdm import tqdm

def upload_files_to_gcp_bucket(bucket_name, file_pairs):
    """
    Uploads files from local paths to a GCP bucket with a progress bar.
    
    Parameters:
    - bucket_name: Name of the GCP bucket.
    - file_pairs: List of tuples where each tuple contains (local_file_path, destination_blob_name).
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    for local_file_path, destination_blob_name in file_pairs:
        blob = bucket.blob(destination_blob_name)
        
        file_size = os.path.getsize(local_file_path)
        
        with open(local_file_path, 'rb') as file_obj:
            with tqdm.wrapattr(file_obj, 'read', total=file_size, miniters=1, desc=local_file_path, ascii=True) as f:
                blob.upload_from_file(f, size=file_size, timeout=600)

        print(f"File {local_file_path} uploaded to {bucket_name}/{destination_blob_name}.")

if __name__ == "__main__":
    # Example usage
    print(os.getcwd())
    bucket_name = "street-bucket"

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
                      'Game19_0925',    # Bangalore Play 365 - 2 camera
                      'Game20_1001',    # Bangalore Kick n Flick
                      'Game21_0921',    # TS Konigsbrunn vs Harluchs - Drone
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
                      'Game53_0921',

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

                      'Game64_1028',      # Boyfun FC Atlanta
                      'Game65_1030',     # Play 365 Bangalore - 2 camera

                      'Game66_1104',     # Boyfun FC Atlanta
                      'Game67_1109',     # Play 365 Bangalore -  2 camera
                      'Game68_1113',     # Play 365 Bangalore
                      'Game69_1111',     # Play 365 Bangalore
                      'Game70_1117',     # Play 365 Bangalore
                      'Game71_1118',     # Boyfun FC Atlanta
                      # P1 - 20241117_185139
                      # P2 - 20241117_185235

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
    
    #game_code = game_code_list[25]
    game_codes = game_code_list[-2:] #[-10:-9]
    ext_choices = ['timestamps','video','all']
    ext_choice = 0
    video_ext = '.mp4' #'.m2ts'

    n_files_from_game_code = dict()
    n_files_from_game_code['Game24_1006'] = 3
    n_files_from_game_code['Game25_1006'] = 3
    n_files_from_game_code['Game28_1006'] = 3
    n_files_from_game_code['Game30_1006'] = 3
    n_files_from_game_code['Game33_0929'] = 4
    n_files_from_game_code['Game44_1020'] = 7
    n_files_from_game_code['Game52_1020'] = 7
    n_files_from_game_code['Game53_0921'] = 1
    n_files_from_game_code['Game55_1027'] = 3
    n_files_from_game_code['Game57_1027'] = 3
    n_files_from_game_code['Game60_1027'] = 3
    n_files_from_game_code['GameX'] = 1

    n_files_from_game_code['Game63_1028'] = 1
    n_files_from_game_code['Game64_1028'] = 3

    n_files_from_game_code['Game72_1130'] = 1
    n_files_from_game_code['Game73_1124'] = 1
    n_files_from_game_code['Game74_1205'] = 1
    n_files_from_game_code['Game75_1109'] = 1
    n_files_from_game_code['Game76_1205'] = 1

    n_files_from_game_code['Game77_1209'] = 1

    # 2025 onwards
    n_files_from_game_code['Game83_0115'] = 2

    n_files_from_game_code['Game107_0203'] = 2
    n_files_from_game_code['Game130_0210'] = 2
    n_files_from_game_code['Game191_0219'] = 2

    
    file_pairs = []
    for game_code in game_codes:
        if game_code not in n_files_from_game_code:
            n_files = 2
            # 2025 onwards
            n_files = 1
        else:
            n_files = n_files_from_game_code[game_code]
        bucket_folder_path = 'game-recordings/'+game_code+'/'
        local_folder_path = '../game_recordings/'+game_code+'/'

        bucket_folder_of_interest = bucket_folder_path
        local_folder_of_interest = local_folder_path

        video_extensions = []
        timestamp_extensions = []
        # Create video extensions and timestamp extensions with a loop of range n_files
        for i in range(n_files):
            video_extensions.append('_p'+str(i+1)+video_ext)
            timestamp_extensions.append('_p'+str(i+1)+'_timestamps.xlsx')
        
        all_ext = []
        if ext_choice == 0:
            all_ext = timestamp_extensions
        elif ext_choice == 1:
            all_ext = video_extensions
        elif ext_choice == 2:
            all_ext =  timestamp_extensions + video_extensions
        else:
            print('Invalid choice of extensions.')
        
        assert all_ext != [], "No extensions selected."
        for ext in all_ext:
            file_pairs.append((local_folder_path + game_code + ext, bucket_folder_path + game_code + ext))
    

    # For music file transfer
    local_folder_path = '../music/'
    bucket_folder_path = 'music/'
    music_file_name = 'World_Song.mp3'

    #file_pairs = []
    #file_pairs.append((local_folder_path + music_file_name, bucket_folder_path + music_file_name))

    upload_files_to_gcp_bucket(bucket_name, file_pairs)

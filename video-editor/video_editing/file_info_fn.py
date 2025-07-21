import av, re, os
import pytz

from datetime import datetime, timezone, timedelta

'''
Game24_1006
P1 : 20241006_224329
P2 : 20241006_224351
P3 : 20241006_230037

Game25_1006
P1 : 20241006_230341
P2 : 20241006_230400
P3 : 20241006_232143

Game26_1006
P1 : 20241006_232546
P2 : 20241006_232604

Game27_1006
P1 : 20241006_234449
P2 : 20241006_234519

Game28_1006
P1 : 20241007_000937
P2 : 20241007_000954
P3 : 20241007_002634

Game29_1006
P1 : 20241007_003218
P2 : 20241007_003238

Game30_1006
P1 : 20241007_005401
P2 : 20241007_005415
P3 : 20241007_011722

Game31_1006
P1 : 20241007_012312
P2 : 20241007_012330

Game32_1006
P1 : 20241007_014812
P2 : 20241007_014835

Game45_1020
P1 : 20241020_221340
P2 : 20241020_221352

Game46_1020
P1 : 20241020_223124
P2 : 20241020_223139

Game47_1020
P1 : 20241020_225302
P2 : 20241020_225317

Game48_1020
P1 : 20241020_231144
P2 : 20241020_231158

Game49_1020
P1 : 20241020_232932
P2 : 20241020_232953

Game50_1020
P1 : 20241020_235150
P2 : 20241020_235214

Game51_1020
P1 : 20241021_001630
P2 : 20241021_001650

Game52_1020
P1 : 20241021_003826
P2 : 20241021_003843
P3 : 20241021_010100
P4 : 20241021_010200
P5 : 20241021_010300
P6 : 20241021_010400
P7 : 20241021_010500

Game54_1027
P1 : 20241027_214440
P2 : 20241027_214500

Game55_1027
P1 : 20241027_220616
P2 : 20241027_220636
P3 : 20241027_222709

Game56_1027
P1 : 20241027_223254
P2 : 20241027_223158

Game57_1027
P1 : 20241027_225250
P2 : 20241027_225224
P3 : 20241027_231107

Game58_1027
P1 : 20241027_231519
P2 : 20241027_231434

Game59_1027
P1 : 20241027_233517
P2 : 20241027_233443

Game60_1027
P1 : 20241027_235529
P2 : 20241027_235450
P3 : 20241028_001925

Game61_1027
P1 : 20241028_002342
P2 : 20241028_002300

Game62_1027
P1 : 20241028_005141
P2 : 20241028_005109

'''
def get_utc_timestamp_from_ist_timestamp(ist_timestamp_str):
    '''
    Function to convert IST timestamp to UTC timestamp and return in milliseconds

    Input:
    - String of format YYYYMMDD_HHMMSS

    Output:
    - UTC timestamp in milliseconds
    '''
    utc_in_milliseconds = None

    # Define IST timezone (UTC+5:30)
    ist = pytz.timezone('Asia/Kolkata')

    # Parse the IST timestamp string
    ist_datetime = datetime.strptime(ist_timestamp_str, '%Y%m%d_%H%M%S')

    # Localize the datetime to IST timezone
    ist_datetime = ist.localize(ist_datetime)

    # Convert IST datetime to UTC
    utc_datetime = ist_datetime.astimezone(pytz.utc)

    # Get UTC timestamp in milliseconds
    utc_in_milliseconds = int(utc_datetime.timestamp() * 1000)

    #print('FROM IST========UTC',utc_in_milliseconds,'========')
    return utc_in_milliseconds

def get_timestamp_by_game_code(filename):

    if 'Game19_0925' in filename:
        start_time_offset = 6 # seconds
        utc_start = 1727271634000 + start_time_offset*1000

        cut_min = 30
        cut_sec = 6
        first_cut = utc_start + cut_min*60*1000 + cut_sec*1000

        cut_min = 59
        cut_sec = 51
        second_cut = utc_start + cut_min*60*1000 + cut_sec*1000
        if 'p1' in filename:
            print('Returning None timestamp')
            return None
        
        if 'p2' in filename:
            print('Returning UTC start + offset')
            return utc_start
        
        if 'p3' in filename:
            print('Returning first cut')
            return first_cut
        
        if 'p4' in filename:
            print('Returning second cut')
            return second_cut
    
    if 'Game24_1006' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241006_224329')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241006_224351')
        if 'p3' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241006_230037')
    
    if 'Game25_1006' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241006_230341')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241006_230400')
        if 'p3' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241006_232143')
        
    if 'Game26_1006' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241006_232546')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241006_232604')
        
    if 'Game27_1006' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241006_234449')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241006_234519')
    
    if 'Game28_1006' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241007_000937')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241007_000954')
        if 'p3' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241007_002634')
    
    if 'Game29_1006' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241007_003218')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241007_003238')
    
    if 'Game30_1006' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241007_005401')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241007_005415')
        if 'p3' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241007_011722')
        

    if 'Game31_1006' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241007_012312')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241007_012330')
    
    if 'Game32_1006' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241007_014812')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241007_014835')
        
    if 'Game43_1019' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241019_193040')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241019_193013')
        
    if 'Game45_1020' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241020_221340')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241020_221352')
        
    if 'Game46_1020' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241020_223124')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241020_223139')
        
    if 'Game47_1020' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241020_225302')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241020_225317')
    
    if 'Game48_1020' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241020_231144')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241020_231158')
    
    if 'Game49_1020' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241020_232932')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241020_232953')
    
    if 'Game50_1020' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241020_235150')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241020_235214')
    
    if 'Game51_1020' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241021_001630')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241021_001650')
    
    if 'Game52_1020' in filename:
        ts = None
        if 'p1' in filename:
            ts = get_utc_timestamp_from_ist_timestamp('20241021_003826')
        if 'p2' in filename:
            ts = get_utc_timestamp_from_ist_timestamp('20241021_003843')
        if 'p3' in filename:
            ts = get_utc_timestamp_from_ist_timestamp('20241021_020100')
        if '_p4.' in filename:
            ts = get_utc_timestamp_from_ist_timestamp('20241021_020200')
        if 'p5' in filename:
            ts = get_utc_timestamp_from_ist_timestamp('20241021_020300')
        if 'p6' in filename:
            ts = get_utc_timestamp_from_ist_timestamp('20241021_020400')
        if 'p7' in filename:
            ts = get_utc_timestamp_from_ist_timestamp('20241021_020500')
        return ts
    
    if 'Game54_1027' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241027_214440')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241027_214500')
    
    if 'Game55_1027' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241027_220616')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241027_220636')
        if 'p3' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241027_222709')
        
    if 'Game56_1027' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241027_223254')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241027_223158')
    
    if 'Game57_1027' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241027_225250')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241027_225224')
        if 'p3' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241027_231107')
        
    if 'Game58_1027' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241027_231519')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241027_231434')
        
    if 'Game59_1027' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241027_233517')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241027_233443')
    
    if 'Game60_1027' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241027_235529')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241027_235450')
        if 'p3' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241028_001925')
        
    if 'Game61_1027' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241028_002342')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241028_002300')
        
    if 'Game62_1027' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241028_005141')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241028_005109')
    
    if 'Game65_1030' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241030_192453')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241030_192518')
    
    if 'Game67_1109' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241109_184655')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241109_184815')
        
    
    if 'Game68_1113' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241113_191949')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241113_192119')

    if 'Game70_1117' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241117_185139')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20241117_185235')
    
    if 'Game83_0115' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20250115_193500')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20250115_193525')

    if 'Game191_0219' in filename:
        if 'p1' in filename:
            return get_utc_timestamp_from_ist_timestamp('20250219_194249')
        if 'p2' in filename:
            return get_utc_timestamp_from_ist_timestamp('20250219_194353')
    
    return None

def convert_milliseconds_to_utc_string(milliseconds):
    """
    Converts milliseconds since the Unix epoch to a UTC timestamp string in ISO 8601 format.

    Parameters:
    - milliseconds (int): Milliseconds since the Unix epoch.

    Returns:
    - str: UTC timestamp string in ISO 8601 format.
    """
    # Define IST timezone (UTC+5:30)
    IST = timezone(timedelta(hours=5, minutes=30))

    # Create a datetime object from milliseconds since epoch
    dt_utc = datetime.fromtimestamp(milliseconds / 1000, tz=timezone.utc)

    # Format the datetime object into an ISO 8601 string with 'Z' to indicate UTC
    # utc_string = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    # Convert UTC datetime to IST datetime
    dt_ist = dt_utc.astimezone(IST)

    # Format the datetime object into a string
    ist_string = dt_ist.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + '+0530'

    return ist_string


def get_utc_timestamp_in_milliseconds(timestamp_str):
    """
    Converts a UTC timestamp string into milliseconds since the Unix epoch.

    Parameters:
    - timestamp_str (str): A string representing the UTC timestamp in ISO 8601 format.

    Returns:
    - int: Milliseconds since the Unix epoch.

    Raises:
    - ValueError: If the input string does not match the expected format.
    """
    if timestamp_str is None:
        return 0
    try:
        # Handle timestamps ending with 'Z' (indicating UTC)
        if timestamp_str.endswith('Z'):
            timestamp_str = timestamp_str.rstrip('Z')
            # Try parsing with microseconds
            try:
                dt = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                # Try parsing without microseconds
                dt = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S')
            # Set timezone to UTC
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            # Try parsing with microseconds and timezone offset
            try:
                dt = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%f%z')
            except ValueError:
                # Try parsing without microseconds
                dt = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S%z')
    except ValueError:
        raise ValueError("Timestamp string is not in the expected ISO 8601 format.")

    # Convert the datetime object to milliseconds since the Unix epoch
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    milliseconds_since_epoch = int((dt - epoch).total_seconds() * 1000)

    return milliseconds_since_epoch



def get_video_time_utc(file_path):
    try:
        container = av.open(file_path)
        # Access container metadata for timestamps
        container_metadata = container.metadata
        print("\nTimestamps:")
        timestamp_found = False
        if container_metadata:
            for key, value in container_metadata.items():
                if 'creationdate' in key.lower():
                    print(f"  {key}: {value}")
                    timestamp_found = True
                    return value
        if not timestamp_found:
            print('\n===Timestamps not found in container metadata.===\n')
        # assert timestamp_found, "==================== No timestamp found! Check video metadata container manually. ===================="
    except av.AVError as e:
        print(f"An AV package file error occurred: {e}")
        return None

def get_location_lat_long(filename):
    """
    Extracts latitude and longitude from the metadata of a media file.

    Parameters:
    - filename (str): The path to the media file.

    Returns:
    - tuple: (latitude, longitude) as floats if available, otherwise (None, None).
    """

    try:
        # Open the media file
        container = av.open(filename)
        
        # Access container metadata
        metadata = container.metadata

        # Initialize variables
        latitude = None
        longitude = None

        # Check for location metadata in 'com.apple.quicktime.location.ISO6709'
        location_iso6709 = metadata.get('com.apple.quicktime.location.ISO6709')
        
        if location_iso6709:
            # Parse the ISO 6709 location string
            # Example format: '+13.0541+077.5688+904.027/'
            match = re.match(r'([+-]\d+\.\d+)([+-]\d+\.\d+)', location_iso6709)
            if match:
                lat_str = match.group(1)
                lon_str = match.group(2)
                latitude = float(lat_str)
                longitude = float(lon_str)
                return (latitude, longitude)
            else:
                # Handle cases where altitude is included or different formats
                # Split the string into components
                coords = re.findall(r'[+-]\d+\.\d+', location_iso6709)
                if len(coords) >= 2:
                    latitude = float(coords[0])
                    longitude = float(coords[1])
                    return (latitude, longitude)

        else:
            print('No location metadata found!')
            for m_key in metadata.keys():
                if 'location' in m_key.lower():
                    print(f"Alternate Location key found: {m_key}")
            
            # Check for GPS metadata in other common tags
            gps_latitude = metadata.get('location_latitude')
            gps_longitude = metadata.get('location_longitude')
            if gps_latitude and gps_longitude:
                latitude = float(gps_latitude)
                longitude = float(gps_longitude)
                return (latitude, longitude)

        # If location metadata is not found
        return (None, None)

    except av.AVError as e:
        print(f"An error occurred: {e}")
        return (None, None)

def get_creation_time_av(file_path):
    '''
    NOT USED IN THE CODE
    Function to get the creation time of a video file using the av package.
    '''
    try:
        container = av.open(file_path)
        # Access metadata from the container
        creation_time = container.metadata.get('creation_time')
        if creation_time:
            print(f"Creation time: {creation_time}")
            return creation_time
        else:
            print("Creation time not found in metadata.")
            return None
    except av.AVError as e:
        print(f"An error occurred: {e}")
        return None

def display_metadata(file_path):
    '''
    NOT USED IN THE CODE

    Function to display metadata of a video file using the av package.

    Parameters:
    - file_path (str): Path to the video file.

    Returns:
    - None
    '''
    try:
        container = av.open(file_path)
        
        # File size
        file_size = os.path.getsize(file_path)
        print(f"File Size: {file_size} bytes")
        
        # Access container metadata for timestamps
        container_metadata = container.metadata
        print("\nTimestamps:")
        timestamps_found = False
        if container_metadata:
            for key, value in container_metadata.items():
                if 'time' in key.lower() or 'date' in key.lower():
                    print(f"  {key}: {value}")
                    timestamps_found = True
        if not timestamps_found:
            print("  No timestamps found in container metadata.")
        
        # Video quality details
        print("\nVideo Quality Details:")
        video_streams = [s for s in container.streams if s.type == 'video']
        if video_streams:
            for stream in video_streams:
                codec = stream.codec_context
                print(f"\nStream #{stream.index}:")
                print(f"  Codec: {codec.name}")
                print(f"  Codec Long Name: {codec.codec.long_name}")
                print(f"  Width: {codec.width} pixels")
                print(f"  Height: {codec.height} pixels")
                print(f"  Pixel Format: {codec.format.name if codec.format else 'N/A'}")
                frame_rate = stream.average_rate
                if frame_rate:
                    print(f"  Frame Rate: {float(frame_rate)} fps")
                else:
                    print("  Frame Rate: N/A")
                bitrate = stream.bit_rate if stream.bit_rate else 'N/A'
                print(f"  Bitrate: {bitrate} bps")
        else:
            print("  No video streams found.")
        
    except av.AVError as e:
        print(f"An error occurred: {e}")


def get_game_info_from_game_code(video_filename):
    '''
    Function to get the game information from the game code.
    '''
    # Extract the Game code pattern
    match = re.search(r"Game\d+_\d+", video_filename)

    # Print the result
    if match:
        print('Game code:',match.group(0))  # Outputs: Game84_0113
        game_code = match.group(0)
    else:
        print('File name:',video_filename)
        raise ValueError("Game code not found in the filename.")
    # Found game code
    
    game_info = dict()

    # Game code is the string after 'Game' and before the next '_'
    game_info['game_code'] = game_code
    
    # print('Game Code:', game_code)
    game_info['left_team'] = None
    game_info['right_team'] = None
    
    game_info['left_score'] = 0
    game_info['right_score'] = 0

    team1_1013 = 'RET' # Retired FC
    team2_1013 = 'MNK' # Monk FC
    team3_1013 = 'UNB' # United Brothers FC
    team4_1013 = 'ELH' # El Hechinoz FC
    team5_1013 = 'AUF' # Aufside FC
    team6_1013 = 'PBL' # Pooky Blinders FC

    team1_1019 = 'ABI' # ABI Brewmaster
    team2_1019 = 'MDW' # Madiwala Boys

    if 'Game34_1013' in video_filename:
        game_info['left_team'] = team1_1013
        game_info['right_team'] = team3_1013
    
    if 'Game35_1013' in video_filename:
        game_info['left_team'] = team2_1013
        game_info['right_team'] = team1_1013
    
    if 'Game36_1013' in video_filename:
        game_info['left_team'] = team2_1013
        game_info['right_team'] = team3_1013

    if 'Game37_1013' in video_filename:
        game_info['left_team'] = team4_1013
        game_info['right_team'] = team5_1013
    
    if 'Game38_1013' in video_filename:
        game_info['left_team'] = team5_1013
        game_info['right_team'] = team6_1013
    
    if 'Game39_1013' in video_filename:
        game_info['left_team'] = team4_1013
        game_info['right_team'] = team6_1013
    
    if 'Game40_1013' in video_filename:
        game_info['left_team'] = team5_1013
        game_info['right_team'] = team2_1013
    
    if 'Game41_1013' in video_filename:
        game_info['left_team'] = team4_1013
        game_info['right_team'] = team3_1013
    
    if 'Game42_1013' in video_filename:
        game_info['left_team'] = team2_1013
        game_info['right_team'] = team3_1013

    if 'Game43_1019' in video_filename:
        game_info['left_team'] = team1_1019
        game_info['right_team'] = team2_1019
    
    team1_1020 = 'ELH' # El Hechinoz FC
    team2_1020 = 'BDX' # Borgadix FC
    team3_1020 = 'JAM' # Jam Company
    team4_1020 = 'PBL' # Pooky Blinders FC
    team5_1020 = 'ODM' # OD Mariners
    team6_1020 = 'AUF' # Aufside FC

    if 'Game44_1020' in video_filename:
        game_info['left_team'] = team1_1020
        game_info['right_team'] = team2_1020

    if 'Game45_1020' in video_filename:
        game_info['left_team'] = team3_1020
        game_info['right_team'] = team2_1020

    if 'Game46_1020' in video_filename:
        game_info['left_team'] = team1_1020
        game_info['right_team'] = team3_1020
    
    if 'Game47_1020' in video_filename:
        game_info['left_team'] = team4_1020
        game_info['right_team'] = team5_1020

    if 'Game48_1020' in video_filename:
        game_info['left_team'] = team6_1020
        game_info['right_team'] = team5_1020
    
    if 'Game49_1020' in video_filename:
        game_info['left_team'] = team6_1020
        game_info['right_team'] = team4_1020

    if 'Game50_1020' in video_filename:
        game_info['left_team'] = team3_1020
        game_info['right_team'] = team5_1020
    
    if 'Game51_1020' in video_filename:
        game_info['left_team'] = team4_1020
        game_info['right_team'] = team2_1020

    if 'Game52_1020' in video_filename:
        game_info['left_team'] = team5_1020
        game_info['right_team'] = team2_1020

    team1_1027 = 'SWY' # Sewey FC
    team2_1027 = 'ELH' # El Hechinoz
    team3_1027 = 'WLF' # Wolfpack FC
    team4_1027 = 'ISL' # Island FC
    team5_1027 = 'BDX' # Borgadix FC
    team6_1027 = 'KMN' # Kingsmen FC

    if 'Game54_1027' in video_filename:
        game_info['left_team'] = team1_1027
        game_info['right_team'] = team4_1027
    
    if 'Game55_1027' in video_filename:
        game_info['left_team'] = team2_1027
        game_info['right_team'] = team3_1027
    
    if 'Game56_1027' in video_filename:
        game_info['left_team'] = team5_1027
        game_info['right_team'] = team4_1027
    
    if 'Game57_1027' in video_filename:
        game_info['left_team'] = team6_1027
        game_info['right_team'] = team3_1027
    
    if 'Game58_1027' in video_filename:
        game_info['left_team'] = team5_1027
        game_info['right_team'] = team1_1027
    
    if 'Game59_1027' in video_filename:
        game_info['left_team'] = team2_1027
        game_info['right_team'] = team6_1027

    if 'Game60_1027' in video_filename:
        game_info['left_team'] = team2_1027
        game_info['right_team'] = team4_1027
    
    if 'Game61_1027' in video_filename:
        game_info['left_team'] = team5_1027
        game_info['right_team'] = team6_1027
    
    if 'Game62_1027' in video_filename:
        game_info['left_team'] = team5_1027
        game_info['right_team'] = team4_1027

    if 'Game63_1028' in video_filename:
        game_info['left_team'] = 'NEAR'
        game_info['right_team'] = 'FAR'
    
    if 'Game65_1030' in video_filename \
        or 'Game68_1113' in video_filename \
            or 'Game67_1109' in video_filename \
                or 'Game70_1117' in video_filename \
                    or 'Game83_0115'in video_filename:
        game_info['left_team'] = 'LFT'
        game_info['right_team'] = 'RYT'
    
    if 'Game72_1130' in video_filename:
        game_info['left_team'] = 'WSA'
        game_info['right_team'] = 'GFC'
    
    if 'Game78_0601' in video_filename:
        game_info['left_team'] = 'DFA' # Dynamic Futbol Academy
        game_info['right_team'] = 'SHK' # Shock City FC

    if 'Game79_0511' in video_filename:
        game_info['left_team'] = 'DFA'
        game_info['right_team'] = 'NCL' # Nacional

    if 'Game80_0518' in video_filename:
        game_info['left_team'] = 'DFA'
        game_info['right_team'] = 'CWC' # Clearwater Chargers
    
    if 'Game81_0207' in video_filename:
        game_info['left_team'] = 'DFA'
        game_info['right_team'] = 'TSK' # Tampa Strikers
    
    

    return game_info


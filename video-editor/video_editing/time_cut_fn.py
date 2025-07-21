import pandas as pd

def read_timestamps(file_name, exclude_last_line = True, default_start_offset = 7, default_end_offset = 3):
    '''
    Function to read timestamps from a xlsx file

    Inputs:
    - file_path: Path to the xlsx file with columns: Timestamp, Label, Description

    Output:
    - timestamps: List of timestamps
    - label_dict: Dictionary of labels, descriptions with timestamps as key
    '''

    # Read the xlsx file 
    df = pd.read_excel(file_name)

    # Get the timestamps and labels
    timestamps_str = df['Timestamp'].tolist()

    # Timestamps are of the format 'mm;ss' - Extract the timestamp from each of the string
    timestamps = []
    for ts in timestamps_str:
        #print(ts)
        ts_split = ts.split(';')
        
        if len(ts_split) == 2:  # mm;ss format
            ts_mins = int(ts_split[0])
            ts_secs = int(ts_split[1])
            ts_millis = ts_mins*60*1000 + ts_secs*1000
        elif len(ts_split) == 3:  # hh;mm;ss format
            ts_hours = int(ts_split[0])
            ts_mins = int(ts_split[1]) 
            ts_secs = int(ts_split[2])
            ts_millis = ts_hours*3600*1000 + ts_mins*60*1000 + ts_secs*1000
            
        # timestamps.append(ts_millis) UPGRADE TEST - testing replacement with moviepy based class
        ts_seconds = ts_millis / 1000  # Convert milliseconds to seconds
        timestamps.append(ts_seconds)  # Append the timestamp in seconds
    
    if exclude_last_line:
        timestamps = timestamps[:-1] # Remove the last timestamp which is just the video end timestamp
    
    #timestamps = timestamps[:3]
    # Get labels and descriptions for each timestamp
    labels = df['Label'].tolist()
    descriptions = df['Description'].tolist()

    # Check if column names contain Start_offset and End_offset
    if 'Start_offset' in df.columns and 'End_offset' in df.columns:
        start_offsets = df['Start_offset'].tolist()
        end_offsets = df['End_offset'].tolist()
    else:
        start_offsets = [default_start_offset]*len(timestamps)
        end_offsets = [default_end_offset]*len(timestamps)
    
    if 'Camera_view' in df.columns:
        camera_views = df['Camera_view'].tolist()
    else:
        camera_views = [None]*len(timestamps)

    # Create a dictionary of labels and descriptions with timestamps as key
    label_dict = {}
    for i in range(len(timestamps)): # Remove last timestamp which is just the video end timestamp
        label_dict[i] = (timestamps[i],labels[i], descriptions[i], start_offsets[i], end_offsets[i], camera_views[i])

    return label_dict

def get_timebands_from_timestamps(label_indices_of_interest, label_dict):
    '''
    Function to get timebands from timestamps and labels, filtered by labels of interest

    Inputs:
    - timestamps: List of timestamps (in milliseconds)
    - labels: List of labels corresponding to the timestamps
    - labels_of_interest: List of labels of interest for filtering
    - start_offset: Start offset in seconds
    - end_offset: End offset in seconds


    Output:
    - timebands: List of [start, end] timebands filtered by labels of interest
    '''
    timebands = []
    camera_views = []
    descriptions = []
    labels = []
    
    # Iterate through the labels
    for i in label_indices_of_interest:

        start_offset = label_dict[i][3]
        end_offset = label_dict[i][4]

        timestamp = label_dict[i][0]

        start = timestamp - start_offset # in seconds
        end = timestamp + end_offset # in seconds

        description = label_dict[i][2]
        if not isinstance(description, str):
            description = 'No description'
        
        camera_view = label_dict[i][5]

        label = label_dict[i][1]
        
        print('Description:', description)
        timebands.append([start, end])
        camera_views.append(camera_view)
        descriptions.append(description)
        labels.append(label)
    
    timebands_and_metadata = dict()
    timebands_and_metadata['timebands'] = timebands
    timebands_and_metadata['descriptions'] = descriptions
    timebands_and_metadata['camera_views'] = camera_views
    timebands_and_metadata['labels'] = labels

    return timebands_and_metadata
        
def remove_overlap_from_timebands(timebands):
    '''
    NOT USED AT THE MOMENT
    Function to remove overlap from timebands

    Timebands is a list of [start, end] timestamps that may contain overlapping segments
    Filtering is done to remove the overlapping segments, and provide a list of non-overlapping segments in chronological order

    Inputs:
    timebands: List of [start, end] timebands
    Output:
    filtered_timebands: List of non-overlapping [start, end] timebands
    '''

    # Check that the timebands are in chronological order
    timebands = sorted(timebands, key=lambda x: x[0])

    # Initialize the list of filtered timebands
    filtered_timebands = []

    # Iterate through the timebands
    for i in range(len(timebands)):
        # Check if the current timeband overlaps with the previous timeband
        if i == 0 or timebands[i][0] > filtered_timebands[-1][1]:
            filtered_timebands.append(timebands[i])
        else:
            # Update the end time of the previous timeband
            filtered_timebands[-1][1] = timebands[i][1]

    return filtered_timebands


def timestamp_selector(label_dict, labels_of_interest = None):
    '''
    Function to select timestamps based on labels of interest

    Input:
    - timestamps: List of timestamps
    - label_dict: Dictionary of { timestamp : (label, descriptions) } with timestamps as key
    - labels_of_interest: List of labels of interest for filtering
    '''
    label_indices_of_interest = []
    j = 0
    # for timestamp in timestamps:
    for i in range(len(label_dict.keys())):

        #label, desc, s_off, e_off, camera_view = label_dict[timestamp]
        timestamp, label, desc, s_off, e_off, camera_view = label_dict[i]

        # To make ripleys of previous games from description (ripley mentioned there) and goals
        #if label.lower() == 'skip' or ('ripley' not in desc.lower() and label.lower() != 'goal!'): 
        #if label.lower() == 'skip' or 'ripley' not in camera_view.lower(): 
        
        # #camera_view.lower() == 'ripley' or camera_view.lower() == 'software_cam':# or label.lower() != 'goal!':# 

        if isinstance(desc, str):
            if label.lower() == 'skip' or 'skip' in desc.lower():
                print("Skipping...")
                continue
        else:
            if label.lower() == 'skip':
                print("Skipping...")
                continue
        
        
        '''
        if j > 3: #Stop after x+1 events
            break
        else:
            j+=1 #'''

        # Accounts for all_labels when labels_of_interest is None, and allows for skipping of labels above
        if labels_of_interest is None or label in labels_of_interest: # and desc == 'Penalty kick':
            label_indices_of_interest.append(i)
        
        ''' # To test one goal only
        if label.lower() == 'goal!':
            break
        # '''

    return label_indices_of_interest



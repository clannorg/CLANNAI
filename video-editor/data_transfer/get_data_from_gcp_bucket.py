'''
Functions to download files from GCP bucket to VM/Local
'''

import os
import time

from google.cloud import storage
from tqdm import tqdm


def download_blob(bucket_name, source_blob_name, destination_file_name, pbar=None):
    """Downloads a blob from the bucket and updates the progress bar."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)
    blob_size = blob.size if blob.size else 0  # Check if blob.size is None
    with open(destination_file_name, 'wb') as f:
        with tqdm.wrapattr(f, 'write', total=blob_size, miniters=1, desc=blob.name) as file_obj:
            blob.download_to_file(file_obj)

    if blob_size and pbar is not None:  # Only update the progress bar if blob_size is valid
        pbar.update(blob_size)
    return None


def download_blobs_in_folder(bucket_name, folder_name, destination_folder):
    """Downloads all blobs in a folder from the bucket and shows progress based on total file size."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=folder_name))
    
    total_size = sum(blob.size for blob in blobs if blob.size)
    
    with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading files") as pbar:
        for blob in blobs:
            # Construct the destination file path
            destination_file_name = os.path.join(destination_folder, blob.name)
            if blob.name.endswith('/'):
                continue

            download_blob(bucket_name, blob.name, destination_file_name, pbar)
    return None

def download_single_file_from_gcp_bucket(source_blob_name, destination_file_name, bucket_name="street-bucket"):

    download_blob(bucket_name, source_blob_name, destination_file_name)

    return None

def get_game_recording_folder_contents(game_folder_name, destination_folder="./data", bucket_name="street-bucket"):

    # Replace with your bucket name and the folder you want to download
    folder_name = "game-recordings/"+game_folder_name
    # Download all blobs in the folder
    download_blobs_in_folder(bucket_name, folder_name, destination_folder)

    return None

def run_get_data_from_gcp_bucket():

    start = time.time()

    game_code = 'Game1_0804'


    source_blob_name = 'game-recordings/'+game_code+'/' + game_code +'_p1.mp4'
    destination_file_name = './gcp-data/game-recordings/'+game_code+'/' + game_code +'_p1.mp4'
    #download_single_file_from_gcp_bucket(source_blob_name, destination_file_name)

    source_blob_name = 'game-recordings/'+game_code+'/' + game_code +'_p2.mp4'
    destination_file_name = './gcp-data/game-recordings/'+game_code+'/' + game_code +'_p2.mp4'
    #download_single_file_from_gcp_bucket(source_blob_name, destination_file_name)

    source_blob_name = 'game-recordings/'+game_code+'/' + game_code +'_full_cut_vm003.mp4'
    destination_file_name = './gcp-data/game-recordings/'+game_code+'/' + game_code +'_full_cut_v003.mp4'
    #download_single_file_from_gcp_bucket(source_blob_name, destination_file_name)

    # Download all blobs in the folder
    game_code = 'Game3_0807/'
    #get_game_recording_folder_contents(game_code)

    # Get music file
    source_blob_name = 'music/Aylex_Building_Dreams.mp3'
    destination_file_name = './data/music/Aylex_Building_Dreams.mp3'
    download_single_file_from_gcp_bucket(source_blob_name, destination_file_name)

    print('Time taken to get files from GCP:', round(time.time()-start))
    
    return None

def run_get_game_data_from_gcp_bucket_to_vm(game_code):
    # Replace with your bucket name and the folder you want to download

    # Download all blobs in the folder
    start = time.time()
    get_game_recording_folder_contents(game_code)
    print('Time taken to get files from GCP:', round(time.time()-start),'seconds')

    return None


if __name__ == "__main__":

    #run_get_data_from_gcp_bucket()

    fname = 'STREET_logo_large.png'
    source_folder = 'logo/'
    destination_folder = './data/logo/'

    fname = 'Pixel_Pig.mp3'
    source_folder = 'music/'
    destination_folder = './data/music/'

    fname = 'Game86_0115_p1_timestamps.xlsx'
    #fname = 'Game72_1130_p1.m2ts'
    source_folder = 'game-recordings/Game86_0115/'
    destination_folder = './data/game-recordings/Game86_0115/'

    source_blob_name = source_folder + fname
    destination_file_name = destination_folder + fname

    #download_single_file_from_gcp_bucket(source_blob_name, destination_file_name)

    source_folder = 'annotator_eval/round_1/'
    destination_folder = './data/'
    download_blobs_in_folder('street-bucket', source_folder, destination_folder)
    pass


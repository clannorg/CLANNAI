'''
Functions to upload files from VM/Local to GCP bucket
'''

import os
import time

from google.cloud import storage
from tqdm import tqdm

def upload_file_to_gcp_bucket_in_chunks(bucket_name, local_file_path, destination_blob_name):
    """Uploads a local file to a GCP bucket with a progress bar."""
    
    # Initialize the storage client and bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    # Get the size of the file
    file_size = os.path.getsize(local_file_path)

    # Open the file and upload it in chunks while updating the progress bar
    with open(local_file_path, 'rb') as file_obj:
        with tqdm(total=file_size, unit='B', unit_scale=True, desc=local_file_path, ascii=True) as pbar:
            while True:
                chunk = file_obj.read(1024 * 1024)  # Read in 1 MB chunks
                if not chunk:
                    break
                blob.upload_from_file(file_obj, size=len(chunk), timeout=600)
                pbar.update(len(chunk))

    print(f"File {local_file_path} uploaded to {bucket_name}/{destination_blob_name}.")
    return None

def upload_file_to_gcp_bucket_progress_bar_gone(bucket_name, local_file_path, destination_blob_name):
    """Uploads a local file to a GCP bucket with a progress bar."""
    
    # Initialize the storage client and bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    # Get the size of the file
    file_size = os.path.getsize(local_file_path)

    # Define a callback function to update the progress bar
    with tqdm(total=file_size, unit='B', unit_scale=True, desc=local_file_path, ascii=True) as pbar:
        def progress_callback(current, total):
            pbar.update(current - pbar.n)
        
        # Upload the file with the progress callback
        #blob.upload_from_filename(local_file_path, timeout=600, client=storage_client, raw_download=True, progress=progress_callback)
        blob.upload_from_filename(local_file_path, timeout=600)


    print(f"File {local_file_path} uploaded to {bucket_name}/{destination_blob_name}.")


def upload_file_to_gcp_bucket(bucket_name, local_file_path, destination_blob_name):
    """Uploads a local file to a GCP bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(local_file_path)
    print(f"File {local_file_path} uploaded to {bucket_name}/{destination_blob_name}.")

    
def usage_example(game_code):
    # Example usage
    start = time.time()
    bucket_name = "street-bucket"
    

    destination_folder = 'game-recordings/'+game_code+'/'

    local_file_folder = './data/game-recordings/'+game_code+'/'


    local_file_name = game_code+"_p1_cut_vm003.mp4"
    destination_blob_name = destination_folder + local_file_name
    local_file_path = local_file_folder + local_file_name
    #upload_file_to_gcp_bucket(bucket_name, local_file_path, destination_blob_name)

    local_file_name = game_code+"_p2_cut_vm003.mp4"
    destination_blob_name = destination_folder + local_file_name
    local_file_path = local_file_folder + local_file_name
    #upload_file_to_gcp_bucket(bucket_name, local_file_path, destination_blob_name)

    local_file_name = game_code+"_p3_cut_vm003.mp4"
    destination_blob_name = destination_folder + local_file_name
    local_file_path = local_file_folder + local_file_name
    #upload_file_to_gcp_bucket(bucket_name, local_file_path, destination_blob_name)



    local_file_folder = './data/game-recordings/'+game_code+'/'
    local_file_name = game_code+ "_music_cut_vm003.mp4"
    destination_blob_name = destination_folder + local_file_name
    local_file_path = local_file_folder + local_file_name
    upload_file_to_gcp_bucket(bucket_name, local_file_path, destination_blob_name)

    print('Time taken to write files to ' + bucket_name + ':'+str(round(time.time()-start)))
    # Time taken for 600 MB 5 minute 60 FPS highlight video file - 38 seconds
    return None

def run_put_data_into_gcp_bucket_from_vm(game_code, local_file_name):

    start = time.time()
    bucket_name = "street-bucket"
    destination_folder = 'game-recordings/' + game_code + '/output/'
    local_file_folder = './data/game-recordings/' + game_code + '/output/'

    #local_file_name = game_code+"_p1_cut_vm003.mp4"

    destination_blob_name = destination_folder + local_file_name
    local_file_path = local_file_folder + local_file_name
    upload_file_to_gcp_bucket(bucket_name, local_file_path, destination_blob_name)

    print('Time taken to write files to ' + bucket_name + ':'+str(round(time.time()-start)), 'seconds')
    # Time taken for 600 MB 5 minute 60 FPS highlight video file - 38 seconds
    return None

def main():
    game_code = 'Game3_0807'
    #usage_example(game_code)

    bucket_name = "street-bucket"

    local_folder = './test_and_delete/'
    local_file_name = 'bellandur_blast_annotated.mp4'
    local_file_path = local_folder + local_file_name
    destination_folder = 'test_and_delete/'
    destination_blob_name = destination_folder + 'bellandur_blast_annotated.mp4'
    upload_file_to_gcp_bucket(bucket_name, local_file_path, destination_blob_name)


if __name__ == "__main__":
    main()
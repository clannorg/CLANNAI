import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from street.video_editing.time_cut_fn import read_timestamps, timestamp_selector, get_timebands_from_timestamps


def create_onehot_vector(timebands, end_time):
    '''
    Function to create a one hot vector for the timebands

    Inputs:
    - timebands: List of [start, end] timebands

    Output:
    - timebands_onehot: One hot vector for the timebands
    '''
    # Get the maximum timeband
    if end_time is not None:
        max_timeband = end_time
    else:
        max_timeband = max([timeband[1] for timeband in timebands])
    
    # Create a zero vector for the timebands
    timeband_onehot = [0]*max_timeband
    #print(timeband_onehot)
    for i, timeband in enumerate(timebands):
        start = int(timeband[0])
        end = int(timeband[1])
        #print(i, timeband)
        #print(start, end)
        for t in range(start, end):
            try:
                timeband_onehot[t] = 1
            except Exception as e:
                print('Error',e)
                print('Error at', t)
                print('Timeband index:', i)
                print('Timeband:', timeband)
                print('End time:', end_time)
                raise

    return timeband_onehot

def compare_onehot_vectors(timebands_eval_onehot, timebands_cand_onehot):
    '''
    Function to compare two one hot vectors

    Inputs:
    - timebands_eval_onehot: One hot vector for the eval timebands
    - timebands_cand_onehot: One hot vector for the candidate timebands

    Output:
    - dot_product: Dot product of the two one hot vectors
    - jaccard_similarity: Jaccard similarity of the two one hot vectors
    - cosine_similarity: Cosine similarity of the two one hot vectors
    '''
    print('\n\nComparing the two one hot vectors')

    #print('\nEval',timebands_eval_onehot)
    #print('\nCand',timebands_cand_onehot)
    # Get the dot product of the two one hot vectors
    dot_product = np.dot(timebands_eval_onehot, timebands_cand_onehot)
    #print('Coverage by dot product:', dot_product,'which should be close to', np.sum(timebands_eval_onehot))
    coverage = int(dot_product*100/np.sum(timebands_eval_onehot))
    print('Coverage %  (by dot product)= ', coverage)

    # Get the Jaccard similarity of the two one hot vectors
    # Intersection over Union
    jaccard_similarity = round(np.sum(np.logical_and(timebands_eval_onehot, timebands_cand_onehot)) / np.sum(np.logical_or(timebands_eval_onehot, timebands_cand_onehot)),2)
    print('Similarity based on Jaccard similarity (IOU):', jaccard_similarity)

    # Get the cosine similarity of the two one hot vectors
    cosine_similarity = round(np.dot(timebands_eval_onehot, timebands_cand_onehot) / (np.linalg.norm(timebands_eval_onehot) * np.linalg.norm(timebands_cand_onehot)),2)
    print('Similarity based on cosine similarity:', cosine_similarity)

    return coverage, dot_product, jaccard_similarity, cosine_similarity

def evaluate_single_candidates(candidate_file_name, eval_file_name, end_time):
    # Read the timestamps from the excel file
    label_dict_eval_timestamps = read_timestamps(eval_file_name)
    label_dict_cand_timestamps = read_timestamps(candidate_file_name, False)
    
    # Get the timebands from the eval timestamps
    label_indices_of_interest_eval = timestamp_selector(label_dict_eval_timestamps)
    timebands_and_info_eval = get_timebands_from_timestamps(label_indices_of_interest_eval, label_dict_eval_timestamps)

    # Get the timebands from the candidate timestamps
    label_indices_of_interest_cand = timestamp_selector(label_dict_cand_timestamps)
    timebands_and_info_cand = get_timebands_from_timestamps(label_indices_of_interest_cand, label_dict_cand_timestamps)

    # Check goals
    labels_eval = timebands_and_info_eval['labels']
    labels_cand = timebands_and_info_cand['labels']

    eval_gcount = 0
    cand_gcount = 0
    for i, label in enumerate(labels_eval):
        if 'goal' in label.lower():
            eval_gcount += 1
    for i, label in enumerate(labels_cand):
        if 'goal' in label.lower():
            cand_gcount += 1
    
    assert eval_gcount == cand_gcount, f"Goal count mismatch: Eval: {eval_gcount}, Cand: {cand_gcount}"

    timebands_eval = timebands_and_info_eval['timebands']
    timebands_cand = timebands_and_info_cand['timebands']

    # Create a one hot vector for the timebands
    
    timebands_eval_onehot = create_onehot_vector(timebands_eval, end_time)
    timebands_cand_onehot = create_onehot_vector(timebands_cand, end_time)

    # Compare the one hot vectors
    cov, dp, js, cs = compare_onehot_vectors(timebands_eval_onehot, timebands_cand_onehot)

    return timebands_cand_onehot, cov, dp, js, cs

def main():


    eval_file_name = './data/annotator_eval/round_1/eval.xlsx'
    end_time = 106*60+28 # Video length in seconds

    candidate_file_folder = './data/annotator_eval/round_1/'
    candidate_file_list = os.listdir(candidate_file_folder)


    list_of_readable_files = ['kkamlesh938.xlsx',       # invited for interview - got all goals
            'annotation_subham.banik82.xlsx',            # invited for interview - lot of extra annotations
            'annotation_street.xlsx', # Out - low coverage
            # 'annotation_rashmithombre.xlsx', Waiting on updated file
            #'annotation_maniish.raai.xlsx', # Out - 0 coverage + timestamps are not ordered
            'annotation_chinchurocking.xlsx',            # invited for interview - got all goals
            # 'annotation_FatimaShakeel-fatimashaakeel930.xlsx', Too few annotations
            'annotation_arnabchowdhury732.xlsx']        # invited for interview - got all goals

    candidate_file_list = list_of_readable_files

    candidate_path_list = [candidate_file_folder + candidate_file for candidate_file in candidate_file_list]
    #print(candidate_path_list)

    candidate_vector_list = []

    coverage = []
    dot_product = []
    jaccard_similarity = []
    cosine_similarity = []
    total_times = []
    for candidate_file_name in candidate_path_list:

        print(f"\n\nEvaluating candidate file: {candidate_file_name}")

        timebands_cand_onehot, cov, dp, js, cs = evaluate_single_candidates(candidate_file_name, eval_file_name, end_time)
        candidate_vector_list.append(timebands_cand_onehot)

        coverage.append(cov)
        dot_product.append(dp)
        jaccard_similarity.append(js)
        cosine_similarity.append(cs)
        total_times.append(sum(timebands_cand_onehot))
        

        # End for loop
    

    print('Coverage',coverage)
    print('Dot product',dot_product)
    print('Jaccard similarity',jaccard_similarity)
    print('Cosine similarity',cosine_similarity)
    print('Total times',total_times)

    # General trend analysis

    # Create bar chart showing coverage of each element

    # Sum candidate vectors across all candidates
    candidate_vector_sum = np.sum(candidate_vector_list, axis=0)

    # Get the normalized candidate vector sum
    candidate_vector_sum_normalized = candidate_vector_sum / len(candidate_file_list)

    # Plot the candidate vector sum
    plt.figure()
    plt.plot(candidate_vector_sum_normalized)
    plt.xlabel('Time (s)')
    plt.ylabel('Coverage')
    plt.title('Coverage of the candidate timebands')
    plt.show()

    title = 'candidate_coverage_of_timebands'
    output_file = './test_and_delete/temp_game_files/'+ title + '.png'
    plt.savefig(output_file)
    print(f"Chart saved to {output_file}")

    return None

if __name__ == '__main__':
    main()
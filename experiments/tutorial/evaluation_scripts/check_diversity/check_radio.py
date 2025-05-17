import logging, os
import pickle
import numpy as np
import random
import sys
import json
import matplotlib.pyplot as plt
import pandas as pd
from cornac.eval_methods import RatioSplit
from cornac.eval_methods.base_method import BaseMethod
from cornac.datasets import mind as mind
from cornac.metrics import Activation, Calibration, Fragmentation, Representation, AlternativeVoices
from tqdm.auto import tqdm
from collections import OrderedDict
from collections import defaultdict

logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["CUDA_VISIBLE_DEVICES"] = "2"


datasetname = "nemig" # change datasetname here

save_path = "your_folder_to_save_model_recommendation_results"   #'./experiment_{dataset_name}_drdw_results/{model_name}

file_path = os.path.join(save_path, "top20_recommendation.pkl")

with open(file_path, 'rb') as file:
    top20_recommendations = pickle.load(file)

# Load user history
with open('.combined_user_history.json', 'r') as file:
    user_item_history = json.load(file)

# Read path where the train uir and test uir are saved. For different models, the input files may be different
## Check the corresponding model experiment script.

feedback_train = mind.load_feedback(
    fpath="uir_impression_train.csv")

feedback_test = mind.load_feedback(
    fpath="uir_impression_test.csv")

mind_ratio_split = BaseMethod.from_splits(
    train_data=feedback_train,
    test_data=feedback_test,
    exclude_unknowns=False,
    verbose=True,
    rating_threshold=0.5
)

train_set = mind_ratio_split.train_set
test_set = mind_ratio_split.test_set
user_idx2id = {v: k for k, v in mind_ratio_split.global_uid_map.items()}


def get_user_rated_items(dataset):
    user_rated_items = defaultdict(list)
    uids, iids, ratings = dataset.uir_tuple

    for uid, iid, r in zip(uids, iids, ratings):
        if r > 0:
            user_rated_items[uid].append(iid)
    
    # Now, ensure all users are present
    unique_uids = set(uids)
    for uid in unique_uids:
        if uid not in user_rated_items:
            user_rated_items[uid] = []  # Assign empty list
            print(f"User {uid}, {user_idx2id[uid]}has no positive ratings.")

    return dict(user_rated_items)


def get_user_unclicked_items(dataset):
    # user_rated_items = defaultdict(list)
    user_rated_items = defaultdict(set)
    uids, iids, ratings = dataset.uir_tuple

    for uid, iid, r in zip(uids, iids, ratings):
        if r <= 0:
            user_rated_items[uid].add(iid)  # Add to set (ensures uniqueness)

    return user_rated_items

positive_ratings = get_user_rated_items(mind_ratio_split.test_set)
negative_ratings = get_user_unclicked_items(mind_ratio_split.test_set)

# Load item features
## Update the feature path
sentiment = mind.load_sentiment(fpath=f"./{datasetname}_results/sentiment.json")
category = mind.load_category(fpath=f"./{datasetname}_results/category.json")
complexity = mind.load_complexity(fpath=f"./{datasetname}_results/readability.json")
story = mind.load_story(fpath=f"./{datasetname}_results/story.json")
genre = mind.load_category_multi(fpath=f"./{datasetname}_results/category.json")
entities = mind.load_entities(fpath=f"./{datasetname}_results/party.json")
min_maj = mind.load_min_maj(fpath=f"./{datasetname}_results/min_maj_ratio.json")
entities_binary_count = mind.load_entities(fpath= f"./{datasetname}_results/entities_binary_count.json")
targetSize = 20

act = Activation(item_sentiment=sentiment, divergence_type='JS', k=targetSize)
cal_category = Calibration(item_feature=category, data_type="category", divergence_type='JS', k=targetSize)
cal_complexity = Calibration(item_feature=complexity, data_type="complexity", divergence_type='JS', k=targetSize)
frag = Fragmentation(item_story=story, n_samples=1, divergence_type='JS', k=targetSize)
alt_voices = AlternativeVoices(item_minor_major=min_maj, divergence_type='JS', k=targetSize)
rep = Representation(item_entities=entities, divergence_type='JS', k=targetSize)
rep_binary = Representation(item_entities = entities_binary_count, divergence_type='JS', k=targetSize)


def get_user_rated_items(dataset):
    user_rated_items = defaultdict(list)
    uids, iids, ratings = dataset.uir_tuple

    for uid, iid, r in zip(uids, iids, ratings):
        if r > 0:
            user_rated_items[uid].append(iid)
    
    # Now, ensure all users are present
    unique_uids = set(uids)
    for uid in unique_uids:
        if uid not in user_rated_items:
            user_rated_items[uid] = []  # Assign empty list
            print(f"User {uid}, {user_idx2id[uid]}has no positive ratings.")

    return dict(user_rated_items)

test_user_rated_dict = get_user_rated_items(mind_ratio_split.test_set)
train_user_rated_dict = get_user_rated_items(mind_ratio_split.train_set)

item_id2idx = {k: v for k, v in mind_ratio_split.global_iid_map.items()}
item_idx2id = {v: k for k, v in mind_ratio_split.global_iid_map.items()}
user_id2idx = {k: v for k, v in mind_ratio_split.global_uid_map.items()}
user_idx2id = {v: k for k, v in mind_ratio_split.global_uid_map.items()}


def get_gt_neg(test_set, train_pos_items, val_pos_items, test_pos_items):
    # Find the user rating for it
    u_gt_neg = np.ones(test_set.num_items, dtype='int')
    u_gt_neg[test_pos_items + val_pos_items + train_pos_items] = 0
    return u_gt_neg


def get_positive_items(csr_row, rating_threshold):
    return [
        item_idx
        for (item_idx, rating) in zip(csr_row.indices, csr_row.data)
        if rating >= rating_threshold
    ]

impression_items_list =  list(set(mind_ratio_split.test_set.uir_tuple[1]))
pool =  [item_idx2id[j] for j in impression_items_list]


def compute_user_radio(test_set, user_recommendations, user_history):
    Activation_dict = OrderedDict()
    Representation_dict = OrderedDict()
    Representation_binary_dict = OrderedDict()
    Calibration_category_dict =  OrderedDict()
    Calibration_complexity_dict = OrderedDict()
    Fragmentation_dict = OrderedDict()
    AltVoices_dict = OrderedDict()

    rating_threshold =0.5
    gt_mat = test_set.csr_matrix

    test_user_indices = set(mind_ratio_split.test_set.uir_tuple[0])
    for user_idx in tqdm(test_user_indices, desc="Radio Metric Computing", disable=True, miniters=100):
        test_pos_items = get_positive_items(gt_mat.getrow(user_idx), rating_threshold)

        if len(test_pos_items) == 0:
            continue
      
        if user_idx not in user_recommendations:
            print(f"missing recommendations:{user_idx}")
            continue
        elif len(user_recommendations[user_idx])==0:
            print(f"empty recommendations:{user_idx}")
            continue
     
        recomm = user_recommendations[user_idx]
        raw_item_ids = [item_idx2id[j] for j in recomm]
        user_history = user_item_history[user_idx2id[user_idx]]
        activation_value = act.compute(raw_item_ids, pool)
        calibration_cat_value = cal_category.compute(raw_item_ids, user_history)
        calibration_complexity_value = cal_complexity.compute(raw_item_ids, user_history)
        representation_value = rep.compute(raw_item_ids, pool)
        representation_binary_value = rep_binary.compute(raw_item_ids, pool)
        alt_voices_value = alt_voices.compute(raw_item_ids, pool)
        other_users = list(test_user_indices - {user_idx})  # Exclude user_idx

        # Filter only users present in user_recommendations
        other_users = [u for u in other_users if u in user_recommendations]

        # Sample a random user if there are valid options
        if other_users:
            sampled_user = random.choice(other_users)
            # print(f"Sampled user: {sampled_user}")
        else:
            print("No valid user found in user_recommendations")
        
        recomm_other_user = user_recommendations[sampled_user]
        raw_recomm_other_user = [item_idx2id[j] for j in recomm_other_user]
        fragmentation_value = frag.compute(raw_item_ids, [raw_recomm_other_user])
        Activation_dict[user_idx] = activation_value
        Representation_dict[user_idx] = representation_value
        Calibration_category_dict[user_idx] =  calibration_cat_value
        Calibration_complexity_dict[user_idx]  = calibration_complexity_value
        Fragmentation_dict[user_idx]  = fragmentation_value
        AltVoices_dict[user_idx] = alt_voices_value
        Representation_binary_dict[user_idx] = representation_binary_value

    return Activation_dict, Representation_dict,Representation_binary_dict,  Calibration_category_dict, Calibration_complexity_dict,Fragmentation_dict, AltVoices_dict

Activation_dict, Representation_dict,Representation_binary_dict, Calibration_category_dict, Calibration_complexity_dict,Fragmentation_dict, AltVoices_dict = compute_user_radio(test_set, top20_recommendations, user_item_history)

average_activation = np.mean(list(Activation_dict.values()))  # use values to compute the average
print(f"average_activation: {average_activation}")

valid_Representation_values = [value for value in Representation_dict.values() if value is not None]
average_representation= np.mean(valid_Representation_values)
print(f"average_representation: {average_representation}")

average_representation_binary= np.mean(list(Representation_binary_dict.values()))
print(f"average_representation_binary:{average_representation_binary}")

valid_cal_category  = [value for value in Calibration_category_dict.values() if value is not None] # some users don't have history
average_cal_category = np.mean(valid_cal_category)
print(f"average_cal_category: {average_cal_category}")

valid_cal_complexity  = [value for value in Calibration_complexity_dict.values() if value is not None] # some users don't have history
average_cal_complexity= np.mean(valid_cal_complexity)
print(f"average_cal_complexity: {average_cal_complexity}")

average_fragmentation = np.mean(list(Fragmentation_dict.values())) 
print(f"average_fragmentation: {average_fragmentation}")

average_alt_voices= np.mean(list(AltVoices_dict.values())) 
print(f"average_alt_voices: {average_alt_voices}")

# Save the averages into a dictionary
averages = {
    'average_activation': average_activation,
    'average_representation': average_representation,
    "average_representation_binary":average_representation_binary,
    'average_cal_category': average_cal_category,
    'average_cal_complexity':average_cal_complexity,
    'average_fragmentation':average_fragmentation,
    'average_alt_voices':average_alt_voices
}

# Save the averages to a JSON file
averages_file_path = os.path.join(save_path, "average_radio.json")
with open(averages_file_path, 'w') as f:
    json.dump(averages, f, indent=4)

print(f"Averages saved to {averages_file_path}")

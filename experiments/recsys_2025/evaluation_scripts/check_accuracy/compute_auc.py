import os
import pickle
import numpy as np
import random
import sys
import json
import os
import matplotlib.pyplot as plt
import pandas as pd
from cornac.eval_methods import RatioSplit
from tqdm.auto import tqdm
from collections import OrderedDict
from cornac.eval_methods.base_method import BaseMethod
from cornac.datasets import mind as mind
from collections import defaultdict
from tqdm import tqdm


save_path = "your_folder_to_save_model_recommendation_results"   #'./experiment_{dataset_name}_drdw_results/{model_name}

file_path = os.path.join(save_path, "item_scores.pkl")  
with open(file_path, 'rb') as file:
    item_scores = pickle.load(file)

dataset_name = 'nemig'

input_path = f'./{dataset_name}_results'
# Update the path for different dataset.
# input_path = './mind_results'
# input_path = './ebnerd_results'

# Read path where you saved article_pool items (raw ids) into a csv file, with a column named iid.
article_pool_path = os.path.join(input_path, "article_pool.csv")
impression_items_df = pd.read_csv(article_pool_path, dtype ={'iid': str})
impression_iid_list = impression_items_df['iid'].tolist()

# Read path where the train uir and test uir are saved. For different models, the input files may be different
# Check the corresponding model experiment script.
train_uir_path = os.path.join(input_path, 'uir_impression_train.csv')
feedback_train = mind.load_feedback(fpath = train_uir_path)

test_uir_path = os.path.join(input_path, 'uir_impression_test.csv')
feedback_test = mind.load_feedback(fpath = test_uir_path)

mind_ratio_split = BaseMethod.from_splits(train_data=feedback_train, test_data=feedback_test, exclude_unknowns=False,
        verbose=True,
        rating_threshold=0.5)

UID = mind_ratio_split.global_uid_map
IID = mind_ratio_split.global_iid_map

item_id2idx = {k: v for k, v in mind_ratio_split.global_iid_map.items()}
impression_items_list = []
for iid in impression_iid_list:
    if iid in item_id2idx:
        idx = item_id2idx[iid]
        impression_items_list.append(idx) # Item index in the cornac  internal indexing system

user_idx2id = {v: k for k, v in mind_ratio_split.global_uid_map.items()}


def get_user_rated_items(dataset):
    user_rated_items = defaultdict(list)
    uids, iids, ratings = dataset.uir_tuple

    for uid, iid, r in zip(uids, iids, ratings):
        if r > 0:
            user_rated_items[uid].append(iid)
    
    # Ensure all users are present
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

positive_users = set(positive_ratings.keys())
negative_users = set(negative_ratings.keys())


def compute_auc(user_predictions, positive_ratings, negative_ratings):
    """
    Computes AUC based on pairwise comparisons of positive and negative item scores.

    :param user_predictions: dict {user_idx: {item_idx: predicted_score}}
    :param positive_ratings: dict {user_idx: list of positively rated items}
    :param negative_ratings: dict {user_idx: list of negatively rated items}
    :return: AUC score
    """
    total_pairs = 0
    correct_pairs = 0

    user_prediction_counts = {}  # Stores per-user correct and incorrect counts
    test_users = list(positive_ratings.keys())
    
    for user in tqdm(test_users, desc="Processing Users", unit="user"):  # Add progress bar
        pos_items = positive_ratings.get(user, [])

        neg_items = negative_ratings.get(user, set())  # Get negative items, default to empty set
        if not pos_items or not neg_items:
            print(f"user {user} without both positive & negative items")
            continue  # Skip users without both positive & negative items
        
        user_correct = 0
        user_total = 0
        for pos_item in pos_items:
            index = impression_items_list.index(pos_item)
            pos_score = user_predictions[user][index]
            for neg_item in neg_items:
                # Get predicted scores
                index = impression_items_list.index(neg_item)
                neg_score = user_predictions[user][index]
                # Compare scores
                if pos_score > neg_score:
                    correct_pairs += 1
                    user_correct += 1
                
                user_total += 1
                total_pairs += 1

         # Store per-user counts
        user_prediction_counts[user] = {
            "correct_predictions": user_correct,
            "total_predictions": user_total
        }   

    return correct_pairs,  total_pairs, user_prediction_counts

correct_pairs,  total_pairs, user_prediction_counts = compute_auc(item_scores, positive_ratings, negative_ratings)

auc_score = correct_pairs / total_pairs if total_pairs > 0 else 0.0
print(f"correct_pairs: {correct_pairs}")
print(f"total_pairs: {total_pairs}")
print(f"AUC Score: {auc_score:.4f}")
print(f"Total users evaluated:{len(user_prediction_counts)}")

results = {
    "auc": auc_score,
    "total_pairs": total_pairs,
    "correct_pairs": correct_pairs,
    "user_prediction_counts": {str(k): v for k, v in user_prediction_counts.items()}
}

output_json = os.path.join(save_path, "auc_results.json")
with open(output_json, "w") as json_file:
    json.dump(results, json_file, indent=4)

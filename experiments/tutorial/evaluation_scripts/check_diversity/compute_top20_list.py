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

os.environ["CUDA_VISIBLE_DEVICES"] = "6"

save_path = "your_folder_to_save_model_recommendation_results"
file_path = os.path.join(save_path, "recommendations.pkl")

print(f"save_path:{save_path}")

with open(file_path, 'rb') as file:
    model_recommendations = pickle.load(file)

impression_items_df = pd.read_csv(
    "article_pool.csv", dtype ={'iid': str})
impression_iid_list = impression_items_df['iid'].tolist()

with open('combined_user_history.json', 'r') as file:
    user_history = json.load(file)

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

# Get the dictionary of users and the items they rated > 0
test_user_rated_dict = get_user_rated_items(mind_ratio_split.test_set)
train_user_rated_dict = get_user_rated_items(mind_ratio_split.train_set)

# print(train_user_rated_dict)

item_id2idx = {k: v for k, v in mind_ratio_split.global_iid_map.items()}
impression_items_list = []
for iid in impression_iid_list:
    if iid in item_id2idx:
        idx = item_id2idx[iid]
        impression_items_list.append(idx)

user_id2idx = {k: v for k, v in mind_ratio_split.global_uid_map.items()}

new_user_his_dict = {
    user_id2idx[user]: [item_id2idx[item] for item in items if item in item_id2idx]
    for user, items in user_history.items()
    if user in user_id2idx  # Ensure user exists in mapping
}


def get_positive_items(csr_row, rating_threshold):
    return [
        item_idx
        for (item_idx, rating) in zip(csr_row.indices, csr_row.data)
        if rating >= rating_threshold
    ]

impression_items_list =  list(set(mind_ratio_split.test_set.uir_tuple[1]))
new_ranked_list_top20 = {}

gt_mat = test_set.csr_matrix
train_mat = train_set.csr_matrix
rating_threshold =0.5

test_user_indices = set(mind_ratio_split.test_set.uir_tuple[0])
for user_idx in tqdm(test_user_indices, desc="Ranking", disable=True, miniters=100):
    test_pos_items = test_user_rated_dict[user_idx]
    
    train_pos_items = (
        get_positive_items(train_mat.getrow(user_idx), rating_threshold)
        if user_idx < train_mat.shape[0]
        else []
    )

    if len(test_pos_items) == 0:
            print(f"user:{user_idx} missing positives")
            continue

    if user_idx not in model_recommendations:
        print(f"missing recommendations:{user_idx}")
        continue
    elif len(model_recommendations[user_idx])==0:
        print(f"empty recommendations:{user_idx}")
        continue

    tp_fn = len(test_pos_items)
    if tp_fn ==0:
        continue

    recomm = model_recommendations[user_idx]
    
    # Step 1: Filter out items in train_pos_items
    filtered_recomm = [item for item in recomm if item not in train_pos_items]

    # Step 2: Further filter out items in new_user_his_dict[user_idx]
    filtered_recomm = [item for item in filtered_recomm if item not in user_history[user_idx]]

    # Step 3: Select the top 20 items
    top_20_items = filtered_recomm[:20]
    new_ranked_list_top20[user_idx] = top_20_items

pickle_file_path = os.path.join(save_path, "top20_recommendation.pkl")

# Save the dictionary as a pickle file
with open(pickle_file_path, 'wb') as f:
    pickle.dump(new_ranked_list_top20, f)

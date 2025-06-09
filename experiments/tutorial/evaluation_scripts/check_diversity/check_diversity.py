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
from cornac.metrics import ILD, GiniCoeff
from tqdm.auto import tqdm
from collections import OrderedDict
from collections import defaultdict

save_path = "your_folder_to_save_model_recommendation_results"   #'./experiment_{dataset_name}_drdw_results/{model_name}
datasetname = "nemig" # change datasetname here
print(f"save_path:{save_path}")
file_path = os.path.join(save_path, "top20_recommendation.pkl")

with open(file_path, 'rb') as file:
    model_recommendations = pickle.load(file)

impression_items_df = pd.read_csv(
    "article_pool.csv", dtype ={'iid': str})
impression_iid_list = impression_items_df['iid'].tolist()
# Get the length of recommendation list for each user
recommendation_lengths = [len(recs) for recs in model_recommendations.values()]

with open('combined_user_history.json', 'r') as file:
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

# Load item feature
sentiment = mind.load_sentiment(fpath=f"./{datasetname}_results/sentiment.json")
category = mind.load_category(fpath=f"./{datasetname}_results/category.json")
complexity = mind.load_complexity(fpath=f"./{datasetname}_results/readability.json")
genre = mind.load_category_multi(fpath=f"./{datasetname}_results/category.json")

min_maj = mind.load_min_maj(fpath=f"./{datasetname}_results/min_maj_ratio.json")
sentiment_one_hot_encoded_vectors = mind.load_encoding_vectors(fpath=f"./{datasetname}_results/sentiment_vectors.json") # sentiment one-hot vectors by range
party_one_one_hot_encoded_vectors = mind.load_encoding_vectors(fpath=f"./{datasetname}_results/party_vectors.json")# party one-hot vectors by party classification
Item_sentiment = mind.build(data=sentiment, id_map=mind_ratio_split.global_iid_map)
Item_category = mind.build(data=category, id_map=mind_ratio_split.global_iid_map)
Item_complexity = mind.build(data=complexity, id_map=mind_ratio_split.global_iid_map)

Item_min_major = mind.build(data=min_maj, id_map=mind_ratio_split.global_iid_map)
Item_genre = mind.build(data=genre, id_map=mind_ratio_split.global_iid_map)
Item_feature = Item_genre
Item_senti_vec = mind.build(data=sentiment_one_hot_encoded_vectors, id_map=mind_ratio_split.global_iid_map)
Item_party_vec = mind.build(data=party_one_one_hot_encoded_vectors, id_map=mind_ratio_split.global_iid_map)
ild_cat = ILD(name="cat_ILD", item_feature=Item_feature, k=20)
ild_senti = ILD(name="senti_ILD", item_feature=Item_senti_vec, k=20)
ild_party = ILD(name="party_ILD", item_feature=Item_party_vec, k=20)
gini_cat = GiniCoeff(name="cat_gini", item_genre=Item_genre, k=20)
gini_senti = GiniCoeff(name="senti_gini", item_genre=Item_senti_vec, k=20)
gini_party = GiniCoeff(name="party_gini", item_genre=Item_party_vec, k=20)

item_id2idx = {k: v for k, v in mind_ratio_split.global_iid_map.items()}
impression_items_list = []
for iid in impression_iid_list:
    if iid in item_id2idx:
        idx = item_id2idx[iid]
        impression_items_list.append(idx)

print(f"len impression_items_list:{len(impression_items_list)}")

user_id2idx = {k: v for k, v in mind_ratio_split.global_uid_map.items()}
new_user_his_dict = {
    user_id2idx[user]: [item_id2idx[item] for item in items if item in item_id2idx]
    for user, items in user_item_history.items()
    if user in user_id2idx  # Ensure user exists in mapping
}

impression_items_list =  list(set(mind_ratio_split.test_set.uir_tuple[1]))
new_ranked_list_top20 = {}


def compute_user_diversity(test_set, train_set, user_recommendations):
    Gini_category_dict = OrderedDict()
    Gini_senti_dict = OrderedDict()
    Gini_party_dict = OrderedDict()
    ILD_senti_dict = OrderedDict()
    ILD_party_dict = OrderedDict()
    ILD_category_dict = OrderedDict()
    
    test_user_indices = set(mind_ratio_split.test_set.uir_tuple[0])
    for user_idx in tqdm(test_user_indices, desc="Diversity", disable=True, miniters=100):

        pos_items = positive_ratings.get(user_idx, [])
        neg_items = negative_ratings.get(user_idx, set())  # Get negative items, default to empty set

        if not pos_items or not neg_items:
            print(f"user {user_idx} without both positive & negative items")
            continue  # Skip users without both positive & negative items

        recomm = user_recommendations[user_idx]
        
        ILD_category_dict[user_idx] = ild_cat.compute(recomm)
        ILD_party_dict[user_idx] = ild_party.compute(recomm)
        ILD_senti_dict[user_idx] = ild_senti.compute(recomm)

        Gini_category_dict[user_idx] = gini_cat.compute(recomm)
        Gini_senti_dict[user_idx] = gini_senti.compute(recomm)
        Gini_party_dict[user_idx]= gini_party.compute(recomm)
        
        # Recalldict[user_idx] = sum(recall_list)/len(recall_list)
        
    return Gini_category_dict, Gini_senti_dict, Gini_party_dict,ILD_senti_dict,ILD_party_dict, ILD_category_dict

Gini_category_dict, Gini_senti_dict, Gini_party_dict,ILD_senti_dict,ILD_party_dict, ILD_category_dict = compute_user_diversity(test_set, train_set, model_recommendations)

average_gini_cat = np.mean(list(Gini_category_dict.values()))  # use values to compute the average
average_gini_senti = np.mean(list(Gini_senti_dict.values()))
average_gini_party = np.mean(list(Gini_party_dict.values()))

average_ild_cat = np.mean(list(ILD_category_dict.values())) 
average_ild_senti = np.mean(list(ILD_senti_dict.values())) 
average_ild_party = np.mean(list(ILD_party_dict.values())) 

print(f"average_gini_cat: {average_gini_cat}")
print(f"average_gini_senti: {average_gini_senti}")
print(f"average_gini_party: {average_gini_party}")
print(f"average_ild_cat: {average_ild_cat}")
print(f"average_ild_senti: {average_ild_senti}")
print(f"average_ild_party: {average_ild_party}")

# Save the averages into a dictionary
averages = {
    'average_gini_cat': average_gini_cat,
    'average_gini_senti': average_gini_senti,
    'average_gini_party': average_gini_party,
    'average_ild_cat':average_ild_cat,
    'average_ild_senti':average_ild_senti,
    'average_ild_party':average_ild_party
}

# Save the averages to a JSON file
averages_file_path = os.path.join(save_path, "average_diversity_ild_gini.json")
with open(averages_file_path, 'w') as f:
    json.dump(averages, f, indent=4)

print(f"Averages saved to {averages_file_path}")

import cornac
from cornac.eval_methods import BaseMethod
from cornac.models import EPD
from cornac.metrics import Recall

import pandas as pd
import os
import json
import random
import sys

import logging, os
logging.disable(logging.WARNING)

# The example script shown here is for the specific example of MIND
# Change the import, name, and path to accomodate different datasets
# Available options are: "mind", "nemig", "ebnerd"
from cornac.datasets import mind
dataset_name = 'mind'
input_path = f'./{dataset_name}_results'

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
config_files_dir = os.path.join(current_dir, 'configs')
sys.path.insert(0, config_files_dir)

train_uir_path = os.path.join(input_path, 'uir_impression_train.csv')
feedback_train = mind.load_feedback(fpath = train_uir_path)

test_uir_path = os.path.join(input_path, 'uir_impression_test.csv')
feedback_test = mind.load_feedback(fpath = test_uir_path)

article_pool_path = os.path.join(input_path, 'article_pool.csv')
impression_items_df = pd.read_csv(article_pool_path, dtype ={'iid': str})
impression_iid_list = impression_items_df['iid'].tolist()

political_ref_path =  os.path.join(input_path, 'political_reference_epd.json')
party_input_path = input_path

# For EB-Nerd and Nemig, load the converted party file (refer to PLD_EPD_preparation folder)
# For Mind, load the raw party file: 'party.json'
party_path =  os.path.join(party_input_path, 'converted_party.json')
config_path  = os.path.join(config_files_dir, 'model_parameters.ini') 
    
ratio_split = BaseMethod.from_splits(
    train_data = feedback_train,
    test_data = feedback_test,
    exclude_unknowns = False,
    verbose = True,
    rating_threshold=0.5)

political_type_dict = {1: 'neutral', 2:'major', 3:'minor'}
num_items = len(set([i for u,i,r in feedback_train]))
test_uir = list(zip(*ratio_split.test_set.uir_tuple))


def load_user_group_type(uir):
    # Unique user IDs
    uid_set = set(uid for uid, _, _ in uir)
    uid_list = list(uid_set)
    # print(f"len user ids list:{uid_list}")
    
    # Shuffle for randomness
    random.shuffle(uid_list)
    
    total_users = len(uid_list)
    group_size = total_users // 3

    print(f"group_size average:{group_size}")
    
    # Split into 3 groups
    group1 = uid_list[:group_size]
    group2 = uid_list[group_size:2*group_size]
    group3 = uid_list[2*group_size:3*group_size]
    
    # Handle remainder users
    remainder = uid_list[3*group_size:]
    groups = {1: group1, 2: group2, 3: group3}
    choices = [1, 2, 3]
    
    for uid in remainder:
        group_choice = random.choice(choices)
        groups[group_choice].append(uid)
    print(f"groups len: {len(groups[1])}, {len(groups[2])}, {len(groups[3])}")
    
    # Build user_id to group_id mapping
    user_group_dict = {}
    for group_id, users in groups.items():
        for uid in users:
            user_group_dict[uid] = group_id
    
    return user_group_dict


user_group_dict = load_user_group_type(test_uir)
cleaned_dict = {int(k): v for k, v in user_group_dict.items()}

user_group_save_path = os.path.join(input_path, 'epd_user_groups.json')  # save user groups

with open(user_group_save_path, 'w') as f:
    json.dump(cleaned_dict, f, indent=4)

# Initialize models
model = EPD( 
    name = f"EPD_{dataset_name}",
    party_path = party_path, 
    political_type_dict = political_type_dict, 
    num_items = num_items, 
    configure_path = config_path,
    k = 2, 
    pageWidth = 20,
    article_pool = impression_iid_list, 
    userGroupDict = user_group_dict, 
    dataset_name = dataset_name , 
    political_ref_path = political_ref_path)

# Define metrics to evaluate the models...
metrics = [ Recall(k=20)]

# ...put it together in an experiment, voilà!
experiment_output_path = f'./experiment_{dataset_name}_epd_results'
cornac.Experiment(
        eval_method = ratio_split,
        models = [model],
        metrics = metrics,
        save_dir = experiment_output_path
    ).run()

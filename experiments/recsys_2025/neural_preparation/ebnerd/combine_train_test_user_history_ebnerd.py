import sys
import pandas as pd
import numpy as np
import json
import os

import sys

input_folder =  './ebnerd_input'

# Step 1: Load EB-NERD dataset
articles_path = os.path.join(input_folder, 'articles.parquet')
train_behaviors_path = os.path.join(input_folder, 'behaviors-train.parquet')
train_history_path = os.path.join(input_folder, 'history-train.parquet')
val_behaviors_path = os.path.join(input_folder, 'behaviors-val.parquet')
val_history_path = os.path.join(input_folder, 'history-val.parquet')

articles_df = pd.read_parquet(articles_path)
train_behaviors_df = pd.read_parquet(train_behaviors_path)
train_history_df = pd.read_parquet(train_history_path)
val_behaviors_df = pd.read_parquet(val_behaviors_path)
val_history_df = pd.read_parquet(val_history_path)


dataset_result_folder =  './ebnerd_results'
incompelete_article_path = os.path.join(dataset_result_folder, "incomplete_article_ids.txt")
with open(incompelete_article_path, "r") as file:
    incomplete_ids = [line.strip() for line in file if line.strip()]

incomplete_ids_set = set(incomplete_ids)
print(f" len incomplete_ids_set:{len(incomplete_ids_set)}")

# Step 2: Initialize user history dictionary
user_history_dict_train = {}

## Part 3A - Training Set
# Step 3: Go through each user group
for user_id, group in train_history_df.groupby('user_id'):
    all_articles = []

    # Collect all articles for the user
    for article_list in group['article_id_fixed']:
        all_articles.extend(article_list)

    # Step 4: Filter out incomplete articles
    filtered_articles = [article for article in all_articles if article not in incomplete_ids_set]

    # Step 5: Remove duplicates while preserving order
    unique_articles = list(dict.fromkeys(filtered_articles))

    # Step 6: Add to dictionary
    if unique_articles:  # If there are valid articles, add them
        user_history_dict_train[user_id] = unique_articles
    else:  # If no valid articles, still add the user but with an empty list
        user_history_dict_train[user_id] = []

# Convert np.int32 values to regular str
user_history_dict_converted_train = {key: [str(value) for value in val] for key, val in user_history_dict_train.items()}
user_history_dict = {}

## Part 3B - Validation Set
# Step 3: Go through each user group
for user_id, group in val_history_df.groupby('user_id'):
    all_articles = []
    for article_list in group['article_id_fixed']:
        all_articles.extend(article_list)

    # Step 4: Filter out incomplete articles
    filtered_articles = [article for article in all_articles if article not in incomplete_ids_set]

    # Step 5: Remove duplicates while preserving order
    unique_articles = list(dict.fromkeys(filtered_articles))

    # Step 6: Add to dictionary
    if unique_articles:  
        user_history_dict[user_id] = unique_articles

user_history_dict_converted_val = {key: [str(value) for value in val] for key, val in user_history_dict.items()}

# Step 7: Training and combinination
# Start with train users
combined_user_history = user_history_dict_converted_train.copy()

# Add users from test who are not already in train
for user, history in user_history_dict_converted_val.items():
    if user not in combined_user_history:
        combined_user_history[user] = history

print(f"Total users in combined history: {len(combined_user_history)}")


## Save user -item -history json file.
output_file_path = os.path.join(dataset_result_folder,  "combined_user_history.json")


with open(output_file_path, 'w') as file:
    json.dump(combined_user_history, file, indent=4)

import pickle
import pandas as pd
import time
import json
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
from cornac.datasets import mind as mind
import os
import sys


# For Mind and NeMig datasets, update the path to the corresponding {datasetname_results} folder
dataset_result_folder =  './nemig_results'
# Load precomputed embeddings for Mind and NeMig datasets
saved_emb_path = os.path.join(dataset_result_folder,  "news_embeddings.pkl")
with open(saved_emb_path, "rb") as f:
    embedding = pickle.load(f)  # Load the dictionary


# ----------------------------------------
# For EB-Nerd dataset: load the article embeddings provided by the dataset.
# Uncomment and update paths as needed
# input_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ebnerd_input')
# articles_emb_path =  os.path.join(input_folder, 'xlm_roberta_base.parquet')
# articles_df_raw = pd.read_parquet(articles_emb_path)
# print(articles_df_raw.dtypes)
# embedding = articles_df_raw.rename(columns={'article_id': 'id', 'FacebookAI/xlm-roberta-base': 'embedding'})
# embedding['id'] = embedding['id'].astype(str)
# embedding['embedding'] = embedding['embedding'].apply(lambda x: x.tolist())



print(type(embedding))  # Check if it's a pandas Series
print(embedding.head())  # See the first few rows
print(embedding.shape)  # Check the total number of embeddings
print(embedding.columns)  # Check actual column names

start_time = time.time()

### Load the impression U-I-R csv file.
train_imp_uir_path = os.path.join(dataset_result_folder,  "uir_impression_train.csv")
feedback_train = mind.load_feedback( fpath = train_imp_uir_path)
print(f"Total uir in feedback_train: {len(feedback_train)}")
print(f"feedback_train head 5: {feedback_train[:5]}")

test_imp_uir_path = os.path.join(dataset_result_folder,  "uir_impression_test.csv")
feedback_test = mind.load_feedback(fpath = test_imp_uir_path)
print(f"Total uir in feedback_test: {len(feedback_test)}")

## Part 1 - Data Preparation
# Load combined history from a JSON file
history_file_path = os.path.join(dataset_result_folder,  "combined_user_history.json")
with open(history_file_path, 'r') as file:
    user_item_history = json.load(file)

# Step 1: Find all items rated as 1 in feedback_train
# Create a set of items that have been rated as 1 at least once.
rated_items_train = {item for user, item, rating in feedback_train if rating > 0}
print(f"len clicked items in train impression:{len(rated_items_train)}")

# Step 2: Find items appearing in at least one training user's history
train_users = {user for user, _, _ in feedback_train}  # Extract user IDs in training set
print(f"len train_users:{len(train_users)}")
items_in_train_history = set()
for user in train_users:
    if user in user_item_history:
        items_in_train_history.update(user_item_history[user])
print(f"len items_in_train_history:{len(items_in_train_history)}")

# Step 3: Find items appearing in at least one test user's history
test_users = {user for user, _, _ in feedback_test}  # Extract user IDs in test set
items_in_test_history = set()
for user in test_users:
    if user in user_item_history:
        items_in_test_history.update(user_item_history[user])
print(f"len items_in_test_history:{len(items_in_test_history)}")

# Find all items already on the graph (train impression clicked, history, test history) 
final_item_set = rated_items_train | items_in_train_history | items_in_test_history
print(f"Total known items on the graph: {len(final_item_set)}")

# Extract all unique items in feedback_test and count the number of new items that do not appear in final_item_set:
unique_items_test = {item for _, item, _ in feedback_test}

# Find new items (items in test set but not in final_item_set)
new_items = [item for item in unique_items_test if item not in final_item_set]

# Count the number of new items
num_new_items = len(new_items)
print(f"Total unique items in feedback_test: {len(unique_items_test)}")
print(f"Total new items not on the graph : {num_new_items}")

# Compute the closest item for each new item (from new_items) in final_item_set based on cosine similarity using embedding
# `new_items` is the set of new item IDs
# `final_item_set` is the set of known item IDs

embedding.set_index("id", inplace=True)  
new_items = set(new_items)  # set for fast lookup
final_item_set = set(final_item_set)

# Filter embeddings only for final item set
valid_final_mask = embedding.index.isin(final_item_set)
filtered_final_ids = embedding.index[valid_final_mask].tolist()
filtered_final_embeddings = np.vstack(embedding.loc[valid_final_mask, "embedding"].apply(np.array).tolist())

print(f"Shape of filtered_final_embeddings: {filtered_final_embeddings.shape}")
assert filtered_final_embeddings.shape[0] == len(filtered_final_ids), "Mismatch between extracted embeddings and final_item_set!"

TopN = 3
closest_items = {}
embedding_ids = set(embedding.index)  
for new_item in tqdm(new_items, desc="Finding top N closest items"):
    if new_item not in embedding_ids:
        continue  
    
    new_item_embedding = np.array(embedding.loc[new_item, "embedding"]).reshape(1, -1)

    similarities = cosine_similarity(new_item_embedding, filtered_final_embeddings).flatten()

    topN_indices = np.argsort(similarities)[-TopN:][::-1]

    topN_item_ids = [filtered_final_ids[idx] for idx in topN_indices]
    closest_items[new_item] = topN_item_ids

print(f"Computed closest items for {len(closest_items)} new items.")
print(list(closest_items.items())[:10])

## Part 2 - Data Transformation
# Step 1: Include all (u-i-r) tuples from feedback_train that user clicked
new_feedback = []
# Create a new [(u, i,r)]
for user, item, rating in feedback_train:
    if rating > 0:
        new_feedback.append((user, item, 1))

# Step 2: Expand history for train users
train_users = {user for user, _, _ in feedback_train}  # Extract users from training set
for user in train_users:
    if user in user_item_history:  # Ensure user has a history
        for item in user_item_history[user]:  # Iterate through the user's history
            new_feedback.append((user, item, 1))  # Assign rating 1

    else:
        print(f"missing train user {user} history" )

# Step 3: Expand history for test users
test_users = {user for user, _, _ in feedback_test}  # Extract users from test set
for user in test_users:
    if user in user_item_history:  # Ensure user has a history
        for item in user_item_history[user]:  # Iterate through the user's history
            new_feedback.append((user, item, 1))  # Assign rating 1
    else:
        print(f"missing test user {user} history" )

# Drop duplicates
new_feedback = list(set(new_feedback))

## Part 3 - Data Augmentation
# Step 1: Propagate user interactions from an item’s closest known item to the corresponding new item.
# Extract users who rated each closest_items[new_item] as 1.
# Build a mapping from items to users who rated them as 1
item_to_users = {}  # key = item_id, value = set(users)
for user, item, rating in new_feedback:  
    if rating >0 :  # We only care about positive ratings
        if item not in item_to_users:
            item_to_users[item] = set()
        item_to_users[item].add(user) 

## Step 2: Propagate user behavior to new items.
## For each new_item, find its closest item in final_item_ids.
## Look up users who rated that closest item as 1.
## Assign those users to rate new_item as 1.
for new_item, closest_item_all in closest_items.items(): 
    for closest_item in  closest_item_all:
        if closest_item in item_to_users:  # Ensure the closest item has ratings
            users_who_rated_closest = item_to_users[closest_item]  # Get users who rated closest_item as 1
            for user in users_who_rated_closest:
                new_feedback.append((user, new_item, 1))
        else:
            assert closest_item in final_item_set, f"Closest item {closest_item} should be in final_item_set but isn't."
            print(f"Closest item {closest_item} not found in item_to_users. Skipping {new_item}.")

## Drop duplicates
augmented_behavior = list(set(new_feedback))

elapsed_time = time.time() - start_time
print(f"\nCompleted computation in {elapsed_time:.2f} seconds.")
print(f"Total augmented u-i-r tuples: {len(augmented_behavior)}")
print("Sample tuples:", augmented_behavior[:10])  # Print a few examples

# Save augmented U-I-R for graph-based recommendation models.
output_csv_path = os.path.join(dataset_result_folder, f'augmented_uir_top{TopN}similar.csv')
df_augmented = pd.DataFrame(augmented_behavior, columns=["UserID", "ItemID", "Rating"])


df_augmented.to_csv(output_csv_path, index=False)

print(f"Saved augmented feedback to {output_csv_path}")

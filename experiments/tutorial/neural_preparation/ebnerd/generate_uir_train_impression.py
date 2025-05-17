import pandas as pd
import os
from tqdm import tqdm

input_folder = './ebnerd_input'

# Load EB-NERD dataset
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

# Prepare train user-item-rating file.
user_item_rating = []

# Group by user and add tqdm for progress bar
for user_id, user_df in tqdm(train_behaviors_df.groupby('user_id'), desc="Processing users", total=len(train_behaviors_df['user_id'].unique())):
    # Collect all articles in impressions (excluding invalid items)
    all_impressions = set()
    clicked_articles = set()
    
    for idx, row in user_df.iterrows():
        # Assume article_ids_impression and article_ids_clicked are lists or strings of lists
        impressions = row['article_ids_inview']
        clicks = row['article_ids_clicked']
        
        # Exclude invalid items from impressions
        impressions_clean = [item for item in impressions if item not in incomplete_ids_set]
        all_impressions.update(impressions_clean)
        
        # Exclude invalid items from clicked articles
        clicks_clean = [item for item in clicks if item not in incomplete_ids_set]
        clicked_articles.update(clicks_clean)

    # Now assign ratings and avoid duplicates in user_item_rating
    for article in all_impressions:
        rating = 1 if article in clicked_articles else 0
        # Avoid duplicates in the user_item_rating list
        if (user_id, article, rating) not in user_item_rating:
            user_item_rating.append((user_id, article, rating))

    # Ensure clicked articles are added with rating 1 (if not already added)
    for article in clicked_articles:
        if (user_id, article, 1) not in user_item_rating:
            user_item_rating.append((user_id, article, 1))

# Save to CSV
output_file_path = os.path.join(dataset_result_folder,  "uir_impression_train.csv")
result_df = pd.DataFrame(user_item_rating, columns=['UserID', 'ItemID', 'Rating'])
result_df.to_csv(output_file_path, index=False)


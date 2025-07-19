import pandas as pd
import os
from tqdm import tqdm

import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

input_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ebnerd_input')

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

required_columns = ['article_id', 'title', 'subtitle','body','article_type', 'published_time','ner_clusters', 'entity_groups', 'topics', 'category','category_str']


def combine_title_and_subtitle(row):
    
    # Clean title and subtitle, handle 'null' and empty strings
    title = row["title"]
    subtitle = row["subtitle"]

    # Define a cleaner function
    def clean(text):
        if pd.isnull(text):
            return ""
        text = str(text).strip()
        return "" if text.lower() == "null" else text

    title_clean = clean(title)
    subtitle_clean = clean(subtitle)

    # Combine if both exist
    if title_clean and subtitle_clean:
        return f"{title_clean}: {subtitle_clean}"
    elif title_clean:
        return title_clean
    else:
        # Subtitle only, or empty if both are empty
        return subtitle_clean

articles_df["new_title"] = articles_df.apply(combine_title_and_subtitle, axis=1)


# Check if a value is missing
def is_missing(value):
    return (
        pd.isnull(value)
        or (isinstance(value, str) and value.strip().lower() in ["", "null", "none", "nan"])
    )


# Check if a row is incomplete
def is_incomplete(row):
    return (
        is_missing(row["published_time"])
        or is_missing(row["body"])
        or is_missing(row["new_title"])
        or is_missing(row["category_str"])
        or is_missing(row["article_id"])
    )

incomplete_articles = articles_df[articles_df.apply(is_incomplete, axis=1)]
print(f"Found {len(incomplete_articles)} incomplete articles.")

incomplete_ids = incomplete_articles['article_id'].tolist()
print("Incomplete article IDs:")
print(incomplete_ids)
print(f"Len incomplete articles:{len(incomplete_ids)}")

# Prepare for the cleaned article data
# Remove rows where 'article_id' is in incomplete_ids
articles_df = articles_df[~articles_df['article_id'].isin(incomplete_ids)]
print(f"Remaining rows: {len(articles_df)}")

# Create the new DataFrame with correct mappings
articles_df = articles_df.drop(columns=['title', 'category'], errors='ignore')
new_df = articles_df.rename(columns={
    'article_id': 'id',
    'new_title': 'title',
    'body': 'text',
    'published_time': 'date',
    'category_str': 'category'  
})[['id', 'title', 'text', 'date', 'category']]

print(new_df.head())
print(f"len cleaned EB_Nerd articles: {len(new_df)}")

output_folder = './ebnerd_results'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Save the cleaned articles to csv file. change the output path.
output_cleaned_article_path = os.path.join(output_folder, "cleaned_articles.csv")
new_df.to_csv(output_cleaned_article_path, index=False)

incomplete_ids_path = os.path.join(output_folder, "incomplete_article_ids.txt")
# Save the removed article ids to text. change the output path.
with open(incomplete_ids_path, 'w') as f:
    for article_id in incomplete_ids:
        f.write(f"{article_id}\n")

import pandas as pd
import os
from tqdm import tqdm
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

input_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mind_input')

# Load MIND
articles_path = os.path.join(input_folder, 'news.csv')

df_news = pd.read_csv(articles_path)  
# Some news articles lack body text information (e.g., videos)
# missing_count = df["body"].isna().sum()

# Filter rows where "text" is NaN or empty (including spaces)
empty_text_rows = df_news[df_news["body"].isna() | (df_news["body"].str.strip() == "")]

incomplete_ids = empty_text_rows["news_id"].tolist()
print(f"Len incomplete articles:{len(incomplete_ids)}")

### Please ensure each article contains the required fields for data enrichment:
### - id
### - title
### - text (body)
### - date (publication time)
### - category
### Articles missing any of these fields will be considered incomplete and need to be added to incomplete_ids.

# Remove the incomplete rows from df_news
mask = ~(df_news["body"].isna() | (df_news["body"].str.strip() == ""))
df_news = df_news[mask].reset_index(drop=True)

# After validating article completeness, remove invalid rows and rename columns
df_news = df_news.rename(columns={
    'news_id': 'id',
    'new_title': 'title',
    'body': 'text',
    'published_time': 'date',
    'category': 'category'
    })[['id', 'title', 'text', 'date', 'category']]

# Save the cleaned article CSV
output_folder = './mind_results'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

output_cleaned_article_path = os.path.join(output_folder, "cleaned_articles.csv")
df_news.to_csv(output_cleaned_article_path, index=False)

incomplete_ids_path = os.path.join(output_folder, "incomplete_article_ids.txt")

# Save the removed article IDs to text
with open(incomplete_ids_path, 'w') as f:
    for article_id in incomplete_ids:
        f.write(f"{article_id}\n")

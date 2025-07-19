import pandas as pd
import os
from tqdm import tqdm
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


input_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'nemig_input')


# load NeMig dataset
# Load the CSV file (convert nemig dataset from .nt file to .csv file first)
import pandas as pd
metadata_path = os.path.join(input_folder, 'nemig_de_complete-instances_metadata_literals.csv')
column_names = ['News', 'Schema',  'Data']
df_metadata = pd.read_csv(metadata_path, sep=',', header = None, names=column_names)

#### Process publish date
# Step 1: Filter and copy
published_df = df_metadata[df_metadata['Schema'].str.contains('datePublished', na=False)].copy()

# Step 2: Extract news_id
published_df['news_id'] = published_df['News'].str.extract(r'resource/(news_\d+)')


# Step 3: Clean the date (remove trailing dot and space)
published_df['clean_date'] = published_df['Data'].str.replace(r'\s*\.\s*$', '', regex=True)

# Step 4: Parse to datetime
published_df['parsed_date'] = pd.to_datetime(
    published_df['clean_date'],
    format='%d.%m.%Y',
    errors='coerce'
)

# Step 5: Drop rows with missing info
valid_df = published_df.dropna(subset=['news_id', 'parsed_date'])

# Step 6: Create final dictionary
news_date_dict = dict(zip(valid_df['news_id'], valid_df['parsed_date'].dt.date))

print(news_date_dict)


################# Import body text ###################################
body_path = os.path.join(input_folder, 'nemig_de_complete-instances_content_literals.txt')
data = []

with open(body_path, 'r', encoding='utf-8') as f:
    for line in f:
        # Split only on the first 2 commas
        parts = line.strip().split(',', maxsplit=2)

        if len(parts) == 3:
            subject = parts[0].strip('<>')
            schema = parts[1].strip('<>')
            value = parts[2].strip()

            # Remove trailing dot and any stray quotes
            if value.endswith('.'):
                value = value[:-1].strip()

            # Strip quotes around literal value
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1].strip()

            data.append({
                'News': subject,
                'Schema': schema,
                'Data': value
            })

df = pd.DataFrame(data)

# Extract `news_id`, `type`, and `id` from the News column
df[['type', 'id']] = df['News'].str.extract(r'news_(title|abstract|body)_(\d+)', expand=True)
df['news_id'] = 'news_' + df['id']

# Pivot table to group by news_id and have separate columns for title/abstract/body
pivot_df = df.pivot_table(index='news_id',
                          columns='type',
                          values='Data',
                          aggfunc='first').reset_index()


# Fill title field: combine title + abstract as requested
def is_valid(val):
    return pd.notna(val) and str(val).strip() != ''

def build_title(row):
    title = row.get('title')
    abstract = row.get('abstract')

    valid_title = is_valid(title)
    valid_abstract = is_valid(abstract)

    if valid_title and valid_abstract:
        return title.strip() + ' ' + abstract.strip()
    elif valid_title:
        return title.strip()
    elif valid_abstract:
        return abstract.strip()
    else:
        invalid_items.append(row.name)
        print(f"Missing title and abstract for {row.name}")
        return None

invalid_items = []

# Apply title creation logic
pivot_df['title'] = pivot_df.apply(build_title, axis=1)

# Keep only required columns
final_df = pivot_df[['news_id', 'title', 'body']]


print(final_df.head())
################# Get Category ###################################

import re

# Function to parse the text and extract news_id and category_id
def parse_news_articles(file_path):
    # List to hold parsed results
    parsed_data = []

    # Open the file and read line by line
    with open(file_path, 'r') as file:
        for line in file:
            # Use regular expressions to extract the necessary parts
            news_id_match = re.search(r'<http://nemig_de.org/resource/(news_\d+)>', line)
            category_id_match = re.search(r'<http://nemig_de.org/resource/news_topic_([^>]+)>', line)

            # If both matches are found, extract and store them
            if news_id_match and category_id_match:
                news_id = news_id_match.group(1)  # Extract 'news_xx'
                category_id = category_id_match.group(1)  # Extract 'news_topic_xx' or 'news_topic_-1'
                parsed_data.append({'news_id': news_id, 'category_id': category_id})

    return parsed_data

# Example usage
topic_file_path = os.path.join(input_folder, 'nemig_de_complete-instances_subtopic_mapping.txt')  # Path to your input file
parsed_articles = parse_news_articles(topic_file_path)

# Print parsed results
for article in parsed_articles:
    print(f"News ID: {article['news_id']}, Category ID: {article['category_id']}")

####################### Merge required data for data enrichment #############################
clean_df = final_df.rename(columns={
    'news_id': 'id',
    'body': 'text'
})

category_df = pd.DataFrame(parsed_articles)
## keep string as the category name
clean_df = clean_df.merge(category_df.rename(columns={'news_id': 'id', 'category_id': 'category'}), on='id', how='left')

clean_df['date'] = clean_df['id'].map(news_date_dict)
clean_df = clean_df[['id', 'title', 'text', 'category', 'date']]

####################### Clean data, check if a row is incomplete #############################

# Replace empty strings with NaN for consistent checking
clean_df.replace('', pd.NA, inplace=True)

# Find rows with any missing or invalid data
invalid_rows = clean_df[clean_df.isna().any(axis=1)]

print(f"Found {len(invalid_rows)} incomplete articles.")
incomplete_ids = invalid_rows['id'].tolist()
print("Incomplete article IDs:")
print(incomplete_ids)


### For NeMig, we found all rows required data exist.

##### Save results

output_folder = './nemig_results'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

output_cleaned_article_path = os.path.join(output_folder, "cleaned_articles.csv")
# Save to CSV
clean_df.to_csv(output_cleaned_article_path, index=False, encoding='utf-8')

print(f"clean news data is saved to {output_cleaned_article_path}")


# save the removed article ids to text. change the output path.
incomplete_ids_path = os.path.join(output_folder, "incomplete_article_ids.txt")
with open(incomplete_ids_path, 'w') as f:
    for article_id in incomplete_ids:
        f.write(f"{article_id}\n")


##  Save title json for later usage
id_title_dict = dict(zip(clean_df['id'], clean_df['title']))


import json
# Save to JSON
output_id_to_title_path = os.path.join(output_folder, "id_to_title.json")
with open(output_id_to_title_path, 'w', encoding='utf-8') as f:
  json.dump(id_title_dict, f, ensure_ascii=False, indent=2)

print(f"NeMig id_to_title.json is saved to {output_id_to_title_path}.")


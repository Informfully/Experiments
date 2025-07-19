# Configuration settings for data enhancement pipeline
import os
dataset_result_path = './ebnerd_results'

input_file_path = os.path.join(dataset_result_path, 'cleaned_articles.csv')  # input path must be a csv file
output_file_path = dataset_result_path   # output path must be a directory to put all json files

lang = 'da'

# Define attributes for enriching features
attributes = {
    'category': {
        'enrich': True, # True or False
        'method': 'metadata', # Either 'metadata' or 'zero-shot'
        'cat_file_path': input_file_path
         ## If 'method' is set as 'zero-shot', then 'candidate_labels' must be provided.
    },
    'readability': {'enrich': True},
    'sentiment': {'enrich': True},
    'named_entities': {
        'enrich': True,
        'entities': ['PER', 'LOC', 'ORG', 'MISC'],  
        'ner_file_path': '',
    },
    'enriched_named_entities': {
        'enrich': True,
        'ener_file_path': '',
    },
    'region': {'enrich': True, 'lang': False},
    'political_party': {'enrich': True},
    'min_maj_ratio': {
        'enrich': True,
        'major_gender': ['male'],
        'major_citizen': ['Denmark'],
        'major_ethnicity': ['white people'],
        'major_place_of_birth': ['Denmark']
    },
    'story': {'enrich': True}
}

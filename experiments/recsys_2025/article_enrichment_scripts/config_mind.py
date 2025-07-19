# Configuration settings for data enhancement pipeline
import os
dataset_result_path = './mind_results'

input_file_path = os.path.join(dataset_result_path, 'cleaned_articles.csv')  # input path must be a csv file
output_file_path = dataset_result_path   # output path must be a directory to put all json files

lang = 'en'  # Example: "en", "de", "es", "fr"

# Define attributes for enriching features
attributes = {
    'category': {
        'enrich': True,  # True or False
        'method': 'metadata',  # Either 'metadata' or 'zero-shot'
        'cat_file_path': input_file_path,  # If not exists, leave as empty string (i.e, '')
#         'candidate_labels':  ['lifestyle' 'health' 'news' 'sports' 'weather' 'entertainment' 'autos'
#  'travel' 'foodanddrink' 'tv' 'finance' 'movies' 'video' 'music' 'kids'
#  'middleeast' 'northamerica' 'games']  # Example: ["politics", "public health", "economics", "business", "sports"]
        ## If 'method' is set as 'zero-shot', then 'candidate_labels' must be provided.
    },
    'readability': {'enrich': True},
    'sentiment': {'enrich': True},
    'named_entities': {
        'enrich': True,
         'entities':[ 'EVENT', 'LOC',  'NORP',  'ORG', 'PERSON'],
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
        'major_citizen': ['United States of America'],
        'major_ethnicity': ['white people'],
        'major_place_of_birth': ['United States of America']
    },
    'story': {'enrich': False}
}

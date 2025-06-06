import numpy as np
import re
import pandas as pd
import json
from gensim.models import FastText
import os


class GloveWrapper:
    def __init__(self, glove_dict):
        self.wv = self.WordVecs(glove_dict)
        self.vector_size = 300  # or len(any_vector) to infer dynamically


class WordVecs:
    def __init__(self, glove_dict):
        self.glove_dict = glove_dict
    def __contains__(self, key):
        return key in self.glove_dict
    def __getitem__(self, key):
        return self.glove_dict[key]
    

# Step 1: Load the pre-trained word embeddings
#
# ---------------------------------------
# For Mind, use glove.840B.300d.txt
# glove_path = "glove.840B.300d.txt"
# glove_dict = {}
#
# with open(glove_path, "r", encoding="utf-8") as f:
#     for line in f:
#         values = line.strip().split(" ")  
#         word = values[0]  
#         try:
#             vector = np.array(values[1:], dtype=np.float32)  
#             glove_dict[word] = vector  
#         except ValueError as e:
#             print(f"Skipping malformed line: {line[:50]}... Error: {e}")
#
# print(f"Loaded {len(glove_dict)} word vectors.")
# model = GloveWrapper(glove_dict)

# ---------------------------------------
# For Eb_Nerd,  FastText Danish vector (300-dimensional)
# input_folder = './ ebnerd _input' 
# model_path =  os.path.join(input_folder,'cc.da.300.bin') # Adjust this path to your actual file location
# model = FastText.load_fasttext_format(model_path)

# ---------------------------------------
#  For NeMig, use FastText German 300d vector, refer to https://fasttext.cc/docs/en/crawl-vectors.html
input_folder = './nemig_input'
model_path =  os.path.join(input_folder,'cc.de.300.bin')  # Adjust this path to your actual file location
model = FastText.load_fasttext_format(model_path)


# Step 2: Function to tokenize the sentence into words (consider punctuation as separate tokens)
def word_tokenize(sent):
    """Tokenize a sentence into words, handling punctuation properly.

    Args:
        sent: the sentence that needs to be tokenized.

    Returns:
        list: A list of words in the sentence.
    """
    pat = re.compile(r"[\w]+|[.,!?;|]")
    if isinstance(sent, str):
        return pat.findall(sent.lower()) # Tokenize and convert to lowercase
    else:
        return []

dataset_result_folder =  './nemig_results'
incompelete_article_path = os.path.join(dataset_result_folder, "cleaned_articles.csv")
df = pd.read_csv(incompelete_article_path, usecols=["id", "title"])
article_title = dict(zip(df["id"], df["title"]))


def detokenize(tokens):
    sentence = ""
    for token in tokens:
        if re.match(r"[.,!?;|]", token):
            sentence += token # No space before punctuation
        else:
            if sentence:
                sentence += " "
            sentence += token
    return sentence

filtered_news_title_dict = {}

for news_id, title in article_title.items():
    words = word_tokenize(title)
    # Keep only words in FastText vocab
    valid_words = [word for word in words if word in model.wv]
    if valid_words: # Only keep non-empty titles
        filtered_news_title_dict[news_id] = detokenize(valid_words)

# Save the cleaned Title as a JSON file 
cleaned_title_path = os.path.join(dataset_result_folder, "cleaned_id_title_mapping.json")

with open(cleaned_title_path, 'w', encoding='utf-8') as json_file:
  json.dump(filtered_news_title_dict, json_file, ensure_ascii=False, indent=4)

# Step 3: Initialize the word_index_dict and embedding_list
word_index_dict = {}
embedding_list = []

# Add an entry for the empty string "" (index 0)
word_index_dict[""] = 0
embedding_list.append(np.zeros((model.vector_size,)))  # First row is zero for ""

# Step 4: Tokenize the titles and populate word_index_dict and embedding_list
for article_id, title in filtered_news_title_dict.items():
    words = word_tokenize(title) 
    
    for word in words:
        # If the word is not already in word_index_dict, get its embedding
        if word not in word_index_dict:
            word_embedding = model.wv[word] # Get the word embedding from FastText
            word_index_dict[word] = len(word_index_dict)  # Assign an index
            embedding_list.append(word_embedding) # Append its embedding to the list

# Step 5: Create the embedding matrix from the list of embeddings
embedding_matrix = np.array(embedding_list)  

print("len Word Index Dictionary:", len(word_index_dict))
print("Embedding Matrix Shape:", embedding_matrix.shape)

# Step 6: Save the word index dictionary to a JSON file
word_index_path = os.path.join(dataset_result_folder, "word_index_dict.json")

with open(word_index_path, 'w', encoding='utf-8') as json_file:
    json.dump(word_index_dict, json_file, ensure_ascii=False, indent=4)

# Step 7: Save the embedding matrix to a .npy file
emb_matrix_path = os.path.join(dataset_result_folder, "embedding_matrix.npy")
np.save(emb_matrix_path, embedding_matrix)

print("Word index dictionary saved to 'word_index_dict.json' and embedding matrix saved to 'embedding_matrix.npy'")

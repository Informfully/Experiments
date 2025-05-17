import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
import pandas as pd
import numpy as np
import pickle
import re
from tqdm import tqdm  # Import tqdm for progress bar
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


dataset_result_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mind_results')


# Load model from HuggingFace Hub
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-mpnet-base-v2')
model = AutoModel.from_pretrained('sentence-transformers/all-mpnet-base-v2')


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model.to(device)

#Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

def split_into_sentences(text):
    # Improved sentence splitting using regex
    return re.split(r'(?<=[.!?])\s+', text.strip())

# Load your cleaned DataFrame from a CSV file
input_file_path = os.path.join(dataset_result_folder, "cleaned_articles.csv")
df = pd.read_csv(input_file_path)  

# Compute embeddings
news_ids = df['id'].tolist()
all_sentences = [split_into_sentences(text) for text in df['text'].astype(str)]

# Compute embeddings for each article
embeddings_list = []

for sentences in tqdm(all_sentences, desc="Processing articles", unit="article"):

    # Tokenize sentences
    encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt').to(device)

    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)

    # Perform pooling
    sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])

    # Normalize embeddings
    sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
    # Aggregate embeddings (mean pooling across sentences)
    article_embedding = sentence_embeddings.mean(dim=0)
    embeddings_list.append(article_embedding.cpu().numpy())



# Save embeddings and IDs in a single file
output_article_emb_path = os.path.join(dataset_result_folder, "news_embeddings.pkl")
embeddings_df = pd.DataFrame({'id': news_ids, 'embedding': embeddings_list})
embeddings_df.to_pickle(output_article_emb_path)

print("Embeddings saved successfully!")

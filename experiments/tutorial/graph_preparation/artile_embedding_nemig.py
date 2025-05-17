import pandas as pd
from sentence_transformers import SentenceTransformer
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


dataset_result_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'nemig_results')


input_file_path = os.path.join(dataset_result_folder, "cleaned_articles.csv")

df = pd.read_csv(input_file_path)
id_text_map = dict(zip(df['id'], df['text']))

print(f"len articles: {len(id_text_map)}")
import time
start_time = time.time()  


# Extract list of texts and corresponding ids
news_ids = list(id_text_map.keys())
texts = list(id_text_map.values())

model = SentenceTransformer("intfloat/multilingual-e5-base")

# Generate embeddings
embeddings = model.encode(texts, show_progress_bar=True)

# Print a few sample articles and their embeddings
for i in range(3):  # change 3 to however many samples you want
    print(f"\nSample {i+1}")
    print(f"ID: {news_ids[i]}")
    print(f"Text: {texts[i][:300]}...")  # only print first 300 characters for readability
    print(f"Embedding (first 10 values): {embeddings[i][:10]}")
    print(f"Embedding dimension: {len(embeddings[i])}")


# Save embeddings and IDs in a single file
embeddings_df = pd.DataFrame({'id': news_ids, 'embedding': embeddings.tolist()})


### save the embedding file

output_article_emb_path = os.path.join(dataset_result_folder, "news_embeddings.pkl")

embeddings_df.to_pickle(output_article_emb_path)

end_time = time.time()    # Record end time
elapsed_time = end_time - start_time

print(f"Time taken for computing article embedding for NeMig: {elapsed_time:.2f} seconds")
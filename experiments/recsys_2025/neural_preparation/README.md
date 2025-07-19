# Preparation for Running Neural Models

This guide explains how to prepare the training and test inputs required by our neural recommendation models for the following datasets: **EB-NeRD**, **NeMig**, and **MIND**.

## 1. Generate Train/Test Splits and User History

Each dataset must produce the following files:

- `uir_impression_train.csv` — user–item–rating interactions for training  
- `uir_impression_test.csv` — user–item–rating interactions for testing  
- `combined_user_history.json` — user browsing history in the format:
  ```json
  {
    "user_id_1": ["item_id_1", "item_id_2", ...],
    "user_id_2": ["item_id_3", "item_id_4", ...]
  }
  ```

* `article_pool.csv` — unique item IDs appearing in the test impressions.
This file is used for our experiments.

### NeMig and MIND

* Both datasets provide similar `behaviors.tsv` files.
* **MIND** includes predefined train/test splits.
* **NeMig** does not provide a split. We perform a **random 80/20 split**:

  * We found in the dataset, each user has **5 impressions**.
  * Randomly selecting **1** impression for testing, the remaining **4** for training.

### EB-NeRD

Use the following scripts (in order) from the `ebnerd` folder:

1. `combine_train_test_user_history_ebnerd.py`
   → generates `combined_user_history.json`
2. `generate_uir_train_impression.py`
   → generates `uir_impression_train.csv`
3. `generate_uir_test_impression.py`
   → generates `uir_impression_test.csv` and `article_pool.csv`

## 2. Clean Titles and Build Word Embeddings

Follow these steps to preprocess item titles and generate embedding matrices:

### 2.1: Install Dependencies

```bash
pip install gensim
```

### 2.2: Download Pretrained Word Vectors

| Dataset | Language | Source                                                                        |
| ------- | -------- | ----------------------------------------------------------------------------- |
| NeMig   | German   | [FastText 300d crawl vectors](https://fasttext.cc/docs/en/crawl-vectors.html) |
| EB-NeRD | Danish   | [FastText 300d crawl vectors](https://fasttext.cc/docs/en/crawl-vectors.html) |
| MIND    | English  | [GloVe 840B, 300d](https://nlp.stanford.edu/projects/glove/)                  |

### 2.3: Run `generate_word_embedding.py`

Update the script to point to the downloaded vector directory, then run it. It will produce:

| Output File                    | Description                                                                           |
| ------------------------------ | ------------------------------------------------------------------------------------- |
| `cleaned_id_title_mapping.csv` | Cleaned titles with only known words (i.e., words present in the embedding vocab)     |
| `word_index_dict.json`         | Mapping from words to row indices in the embedding matrix (index 0 = padding/unknown) |
| `embedding_matrix.npy`         | NumPy array of shape `(vocab_size, 300)`; first row is all zeros                      |

By default, all outputs are saved under `{datasetname}_results`.

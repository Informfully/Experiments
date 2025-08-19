# Preparation for Graph-Based Models (D-RDW, RP3-Beta, RWE-D)
 
This folder contains data preparation scripts for graph-based recommendation models such as **D-RDW**, **Rp3beta**, and **RWE-D**.

## Overview

For graph-based methods, the bipartite graph includes:

- **Known items**: Articles from training user impression logs (clicked articles) **and** user history (both train and test).
- **Unknown items**: Articles appearing only in test impression logs but **not** in user history or training clicks, meaning they are missing from the graph.

To incorporate unknown items into the graph, we:

1. Find their most similar known items using article embeddings.
2. Propagate user interactions from similar known items to these unknown items.
3. This ensures all test items are represented on the graph.

## Note

- The **EB-Nerd** dataset provides article embeddings directly, so no embedding creation is needed.
- For **NeMig** and **Mind**, embeddings are **not provided**. We generate article embeddings using `sentence-transformers`.

## Instructions

1. Install the required library:

   ```bash
   pip install sentence-transformers
   ```

2. Provide the `cleaned_articles.csv` file (output from `article_enrichment_scripts/data_cleaning_{datasetname}.py`), by default located in the `{datasetname}_results` folder.

3. Generate article embeddings by running the appropriate script:

   - `article_embedding_mind.py` for MIND
   - `article_embedding_nemig.py` for NeMig

4. After embedding generation, proceed with graph augmentation using the prepared embeddings.
Execute `generate_uir_augmentation_top3_combined_his.py`.

### Instructions for using `generate_uir_augmentation_top3_combined_his.py`

Before running the script, ensure the following files are prepared:

- `uir_impression_train.csv` — user–item–rating interactions from the training set impression logs.
- `uir_impression_test.csv` — user–item–rating interactions from the test set impression logs.
- `combined_user_history.json` — browsing history per user

Refer to `neural_preparation/README.md` for instructions on how to generate these files.

- The script augments each user–item interaction with additional interactions from the **Top-N most similar items** based on the pretrained embeddings.
- You can adjust the value of **TopN** within the script.
  In our experiments, we use:

  ```python
  TopN = 3
  ```

#### Output

The script generates `augmented_uir_top{TopN}similar.csv` (augmented user–item interaction file with added interactions from similar items.)

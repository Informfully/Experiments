# Informfully Recommenders Tutorial (2025)

This tutorial covers the basic steps for using the [Informfully Recommenders](https://github.com/Informfully/Recommenders).
Informfully Recommenders is an extension of [Cornac](https://github.com/PreferredAI/cornac).
Once installed, you can simply load and access the framework like any library/external dependency.

Please see the [Official Guide](https://cornac.readthedocs.io/en/v2.3.0/user/index.html) for installation instructions.
For a detailed overview, see our online documentation at [System Overview](https://informfully.readthedocs.io/en/latest/recommenders.html).

We share a complete collection of all our recommendations in [final recommendations](./final_recommendations/README.md).

## Overview

In this repository, we share our experiment configuration files.
We provide a brief guide to reproducing our results.
To run and everything shown in our paper, you need (1) experiment configuration files (this folder) and (2) a custom extension of the [Cornac recommender framework](https://github.com/Informfully/Recommenders).

This repository is organized as follows:

* **article_enrichment_scripts**: Code to enrich the dataset.
* **evaluation_scripts**: Code to evaluate the recommender algorithm performance.
* **experiment_reranking_scripts**: Code to re-rank the candidate lists.
* **experiment_scripts**: Code to initialize and run the recommender pipeline.s
* **graph_preparation**: Code to create and augment the graphs required for random walks.
* **neural_preparation**: Code to enrich, merge, and format the dataset for the neural baseline models.
* **PLD_EPD_preparation**: Code to prepare the data and run PLD and EPD algorithms.

Please follow the steps outlined below.
Steps 1-2 must be completed before running experiments.
The models shown in Step 3 can be run independently of each other (depending on what models and datasets you want to use).
Step 4, evaluating the recommendations, is optional and can be skipped.

## Step 1 - Download and Setup

* Step 1-1: Download our extended Cornac framework called [Informfully Recommenders](https://github.com/Informfully/Recommenders).
Please refer to the [Cornac tutorial](https://github.com/PreferredAI/cornac) for instructions on using the framework, in case you have any questions.
But **DO NOT** download the original Cornac codebase, as running our code requires additional functionality.
For a tutorial and installation instructions, we refer to the [official repository](https://github.com/PreferredAI/cornac).
Once installed, you can access Cornac as an external library.
In other words, you can focus on working exclusively with the files shared in this repository and run them from any folder.
* Step 1-2: In this tutorial, we use the EB-NeRD dataset, but you can use any other dataset of the same format.*
Download the EB-NeRD dataset from the [official website](https://recsys.eb.dk/index.html).
You need the following files: **ebnerd_small** (iter-item interactions) and **ebnerd_roberta_base** (article embeddings).
For legal reasons, we cannot include the dataset in our codebase.

(*) Datasets of the same format for which we provide additional examples are [MIND](https://msnews.github.io) and [NeMig](https://github.com/andreeaiana/nemig).

## Step 2 - Data Pre-processing

Please find the relevant files for this step in the folder: **article_enrichment_scripts**

* Step 2-1 (**article_enrichment_scripts/data_cleaning.py**): Data cleaning/removal of invalid items (i.e., items with empty or invalid date stamps).
Please ensure that you have installed **pandas** and **pyarrow** (for reading and writing **.parquet** files) before proceeding with this tutorial.
Two main actions are performed:
  * a) For each article, we combined the title and the subtitle/lead to make a longer article input title to train the neural model.
  * b) We then check if we have a complete data entry for the article entry.
  This includes the following attributes: published_time, body, title, category_str, and article_id.
  If any columns are empty or null, we add the article ID to **incomplete_ids**.
  This flags them for removal.
  * c) We then cleaned the article data, where all articles in **incomplete_ids** are removed from the item pool.
  This results in clean data collection, which is then exported to a CSV file.
  The CSV file contains the following attributes: article_id, title, body, published_date, and category.
  This file serves as the input for the next step, the data enrichment.
  Upon successful completion, the output of **data_cleaning.py** creates the following files: incomplete_article_ids.txt (the removed items) and cleaned_articles.csv (for article enrichment).

* Step 2-2 (**article_enrichment_scripts/article_enrich.py**): Run the augmentation scripts for sentiment, category, political entities, and story enrichments.
  * a) Before running **article_enrich.py**, you need to change the **config.py**.
  Everything can stay the same as in our example.
  However, you might want to change the path for the input file: **input_file_path** (the full path of the previously mentioned CSV **cleaned_articles.csv**) and **output_file_path** (your path to store the enriched JSON files).
  Please note that running the enrichment script requires an active internet connection, as it uses Wikidata for enrichment.
  * b) Upon successful completion, you will find the enriched JSON files in the path specified in **config.py**.
  This includes the following files: category.json, enriched_named_entities.json, min_maj_ratio.json, named_entities.json, party.json, readability.json, region.json, sentiment.json, and story.json.

## Step 3 - Running Recommenders

We provide instructions for running neural models (A), random walk models (B), and generating randomized baseline recommendations.
You can find more information on the neural recommenders used here on the [official GitHub repository](https://github.com/recommenders-team/recommenders).

### Part A - Running Neural Models

Please find the relevant files for this step in the folder: **neural_preparation**, **experiment_scripts**, and **experiment_reranking_scripts**

* Step 3A-1 (**neural_preparation/combine_train_test_user_history.py**): Extract user history from the EB-NeRD behavior file (this combines the history in the training and test set for each user, because the neural models’ input is limited to only one user history file).
The following two combination steps exist:
  * a) For users that are both in the training and validation set: Keep the history of the train **history.parquet** file.
  (The history in the validation set can be ignored, as it is a copy of the training history.)
  * b) For users only appear in the validation set: Use the history info from **history.parquet**.
  (The validation history can be used for training purposes, as the prediction task is tone on the impressions only, and not on any history.)
  
* Step 3A-2 (**neural_preparation/generate_uir_test_impression.py** and **neural_preparation/generate_uir_test_impression.py**): Read the impression logs from the EB-NeRD behavior file and convert them to the Cornac internal user-item interaction matrix (using a separate CSV file for training and validation set).
In doing so, we also remove any users with an empty history.
Finally, because Cornac requires a user-item interaction matrix, it accepts only one entry per user-item pair.
This has the following consequences:
  * a) The user-item interaction matrix cannot distinguish between an item being in the history vs. the impression list.
  * b) To have access to both the history and the impression articles, the history is folded into the impression (to make a distinction later on, the original history is provided as an additional parameter to the model).
  * c) Impressions are combined.
  (Articles can appear in multiple impressions of users.
  Once with a read status, once with an unread one.
  We now combine records for each user-item pair by saying that a user has read an item if there is at least one impression where the item is marked as read.)
  All data is automatically saved to a CSV containing the relevant impression items for the subsequent models in the user-item interaction format.

* Step 3A-3 (**neural_preparation/generate_word_embedding.py**): Preparation of the word embedding file for the neural models.
This required two inputs: **cleaned_articles.csv** (see Step 2) and the [fastText 300d word vector for Danish](https://fasttext.cc/docs/en/crawl-vectors.html).
Running the script will create a separate JSON file embedding that is leveraged by the neural models for article similarity.

* Step 3A-4 (pick neural model from folder: **experiment_scripts**): Prepare and run the experiment scripts (one for each mode), where you can specify the details for running the specific model (we provide a sample script with all the parameters used in our experiment for neural models.

* Step 3A-5 (pick re-ranking approach from folder: **experiment_reranking_scripts**): Run re-ranking experiment script (one for each re-ranking approach, this skips the recommendation step and uses pre-calculated candidate items/ranked list.

### Part B - Running Random Walk

Please find the relevant files for this step in the folder: **graph_preparation** and **experiment_scripts**

* Step 3B-1 (**graph_preparation/generate_uir_augmentation_top3_combined_his.py**): Run graph creation and augmentation scripts with the EB-NeRD behavior file as input.
The additional augmentation step is required to integrate cold items into the graph.
We use the EB-NeRD work embeddings for the similarity calculations (xlm_roberta_base.parquet).

* Step 3B-2 (**experiment_scripts/drdw_experiment.py**): For D-RDW, you first need to define a target distribution (see script, line 65ff.).
In our example, we provide a simplified mapping of the political landscape by using the broad categories of: a) government parties and supporting parties, b) opposition parties, and c) independent and foreign parties.
This division into different party buckets can be customized.
The script will then automatically detect any mentions of the parties that you have specified.
For this detection, two options are available.

  1) 'only_mentions' option counts mentions if it detects a subset of the specified party buckets, and no other parties from unspecified buckets in the article.
  For example, the list ['party1', 'party2'] and an article that mentions only 'party1' will match.
  If the article included 'party3', it would not match.
  2) 'composition' option counts mentions if it detects a subset for each specified party bucket.
  For example, the list with two buckets [['party1', 'party2'], ['party3', 'party4']] will match an article that contains ['party1', 'party4'].
  It will not match if a party from one of the buckets is absent.
  It will also not match if there is a 'party5' not present in any of the buckets.

<!--
By default, the target distribution creates five conditions:
1) government parties,
2) opposition parties,
3) government and opposition parties,
4) other parties (e.g., foreign parties), and 
5) no political parties.
-->

* Step 3B-3 (pick random walk from folder: **experiment_scripts**): Prepare and run the experiment scripts (one for each model), where you can specify the details for running the specific model.
We provide a sample script that includes all the parameters used in our random-walk experiment.

### Part C- Running Filtering Algorithms

Please find the relevant files for this step in the folder: **PLD_EPD_preparation**

* Step 3C-1 {**process_party_data_{datasetname}.py**}: Run the script with either 'ebnerd' or 'nemig' in the name to compute party classification.

* Step 3C-2 (**PLD_train_uir_processing.py**): Run this script to produce the training set uir format for the PLD model.

### Part D - Creating Random Baseline

Please find the relevant files for this step in the folder: **experiment_scripts/random_ebnerd_small.py**.
To run the random baseline script, simply provide the relevant user-item interaction metric and item pool as input.

## Step 4 - Evaluation Metrics

Please find the relevant file for this step in the folder: **evaluation_scripts**.
Run the evaluation script for calculating norm-aware diversity (RADio), traditional diversity (Gini, ILD), and AUC.
(Please note that there is no separate script for energy cost.
Instead, we time and log all events.
That way, we can calculate how long it took to successfully complete a given task.)
The following conditions apply to running the evaluation:

* RADio, Gini, and ILD are calculated using the top 20 items of the candidate list.
We provide a separate script that reduces and calculates only the top 20 recommendations (**compute_top20_list.py**).
This needs to be applied to all neural and random walk models, except D-RDW (which already has a max. recommendation limitation).
In addition to limiting the number of recommendations, this script also filters out items that a user has already added to their history.
* Norm-aware RADio diversity metrics are calculated using **check_diversity_ebnerd/check_radio.py**, traditional diversitc metrics can be fourn in **check_diversity_ebnerd/check_diversity.py**, and AUC is in **compute_auc.py**.
* Intra-List Distances (**generate_party_one_hot.py** and **generate_senti_one_hot.py**): We need vectors for the calculation of the intra-list distance for recommendations.
The two scripts provided here will encode the party and sentiment of articles into pre-defined buckets.
(Both the party and sentiment vectors are required to successfully compute ILD.)
There is no vector for the category; it is just a list of different categories.
(The category information is in the article dataset, where you can map the article raw ID to the category for every item in the article pool.)
* RADio Representation (**party_binary.py**): We used the binary mention of party in each article.
I.e., if an article is mentioned multiple times, it is only counted as once.
For articles without party mentions, there is a special entry {"No party":1} generated by a dedicated script (party_binary.py).

## Step 5 - Conducting User Studies

To turn this into a production-ready system for running user studies, the following three steps are necessary.

### Part A - Online Deployment

Tutorial page for [online deployment](https://informfully.readthedocs.io/en/latest/install.html).

### Part B - Creating Experiment

Tutorial page for [creating experiments](https://informfully.readthedocs.io/en/latest/overview.html).

### Part C - Item Visualization

Tutorial page for [iItem visualization](https://informfully.readthedocs.io/en/latest/recommendations.html).

## Resources

* [Experiments Repository](https://github.com/Informfully/Experiments) (recommender tutorial, this folder).
* [Recommenders Repository](https://github.com/Informfully/Recommenders) (extended recommendation framework).
* [Cornac Framework](https://github.com/PreferredAI/cornac) (official Cornac website with more tutorials).

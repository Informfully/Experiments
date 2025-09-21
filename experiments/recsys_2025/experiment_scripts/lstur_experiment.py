###### Experiment Script: LSTUR Model ######
# This script demonstrates the experiment of the LSTUR model.
#
# 1. Data Preparation:
#    - Loads user-item interaction data, user history, and impression logs.
#    - Splits the data into training and testing sets using `RatioSplit`.
#    - Processes item attributes (e.g., sentiment, category, complexity) 
#      for diversity metrics evaluation.
#
# 2. LSTUR Model Configuration:
#    - The LSTUR model utilizes user history and impression logs for training.
#    - Requires pre-trained word embeddings and mappings for processing news titles.
#
# 3. Evaluation:
#    - Defines metrics (e.g., NDCG, Recall).
#
# 4. Experiment Execution:
#    - Combines the LSTUR model, metrics in a Cornac `Experiment`.
#    - Results are saved for further analysis in the specified output directory.
# ============================================================================

import tensorflow as tf
tf.compat.v1.disable_eager_execution()
tf.get_logger().setLevel('INFO')
tf.autograph.set_verbosity(0)

import logging
tf.get_logger().setLevel(logging.ERROR)

import logging, os
logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=Warning)

import json
import numpy as np
import pandas as pd
import pickle
import random
import sys

from cornac.data import Reader
from cornac.eval_methods import BaseMethod
from cornac.metrics import Recall
from cornac.experiment.experiment import Experiment

from cornac.datasets import mind as mind


from cornac.models import LSTUR


#  Load data and set up environment
def main():

    dataset_name = 'ebnerd'
    
    input_path = f'./{dataset_name}_results'
    # Update the path for different dataset.
    # input_path = './mind_results'
    # input_path = './ebnerd_results'

    train_uir_path = os.path.join(input_path, 'uir_impression_train.csv')
    feedback_train = mind.load_feedback(fpath = train_uir_path)
    
    test_uir_path = os.path.join(input_path, 'uir_impression_test.csv')
    feedback_test = mind.load_feedback(fpath = test_uir_path)

    article_pool_path = os.path.join(input_path, 'article_pool.csv')
    impression_items_df = pd.read_csv(article_pool_path, dtype ={'iid': str})
    impression_iid_list = impression_items_df['iid'].tolist()

    user_history_path = os.path.join(input_path, 'combined_user_history.json')
    with open(user_history_path, 'r') as file:
        user_item_history = json.load(file)


    # Paths to article text, embedding resources
    title_emb_path = input_path
    title_dict_path = os.path.join(title_emb_path, 'cleaned_id_title_mapping.json')
    word_dict_path = os.path.join(title_emb_path, 'word_index_dict.json')
    word_embedding_path =  os.path.join(title_emb_path, 'embedding_matrix.npy')
    
    # Split data
    rs = BaseMethod.from_splits(
        train_data=feedback_train,
        test_data=feedback_test,
        exclude_unknowns=False,
        verbose=True,
        rating_threshold=0.5
    )
    


    # Set up the LSTUR model
    ##  we used npratio = 4 for NeMig and Mind
    ## npratio = 6 for Eb-Nerd
    # because npratio is higher in the eb-nerd dataset

    model = LSTUR(
        wordEmb_file = word_embedding_path,
        wordDict_file = word_dict_path,
        newsTitle_file = title_dict_path,
        userHistory = user_item_history,
        epochs = 150,
        word_emb_dim = 300, 
        head_num = 20,
        history_size = 50, 
        title_size = 30, 
        window_size = 3 , 
        filter_num = 300, 
        gru_unit = 300,
        npratio = 4,
        dropout = 0.2, 
        learning_rate = 0.001, 
        batch_size = 64, 
        seed = 42,
        article_pool=  impression_iid_list
    )

    # Define metrics
    targetSize = 20
    metrics = [Recall(k=targetSize)]

    
    experiment_output_path = f'./experiment_{dataset_name}_lstur_results'
    # Set up the experiment
    Experiment(
        eval_method=rs,
        models=[model],
        metrics=metrics,
        save_dir = experiment_output_path
    ).run()


if __name__ == "__main__":
    main()

import logging, os

logging.disable(logging.WARNING)

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=Warning)

import numpy as np
import pandas as pd
import pickle
import json
import random

import cornac
from cornac.eval_methods import BaseMethod
from cornac.metrics import Recall
from cornac.experiment.experiment import Experiment
from cornac.datasets import mind as mind

from cornac.models import RandomModel


# Load data and set up environment
def main():

    dataset_name = 'nemig'
    
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


    # Split data
    rs = BaseMethod.from_splits(
        train_data = feedback_train,
        test_data = feedback_test,
        exclude_unknowns = False,
        verbose = True,
        rating_threshold = 0.5
    )

    # Set up the RandomModel
    model = RandomModel(article_pool = impression_iid_list)

    # Define metrics
    targetSize = 20
    metrics = [Recall(k=targetSize)]

    experiment_output_path = f'./experiment_{dataset_name}_random_results'
    # Set up the experiment
    Experiment(
        eval_method = rs,
        models = [model],
        metrics = metrics,
        save_dir = experiment_output_path
    ).run()


if __name__ == "__main__":
    main()

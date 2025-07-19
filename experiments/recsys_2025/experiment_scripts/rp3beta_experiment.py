import logging, os
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
logging.disable(logging.WARNING)

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=Warning)

import numpy as np
import pandas as pd 

import cornac
from cornac.data import Reader
from cornac.eval_methods import BaseMethod
from cornac.metrics import MAE, RMSE, Recall, FMeasure
from cornac.experiment.experiment import Experiment
from cornac.metrics import NDCG, AUC, MRR, Precision
from cornac.metrics import GiniCoeff, ILD, EILD, Precision, Activation, Calibration, Fragmentation, Representation, AlternativeVoices, Alpha_NDCG, Binomial
from cornac.datasets import mind as mind
from cornac.eval_methods import RatioSplit
from cornac.utils import common

from cornac.models import RP3_Beta

dataset_name = 'nemig'

input_path = f'./{dataset_name}_results'
# Update the path for different dataset.
# input_path = './mind_results'
# input_path = './ebnerd_results'

## We used TopN = 3
TopN = 3

train_uir_path = os.path.join(input_path, f'augmented_uir_top{TopN}similar.csv')

feedback_train = mind.load_feedback(fpath=train_uir_path)

test_uir_path = os.path.join(input_path, 'uir_impression_test.csv')
feedback_test = mind.load_feedback(fpath=test_uir_path)


article_pool_path = os.path.join(input_path, "article_pool.csv")
impression_items_df = pd.read_csv(article_pool_path, dtype ={'iid': str})
impression_iid_list = impression_items_df['iid'].tolist()

rs = BaseMethod.from_splits(
    train_data = feedback_train, 
    test_data = feedback_test,
    exclude_unknowns = False,
    verbose = True,
    rating_threshold = 0.5
)



# Define metrics
targetSize = 20
metrics = [Recall(k=targetSize)]

model = RP3_Beta(article_pool = impression_iid_list)

experiment_output_path = f'./experiment_{dataset_name}_rp3beta_results'

# Put it together in an experiment, voilà!
cornac.Experiment(
    eval_method = rs,
    models = [model],
    metrics = metrics,
    save_dir = experiment_output_path
).run()

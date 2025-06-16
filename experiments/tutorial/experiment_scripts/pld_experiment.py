import cornac
from cornac.datasets import mind
from cornac.eval_methods import BaseMethod
from cornac.models import PLD
from cornac.metrics import MAE, NDCG, AUC, Recall, Precision

import pandas as pd
import os
import sys


dataset_name = 'nemig'
input_path = f'./{dataset_name}_results'

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
config_files_dir = os.path.join(current_dir, 'configs')
sys.path.insert(0, config_files_dir)

# Update the path for different dataset.
# input_path = './mind_results'
# input_path = './ebnerd_results'

train_uir_path = os.path.join(input_path, 'PLD_uir_trainImp_trainHis_testHis.csv')
feedback_train = mind.load_feedback(fpath = train_uir_path)
    
test_uir_path = os.path.join(input_path, 'uir_impression_test.csv')
feedback_test = mind.load_feedback(fpath = test_uir_path)

article_pool_path = os.path.join(input_path, 'article_pool.csv')
impression_items_df = pd.read_csv(article_pool_path, dtype ={'iid': str})
impression_iid_list = impression_items_df['iid'].tolist()

USER_GROUP = [[[-1.0], [2, 2, 3, 3, 2, 2, 2, 1, 1, 1, 1]],
              [[-0.5], [1, 2, 2, 3, 3, 2, 2, 2, 1, 1, 1]],
              [[0], [1, 1, 1, 2, 3, 4, 3, 2, 1, 1, 1]],
              [[0.5], [1, 1, 1, 2, 2, 2, 3, 3, 2, 2, 1]],
              [[1.0], [1, 1, 1, 1, 2, 2, 2, 3, 3, 2, 2]]]

rs =  BaseMethod.from_splits(train_data=feedback_train, test_data=feedback_test, exclude_unknowns=False,
        verbose=True,
        rating_threshold=0.5)

party_input_path = input_path

## For EB-Nerd and Nemig, load the converted party file. Refer to PLD_EPD_preparation folder.
## For Mind, load the raw party file: 'party.json'
party_path =  os.path.join(party_input_path, 'converted_party.json')

party_dict = mind.load_party(party_path, rs.global_iid_map)
party_dict = mind.build(party_dict, rs.global_iid_map )

num_users = len(set([u for u,i,r in feedback_train]))

num_items = len(rs.global_iid_map)

# initialize models
# group_granularity should be initial when it is not 0.2
config_path  = os.path.join(config_files_dir, 'model_parameters.ini') 

user_score_path = os.path.join(party_input_path, 'pld_user_score.csv')

item_score_path =os.path.join(party_input_path, 'pld_item_score.csv')

update_score = True

model = PLD(
    name = f'PLD_{dataset_name}',
    party_dict = party_dict,
    distribution = USER_GROUP,
    num_items = num_items,
    num_users = num_users,
    configure_path = config_path,
    user_score_path = user_score_path,
    item_score_path = item_score_path,
    update_score = True,
    article_pool = impression_iid_list)

# define metrics to evaluate the models
metrics = [Recall(k=20)]

# put it together in an experiment, voilà!
experiment_output_path = f'./experiment_{dataset_name}_pld_results'
cornac.Experiment(
        eval_method = rs,
        models = [model],
        metrics = metrics,
        save_dir = experiment_output_path
    ).run()

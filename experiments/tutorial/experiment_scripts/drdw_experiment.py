import os
import numpy as np
import pandas as pd
import pickle
import json
import random
import sys

from cornac.data import Reader
from cornac.eval_methods import BaseMethod
from cornac.experiment.experiment import Experiment
from cornac.datasets import mind as mind
from cornac.metrics import Recall
from cornac.models import D_RDW


# Load data and set up environment
def main():
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
   
    data_enrichment_path = input_path
    
    sentiment_file_path  = os.path.join(data_enrichment_path, 'sentiment.json')
    sentiment = mind.load_sentiment(fpath=sentiment_file_path)
    
    category_file_path  = os.path.join(data_enrichment_path, 'category.json')
    category = mind.load_category(fpath= category_file_path)
 
    party_file_path = os.path.join(data_enrichment_path, 'party.json')
    entities = mind.load_entities(fpath=party_file_path, keep_empty = True)

    Item_sentiment = mind.build(data=sentiment, id_map=rs.global_iid_map)
    Item_category = mind.build(data=category, id_map=rs.global_iid_map)
    Item_entities = mind.build(data=entities, id_map=rs.global_iid_map)   

    if dataset_name == "mind":
        Target_distribution = {
            "sentiment": {"type": "continuous", "distr": [
                {"min": -1, "max": -0.5, "prob": 0.2},
                {"min": -0.5, "max": 0, "prob": 0.3},
                {"min": 0, "max": 0.5, "prob": 0.3},
                {"min": 0.5, "max": 1.01, "prob": 0.2}
            ]},
            "entities": {"type": "parties", "distr": [
                {"description": "only mention", "contain": ["Republican Party"], "prob": 0.15},
                {"description": "only mention", "contain": ["Democratic Party"], "prob": 0.15},
                {"description": "composition", "contain": [["Republican Party"], ["Democratic Party"]], "prob": 0.15},
                {"description": "minority but can also mention", "contain": ["Republican Party", "Democratic Party"], "prob": 0.15},
                {"description": "no parties", "contain": [], "prob": 0.4}
            ]}
        }

    elif dataset_name == "nemig":
        gov_parties = [
            "Social Democratic Party of Germany", "Alliance '90/The Greens", "Free Democratic Party"
        ]

        opp_parties = [
            "Christian Democratic Union", "Christian Social Union of Bavaria",
            "Alternative for Germany", "The Left", "South Schleswig Voters' Association"
        ]

        gov_opp_combined_parties = gov_parties + opp_parties

        Target_distribution = {
            "sentiment": {"type": "continuous", "distr": [
                {"min": -1, "max": 0, "prob": 0.5},
                {"min": 0, "max": 1.01, "prob": 0.5}
            ]},
            "entities": {"type": "parties", "distr": [
                {"description": "only mention", "contain": gov_parties, "prob": 0.15},
                {"description": "only mention", "contain": opp_parties, "prob": 0.15},
                {"description": "composition", "contain": [gov_parties, opp_parties], "prob": 0.15},
                {"description": "minority but can also mention", "contain": gov_opp_combined_parties, "prob": 0.15},
                {"description": "no parties", "contain": [], "prob": 0.4}
            ]}
        }

    elif dataset_name == "ebnerd":
        gov_parties = [
            "Social Democrats", "Venstre", "Moderate Party", "Union Party",
            "Social Democratic Party", "Inuit Ataqatigiit", "Naleraq"
        ]

        opp_parties = [
            "Denmark Democrats - Inger Støjberg", "Green Left", "Liberal Alliance",
            "Conservative People's Party", "Conservative Party", "Red–Green Alliance",
            "Danish People's Party", "Danish Social Liberal Party", "The Alternative"
        ]

        gov_opp_combined_parties = gov_parties + opp_parties

        Target_distribution = {
            "sentiment": {"type": "continuous", "distr": [
                {"min": -1, "max": -0.5, "prob": 0.2},
                {"min": -0.5, "max": 0, "prob": 0.3},
                {"min": 0, "max": 0.5, "prob": 0.3},
                {"min": 0.5, "max": 1.01, "prob": 0.2}
            ]},
            "entities": {"type": "parties", "distr": [
                {"description": "only mention", "contain": gov_parties, "prob": 0.15},
                {"description": "only mention", "contain": opp_parties, "prob": 0.15},
                {"description": "composition", "contain": [gov_parties, opp_parties], "prob": 0.15},
                {"description": "minority but can also mention", "contain": gov_opp_combined_parties, "prob": 0.15},
                {"description": "no parties", "contain": [], "prob": 0.4}
            ]}
        }

    # Prepare article feature DataFrame for reranking
    article_feature_dataframe = (
        pd.Series(Item_category).to_frame('category')
        .join(pd.Series(Item_entities).to_frame('entities'), how='outer')
        .join(pd.Series(Item_sentiment).to_frame('sentiment'), how='outer')
    )

    # Set up the D-RDW model
    ## for Nemig, maxHops = 5 has better result
    ## for EB_NeRD and MIND,  maxHops = 3
    ## Other parameters are the same. 
    model = D_RDW(
        item_dataframe = article_feature_dataframe,
        diversity_dimension = ["sentiment", "entities"],
        target_distributions = Target_distribution,
        targetSize = 20,
        maxHops = 3, 
        filteringCriteria = None,
        rankingType = "graph_coloring",
        rankingObjectives = "category",
        sampleObjective = "rdw_score",
        verbose = True,
        article_pool = impression_iid_list
    )

    # Define metrics
    targetSize = 20
    metrics = [Recall(k=targetSize)]

    experiment_output_path = f'./experiment_{dataset_name}_drdw_results'
    # Set up the experiment
    Experiment(
        eval_method = rs,
        models = [model],
        metrics = metrics,
        save_dir = experiment_output_path
    ).run()


if __name__ == "__main__":
    main()

import json
import numpy as np
import pandas as pd
import pickle
import os
from cornac.data import Reader
from cornac.eval_methods import BaseMethod
from cornac.models import Recommender
from cornac.metrics import  Recall
from cornac.datasets import mind as mind
from cornac.rerankers import GreedyKLReranker, PM2Reranker, MMR_ReRanker, DynamicAttrReRanker
from cornac.experiment.pipelineExperiment import PipelineExperiment

os.environ["CUDA_VISIBLE_DEVICES"] = "6"


# Load data and set up environment
def main():

    experiment_config_file = './configs/npa_pipeline.ini'
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

    user_history_path = os.path.join(input_path, 'combined_user_history.json')
    with open(user_history_path, 'r') as file:
        user_item_history = json.load(file)

    # Split data
    ratio_split = BaseMethod.from_splits(
        train_data = feedback_train,
        test_data = feedback_test,
        exclude_unknowns = False,
        verbose = True,
        rating_threshold = 0.5
    )
    
    # Load article attributes
    data_enrichment_path = input_path
    sentiment_file_path  = os.path.join(data_enrichment_path, 'sentiment.json')
    sentiment = mind.load_sentiment(fpath=sentiment_file_path)
    category_file_path  = os.path.join(data_enrichment_path, 'category.json')
    category = mind.load_category(fpath= category_file_path)
    party_file_path = os.path.join(data_enrichment_path, 'party.json')
    entities = mind.load_entities(fpath=party_file_path, keep_empty = True)
    Item_sentiment = mind.build(data=sentiment, id_map=ratio_split.global_iid_map)
    Item_category = mind.build(data=category, id_map=ratio_split.global_iid_map)
    Item_entities = mind.build(data=entities, id_map=ratio_split.global_iid_map)
    senti_party_vec_path =  os.path.join(data_enrichment_path, 'combined_senti_party_vectors.json')
    sentiment_party_combined_vectors = mind.load_encoding_vectors(fpath=senti_party_vec_path)
    Item_sentiment = mind.build(data=sentiment, id_map=ratio_split.global_iid_map)
    Item_category = mind.build(data=category, id_map=ratio_split.global_iid_map)
    Item_entities = mind.build(data=entities, id_map=ratio_split.global_iid_map)
    Item_party_senti_vec = mind.build(data=sentiment_party_combined_vectors, id_map=ratio_split.global_iid_map)

    # Set up the model
    model = Recommender(name="NPA")

    # Define metrics
    targetSize = 20
    metrics = [Recall(k=targetSize)]

    # Prepare article feature DataFrame for reranking
    article_feature_dataframe = (
        pd.Series(Item_category).to_frame('category')
        .join(pd.Series(Item_entities).to_frame('entities'), how='outer')
        .join(pd.Series(Item_sentiment).to_frame('sentiment'), how='outer')
    )

    # Setup Target Distribution
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

    # Set up re-rankers
    sentiment_party_greedy_reranker = GreedyKLReranker(
        item_dataframe = article_feature_dataframe,
        diversity_dimension = ["sentiment", "entities"],
        top_k = targetSize,
        target_distributions = Target_distribution,
        diversity_dimension_weight = [0.5, 0.5],
        user_item_history = user_item_history, 
        rerankers_item_pool = impression_iid_list # for mind setup
    )

    sentiment_party_pm2_reranker = PM2Reranker(
        item_dataframe = article_feature_dataframe,
        diversity_dimension = ["sentiment", "entities"],
        top_k = targetSize,
        target_distributions = Target_distribution,
        diversity_dimension_weight = [0.5, 0.5],
        user_item_history = user_item_history, 
        rerankers_item_pool = impression_iid_list # for mind setup
    )

    sentiment_party_mmr_reranker = MMR_ReRanker(
        top_k = targetSize,
        item_feature_vectors = Item_party_senti_vec,
        user_item_history = user_item_history,
        rerankers_item_pool = impression_iid_list,
        lamda = 0.1
    )

    bin_edges = {'sentiment': [-1, -0.5, 0, 0.5, 1]}
    party_category_json_path = f"./configs/party_category_{dataset_name}.json"
    dynamic_reranker_rank_bias = DynamicAttrReRanker(
        name = "DYN_reranker_probByposition",
        item_dataframe = article_feature_dataframe,
        diversity_dimension = ["sentiment", "entities"], 
        top_k = targetSize,
        feedback_window_size = 3,
        bin_edges = bin_edges,
        user_choice_model= "logarithmic_rank_bias",
        user_simulator_config_path = "./configs/user_simulator_config.ini",
        party_category_json_path = party_category_json_path,
        user_item_history = user_item_history,
        rerankers_item_pool = impression_iid_list)

    dynamic_reranker_preference_bias = DynamicAttrReRanker(
        name = "DYN_reranker_probByPreference",
        item_dataframe = article_feature_dataframe,
        diversity_dimension = ["sentiment", "entities"],
        top_k = targetSize,
        feedback_window_size = 3,
        bin_edges = bin_edges,
        user_choice_model = "preference_based_bias",
        user_simulator_config_path = "./configs/user_simulator_config.ini",
        party_category_json_path = party_category_json_path,
        user_item_history = user_item_history,
        rerankers_item_pool = impression_iid_list)
    
    # Set up the experiment
    pipelineExp = PipelineExperiment(
        model=[model],
        metrics=metrics,
        eval_method = ratio_split,
        rerankers={
            'static': [
                sentiment_party_greedy_reranker,
                sentiment_party_pm2_reranker,
                sentiment_party_mmr_reranker
            ],
            'dynamic': [dynamic_reranker_rank_bias, dynamic_reranker_preference_bias]},
        user_based=True,
        verbose=False,
        pipeline_config_file=experiment_config_file
    )
    pipelineExp.run()


if __name__ == "__main__":
    main()

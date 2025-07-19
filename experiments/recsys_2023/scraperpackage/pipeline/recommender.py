from calendar import month
from datetime import date, datetime, timedelta
import random

from dotenv import load_dotenv
from os import getenv

from operator import itemgetter as i
from functools import cmp_to_key


current_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0, 0)
# current_date = datetime(year=2022, month=9, day=19, hour=0, minute=0, second=0, microsecond=0)


def cmp(x, y):
    
    """
    Replacement for built-in function cmp that was removed in Python 3

    Compare the two objects x and y and return an integer according to
    the outcome. The return value is negative if x < y, zero if x == y
    and strictly positive if x > y.

    https://portingguide.readthedocs.io/en/latest/comparisons.html#the-cmp-function
    """

    return (x > y) - (x < y)


def multikeysort(items, columns):
    comparers = [
        ((i(col[1:].strip()), -1) if col.startswith('-') else (i(col.strip()), 1))
        for col in columns
    ]
    def comparer(left, right):
        comparer_iter = (
            cmp(fn(left), fn(right)) * mult
            for fn, mult in comparers
        )
        return next((result for result in comparer_iter if result), 0)
    return sorted(items, key=cmp_to_key(comparer))


def prepare_recommendations(articles_collection, recommendations_collection, recommendation_lists_collection, users_collection):

    start_time = datetime.now()

    non_political_articles = load_articles_in_list(articles_collection=articles_collection, type='non-political', historical_data_days=0)
    
    # GROUP 1 - natural distribution
    # load all the political and non political articles into the seperate list without manipulation
    political_articles = load_articles_in_list(articles_collection=articles_collection, type='political', historical_data_days=0)
    save_recommendations(1, political_articles, non_political_articles, recommendations_collection)

    # GROUP 2 - major parties get the visibility
    # load all the political pertaining to SPD, CDU, and GREEN. any article associated to minor parties will be suppressed
    political_articles = load_articles_in_list(articles_collection=articles_collection, type='political', historical_data_days=0)
    political_articles[:] = [d for d in political_articles if d.get('FDP') + d.get('AfD') + d.get('DIE LINKE') + d.get('Other') == 0 ]
    save_recommendations(2, political_articles, non_political_articles, recommendations_collection)

    # GROUP 3 - minor parties get the visibility
    # load all the political pertaining to FDP, AfD, DIE LINKE, Others. 
    political_articles = load_articles_in_list(articles_collection=articles_collection, type='political', historical_data_days=0)
    political_articles[:] = [d for d in political_articles if d.get('FDP') + d.get('AfD') + d.get('DIE LINKE') + d.get('Other') > 0 ]
    save_recommendations(3, political_articles, non_political_articles, recommendations_collection)
    
    print('Step 1: recommendations have been prepared.')

    load_dotenv() # Set environment variables from .env file
    
    experiment_id = getenv("EXPERIMENTID")
    
    user_group_1_id = getenv("USERGROUP1ID")
    user_group_2_id = getenv("USERGROUP2ID")
    user_group_3_id = getenv("USERGROUP3ID")
    user_group_test_1_id = getenv("USERGROUPTEST1ID")
    user_group_test_2_id = getenv("USERGROUPTEST2ID")
    user_group_test_3_id = getenv("USERGROUPTEST3ID")

    user_group_1_description = getenv("USERGROUP1DESCRIPTION")
    user_group_2_description = getenv("USERGROUP2DESCRIPTION")
    user_group_3_description = getenv("USERGROUP3DESCRIPTION")
    user_group_test_1_description = getenv("USERGROUPTEST1DESCRIPTION")
    user_group_test_2_description = getenv("USERGROUPTEST2DESCRIPTION")
    user_group_test_3_description = getenv("USERGROUPTEST3DESCRIPTION")

    users_cursor = users_collection.find({ 'participatesIn': experiment_id })
    for user in users_cursor:
        user_group = user['userGroup']
        if user_group == user_group_1_id:
            save_recommendation_list(recommendations_collection, recommendation_lists_collection, user['_id'], 1, user_group_1_description)
        elif user_group == user_group_2_id:
            save_recommendation_list(recommendations_collection, recommendation_lists_collection, user['_id'], 2, user_group_2_description)
        elif user_group == user_group_3_id:
            save_recommendation_list(recommendations_collection, recommendation_lists_collection, user['_id'], 3, user_group_3_description)
        elif user_group == user_group_test_1_id:
            save_recommendation_list(recommendations_collection, recommendation_lists_collection, user['_id'], 1, user_group_test_1_description)
        elif user_group == user_group_test_2_id:
            save_recommendation_list(recommendations_collection, recommendation_lists_collection, user['_id'], 2, user_group_test_2_description)
        elif user_group == user_group_test_3_id:
            save_recommendation_list(recommendations_collection, recommendation_lists_collection, user['_id'], 3, user_group_test_3_description)
    
    print('Step 2: recommendation lists have been prepared.')
    
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
     

def load_articles_in_list(articles_collection, type, historical_data_days):

    articles = []    

    if type == 'political':        
        search_filter ={ '$and' : [
                        { 'political_references_count' : { '$gt' : 0 } },
                        { 'datePublished': { '$gte': current_date - timedelta(days=historical_data_days) } }
                        ] }
    else:
        search_filter ={ '$and' : [
                        { 'political_references_count' : 0 },
                        { 'datePublished': { '$gte': current_date - timedelta(days=historical_data_days) } }
                        ] }

    articles_cursor = articles_collection.find(search_filter)
    for article in articles_cursor:
        article_prop = {}
        article_prop['_id'] = article['_id']
        article_prop['guid'] = article['guid']
        article_prop['article_id'] = article['article_id']
        article_prop['primary_category'] = article['primaryCategory']
        article_prop['published_date'] = datetime.strptime(article['datePublished'].strftime("%Y-%m-%d"), "%Y-%m-%d")
        article_prop['political_references_count'] = article['political_references_count']
        article_prop['candidate_referenced'] = article['candidate_referenced']

        for political_reference in article['political_references']:
            article_prop[political_reference['party_name']] = political_reference['political_references_count_party_wise']

        articles.append(article_prop)    
    
    return articles


def save_recommendations(group, political_articles, non_political_articles, recommendations_collection):
    
    recommendations_count = 0

    # copy non political articles into another list and use the new list in subsequent steps
    _non_political_articles = non_political_articles[:]

    while (len(political_articles) + len(_non_political_articles) > 0):

        #first get the articles where local candidate is referenced
        random.shuffle(political_articles)
        random.shuffle(_non_political_articles)
        political_articles = multikeysort(political_articles, ['-candidate_referenced'])
        
        # 3 political articles
        for _ in range(3):
            if (len(political_articles) > 0):
                political_article = political_articles[0]
                # As the same article may be inserted twice or thrice in the recommendations table so
                # we are padding _id with the group number to make it unique
                political_article['_id'] = political_article['_id'] + str(group)
                political_article['group'] = group
                political_article['is_political'] = True
                # insert political article in the recommendations
                recommendations_collection.insert(political_article)
                # then remove this article from the list
                political_articles.pop(0)
                recommendations_count += 1
        
        # 3 non political articles
        for _ in range(3):
            if (len(_non_political_articles) > 0):
                non_political_article = _non_political_articles[0]
                # As the same article may be inserted twice or thrice in the recommendations table so
                # we are padding _id with the group number to make it unique
                non_political_article['_id'] = non_political_article['_id'] + str(group)
                non_political_article['group'] = group
                non_political_article['is_political'] = False
                # insert political article in the recommendations
                recommendations_collection.insert(non_political_article)
                # then remove this article from the list
                _non_political_articles.pop(0)
                recommendations_count += 1


def save_recommendation_list(recommendations_collection, recommendation_lists_collection, user_id, user_group, user_group_description):
    
    recommendation_lists = []
    prediction_counter = 999
    search_filter = { '$and' : [
                        { 'group' : user_group },
                        { 'published_date': { '$gte': current_date } }
                        ] }
    recommendations_cursor = recommendations_collection.find(search_filter)
    for recommendation in recommendations_cursor:
        recommendation_lists.append(
            {
                # we are not inserting _id; it would be auto assigned by mongodb
                "userId": user_id,
                "articleId": (recommendation['_id'])[0:24],
                "recommendationAlgorithm": user_group_description,
                "prediction": prediction_counter,
                "createdAt": datetime.now()
            }
        )
        prediction_counter -= 1
    recommendation_lists_collection.insert_many(recommendation_lists)

    # for recommendation in recommendations_cursor:
    #     recommendation_lists_collection.insert_one(
    #         {
    #             # we are not inserting _id; it would be auto assigned by mongodb
    #             "userId": user_id,
    #             "articleId": (recommendation['_id'])[:-1],
    #             "recommendationAlgorithm": user_group_description,
    #             "prediction": prediction_counter,
    #             "createdAt": datetime.now()
    #         }
    #     )
    #     prediction_counter -= 0.001

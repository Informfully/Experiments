from cmath import inf
from datetime import datetime
import time
from .utils.utils import Article

from tqdm import tqdm

import requests
from xml.etree import ElementTree
# from collections import defaultdict
# import re
# import json

from dotenv import load_dotenv
from os import getenv

# Define the default name and feed of the news outlet
NEWS_OUTLET = "WISO"
FEED_EXTRACTION_START_DATE = datetime.now().strftime("%Y%m%d")  #'20220908' #datetime.now().strftime("%Y%m%d")
FEED_EXTRACTION_END_DATE = datetime.now().strftime("%Y%m%d")

ARTICLES_LISTING_BASE_URL = 'https://www.genios.de/data/?START=A50&DBN=OUTLETS&ZG_USER=USERID&ZG_PASS=PASSWORD&DT='+FEED_EXTRACTION_START_DATE+'--'+FEED_EXTRACTION_END_DATE+'&TNR='
ARTICLE_DETAILS_BASE_URL = "https://www.genios.de/data/?START=A20&ZG_USER=USERID&ZG_PASS=PASSWORD&"
NEWS_LANGUAGE = "de-de"

def scrape(prestaging_collection):

    load_dotenv() # Set environment variables from .env file
    wiso_outlets = getenv("WISOOUTLETS")
    wiso_user_id = getenv("WISOUSERID")
    wiso_password = getenv("WISOPASSWORD")

    global ARTICLES_LISTING_BASE_URL, ARTICLE_DETAILS_BASE_URL
    ARTICLES_LISTING_BASE_URL = ARTICLES_LISTING_BASE_URL.replace('USERID', wiso_user_id).replace('PASSWORD', wiso_password).replace('OUTLETS', wiso_outlets)
    ARTICLE_DETAILS_BASE_URL = ARTICLE_DETAILS_BASE_URL.replace('USERID', wiso_user_id).replace('PASSWORD', wiso_password) 
    
    while(True):
        try:
            # first get the listings
            new_articles_listing_count =  load_articles_listing_to_prestaging(prestaging_collection)
            print('New articles (identifiers only) added to Pre staging collection from WISO:', new_articles_listing_count)
            print('Scraping Phase - step 1 completed at: ', datetime.now())
            break
        except Exception as e:
            print(e)
            time.sleep(3) # Sleep for 3 seconds and then try again
            continue
    
    while(True):
        try:
            # then pull the details for all the articles
            new_articles_count = load_articles_details_to_prestaging(prestaging_collection)    
            print('New articles added to Pre staging collection from WISO:', new_articles_count)    
            print('Scraping Phase - step 2 completed at: ', datetime.now())
            break                
        except Exception as e:
            print(e)
            time.sleep(3) # Sleep for 3 seconds and then try again
            continue

    return new_articles_count          


def save_article(prestaging_collection, article):  
    # Filter by guid
    filter = { 'article_id': article.article_id }

    # We shall pass the document object

    article_object = { "$setOnInsert": article.getArticleObject() }

    # Using update_one() method for single update with upsert.
    # upsert=True creates a new document if no documents match the filter. 
    # Otherwise, it updates a single document that matches the filter.
    updateResult = prestaging_collection.update_one(filter, article_object, upsert=True)
    # print(updateResult.raw_result['updatedExisting'])
    # print(updateResult.raw_result['n'])
    if (updateResult.raw_result['n'] == 1 and not updateResult.raw_result['updatedExisting']):
        return True
    return False

def load_articles_listing_to_prestaging(prestaging_collection):

    records_per_cycle = 200

    record_counter_start = 1
    record_counter_end = records_per_cycle
    records_count = inf

    new_articles_count = 0
        
    while record_counter_end <= records_count+records_per_cycle:  #10*records_per_cycle+1: #records_count+records_per_cycle:

        articles_listing_url = ARTICLES_LISTING_BASE_URL + str(record_counter_start) + '-' + str(record_counter_end)
        print('ARTICLES LISTING URL:', articles_listing_url)

        response = requests.get(articles_listing_url)
        response_tree = ElementTree.fromstring(response.content)

        #get total number of records returned in the reponse
        records_count = int(response_tree.find('tr_ges').text)
        print('Total records:', records_count, ' Records pulled:', str(record_counter_start), '-', str(record_counter_end))   

        # iterate news items
        for item in response_tree.findall('./treffer'):            

            article = Article()
            
            article.serial_number = item.find('./tr_nummer').text
            article.outlet = NEWS_OUTLET + '-' + item.find('./tr_datenbank').text
            article.published_date = datetime.strptime(item.find('./tr_datum').text, "%d.%m.%Y").strftime("%Y%m%d")
            article.language = NEWS_LANGUAGE
            
            #Title
            if item.find('./tr_titel_2') is not None:
                article.title = item.find('./tr_titel_2').text

            #Lead
            if item.find('./tr_titel_3') is not None:
                article.lead = item.find('./tr_titel_3').text   
            
            article.article_id = item.find('./tr_einzeldok_nr').text

            if save_article(prestaging_collection, article):
                    new_articles_count += 1

        record_counter_start += records_per_cycle
        record_counter_end += records_per_cycle
    
    return new_articles_count

def load_articles_details_to_prestaging(prestaging_collection):

    # Only pull the articles of which the details are not yet extracted.
    # hit those articles urls and load the details in the pre staging collection.

    search_filter = { 'guid': '' }
    documnets_count = prestaging_collection.count_documents(search_filter)
    print('Count of articles to be pulled from WISO:', documnets_count)

    ps_cursor = prestaging_collection.find(search_filter)    
    for ps_article in tqdm(ps_cursor, desc ="Progress", total=documnets_count):

        article = Article()

        article_url = ARTICLE_DETAILS_BASE_URL + ps_article['article_id']
        # print('Article URL:', article_url)

        article_response = requests.get(article_url)
        article_response_tree = ElementTree.fromstring(article_response.content)

        for node in article_response_tree.findall('./dokument/dok_field'): 

            #guid
            if (node.find('./kenner').text == 'id'):
                article.guid = node.find('./inhalt').text           

            #body
            elif (node.find('./kenner').text == 'TX'):
                article.body = node.find('./inhalt').text                    

            #primary categories
            elif (node.find('./kenner').text == 'KO'):
                article.primary_category = node.find('./inhalt').text

            #sub categories
            elif (node.find('./kenner').text == 'Z4'):
                article.sub_categories = node.find('./inhalt').text

        updated_values = { "$set": { "body": article.body,
                                     "primary_category": article.primary_category,
                                     "sub_categories": article.sub_categories,
                                     "guid": article.guid } }
        update_query = { "_id": ps_article['_id'] }
        prestaging_collection.update_one(update_query, updated_values)

    return documnets_count

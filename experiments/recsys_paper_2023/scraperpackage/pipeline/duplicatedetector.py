from nltk import ngrams
from datetime import datetime, timedelta

TIME_WINDOW = 7 # Time window in days to check for duplicates
NGRAM_AMOUNT_THRESHOLD = 10 # Number of matching sentences to be detected as duplicates
NGRAM_SIZE = 5 # Sizes of one ngram

# Check for duplicates of articles in the database (limited to the last X days)
def duplicate_check(staging_collection, articles_collection):

    start_time = datetime.now()

    staging_cursor = staging_collection.find({'is_valid': True })
    comparison_cursor = articles_collection.find({ 
        'dateScraped': {
            '$gte': datetime.now() - timedelta(days=TIME_WINDOW)
        },
    })

    new_count = 0
    duplicate_count = 0

    for staging_article in staging_cursor:        

        duplicate_flag = False

        for comparison_article in comparison_cursor:

            if is_duplicate(staging_article, comparison_article):

                # update the validation flag and reason in the staging collection
                updated_values = { "$set": { "is_valid": False, "invalidity_reason": 'Possible duplicate of '+ comparison_article['guid'] } }
                update_query = { "_id": staging_article['_id'] }
                staging_collection.update_one(update_query, updated_values)        

                duplicate_flag = True
                duplicate_count += 1
                break

        comparison_cursor.rewind()

        if not duplicate_flag:
            # Change body from string to list of dict having text type and text content
            # staging_article["body"] = [{"type":"text","text":staging_article["body"]}]
            articles_collection.insert_one(format_article(staging_article))
            new_count += 1

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))

    return new_count, duplicate_count

def is_duplicate(article_1, article_2):

    # Check the url only if its not empty. Because certain outlets don't provide article url
    # for WISO we don't get urls we are going to validate this check. hence commented this code block
    # if (article_1['url'] != ''):
    #     if article_1['url'] == article_2['url']:
    #         return True

    #if the article has already been copied to articles collection then that article should not be checked for duplication
    if article_1['_id'] == article_2['_id']:
        return False
    
    ngrams_1 = set(article_ngrams(article_1['body'])) #article from staging collection
    ngrams_2 = set(article_ngrams((article_2['body'][0])['text'])) #article from articles collection

    common_ngrams = ngrams_1.intersection(ngrams_2)
    if len(common_ngrams) > NGRAM_AMOUNT_THRESHOLD:
        return True
    
    return False


def article_ngrams(body_text):
    n_grams = []
    #commented by Rana; for NOZ we have one big block for news body. Either we split all the p tags into list
    # and keep using this code or treat it as one block and make the ngrams from it.

    # for paragraph in article['body']:
    #     paragraph_ngrams = ngrams(paragraph['text'].split(), NGRAM_SIZE)
    #     n_grams.extend(paragraph_ngrams)
    
    n_grams = ngrams(body_text.split(), NGRAM_SIZE)

    return n_grams

def format_article(staging_article):

    return {
        "_id": staging_article["_id"],
        "guid": staging_article["guid"],
        "article_id": staging_article["article_id"],
        "url": "",
        "primaryCategory": staging_article["primary_category"],
        "subCategories": staging_article["sub_categories"],
        "title": staging_article["title"],
        "lead": staging_article["lead"],
        "datePublished": datetime.strptime(staging_article["published_date"].strftime("%Y-%m-%d") + ' ' + datetime.now().strftime("%H:%M:%S"), "%Y-%m-%d %H:%M:%S"),
        "dateScraped": datetime.now(),
        "language": staging_article["language"],
        "outlet": staging_article["outlet"],
        "image": staging_article["image_url"], 
        "body": [{"type":"text","text":staging_article["body"]}],
        "body_word_count": staging_article["body_word_count"],
        "political_references": staging_article["political_references"],
        "political_references_count": staging_article["political_references_count"],
        "candidate_referenced": staging_article["candidate_referenced"]
    }


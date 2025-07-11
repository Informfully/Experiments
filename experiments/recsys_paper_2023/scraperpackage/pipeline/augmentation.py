from cgi import print_arguments
import re
from signal import raise_signal
from scraperpackage.scrapers.utils.utils import party_reference_counts
import spacy
from datetime import datetime

nlp = spacy.load("de_core_news_sm")

def augment(staging_collection, categories_collection, parties_collection, politicians_collection):

    # Calculate the word count of the body content and update the document
    update_body_word_counts(staging_collection)

    # Wherever lead is empty, fill it up with the first two sentences from the body content
    fill_lead_from_article_body(staging_collection)

    # Load the party names and politicians, followed by calculating their references in the articles
    findPoliticalReferences(staging_collection, parties_collection, politicians_collection)   

    # If there is any political reference in the article's meaning, any party name or political person is mentioned in the 
    # article, then the category of that article would be changed to Panorama only if the category of that article is not listed
    # categories collection
    update_primay_category(staging_collection, categories_collection)

    # Take the image URL from the categories collection and update the URL in staging against the article based on its category
    update_image_urls(staging_collection, categories_collection)
    
    # If it passes through all the conditions, only then will it be pushed to the articles collection 
    # in the next step, along with duplicate detection
    validateArticle(staging_collection)

    valid_articles_count = staging_collection.count_documents({'is_valid': True })
    return valid_articles_count


def update_body_word_counts(staging_collection):
    start_time = datetime.now()
    staging_cursor = staging_collection.find({})
    for staging_article in staging_cursor:
        updated_values = { "$set": { "body_word_count": len(re.findall(r'\w+', staging_article['body'])) } }
        update_query = { "_id": staging_article['_id'] }
        staging_collection.update_one(update_query, updated_values)
    
    print('Augmentation Phase: body word counts have been updated.')
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))


def fill_lead_from_article_body(staging_collection):

    start_time = datetime.now() 

    # Only pull the articles where the lead is empty and the body length is  more than or equal to 150     
    staging_cursor = staging_collection.find({ '$and': [ { 'lead': '' }, 
                                                         { 'body_word_count': { '$gte': 150 } } ] })
    for staging_article in staging_cursor:
        
        body_text = nlp(staging_article['body'].strip())        
        sentences = list(body_text.sents)

        if (len(sentences) > 1):
            lead_normalized = sentences[0].text + ' ' + sentences[1].text
        else:
            lead_normalized = sentences[0].text        

        updated_values = { "$set": { "lead":  lead_normalized } }
        update_query = { "_id": staging_article['_id'] }
        staging_collection.update_one(update_query, updated_values)
    
    print('Augmentation Phase: missing leads have been updated.')
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))


def findPoliticalReferences(staging_collection, parties_collection, politicians_collection):
    
    start_time = datetime.now()

    # Get all the distinct party categories from the collection
    # party_categories = sorted(parties_collection.distinct('party_category'))
    # Ideally, we should get the distinct categories from the collection, but we sort them
    # in a specific order, we are maintaining the list manually
    party_categories = ['SPD', 'CDU/CSU', 'DIE GRÜNE', 'AfD', 'DIE LINKE', 'FDP', 'Other']

    staging_cursor = staging_collection.find({ '$and': [ { 'body_word_count': { '$gte': 150 } } ] })
    # staging_cursor = staging_collection.find({ '_id': '632c48e37243d007a09ddf3d' })
    for staging_article in staging_cursor:

        political_references = []
        political_references_count = 0
        candidate_referenced = False    
        party_names_found = politicians_found = ''   
                
        for party_category in party_categories:

            # Set all the counters to zero at the category level
            title_party_ref_count = lead_party_ref_count = body_party_ref_count = 0
            title_politician_ref_count = lead_politician_ref_count = body_politician_ref_count = 0
            political_references_count_party_wise = 0

            parties_cursor = parties_collection.find({ 'party_category': {'$regex': party_category} })
            for party in parties_cursor:                

                # These three variables hold the counts returned by the function/method
                _title_party_ref_count, _lead_party_ref_count, _body_party_ref_count, _party_names_found = search_party_in_article(staging_article, party)

                title_party_ref_count += _title_party_ref_count
                lead_party_ref_count  += _lead_party_ref_count
                body_party_ref_count  += _body_party_ref_count                 
                
                if (_party_names_found != ''):
                    party_names_found += _party_names_found

                    # If a party is mentioned, only then will its politicians be checked in the articles. Otherwise No.

                    # politicians_cursor = politicians_collection.find({ 'party_name': {'$regex': party['party_name'], '$options': 'i'} })
                    politicians_cursor = politicians_collection.find({ 'party_name': party['party_name'] })
                    for politician in politicians_cursor: 

                        # These three variables hold the counts returned by the function/method
                        _title_politician_ref_count, _lead_politician_ref_count, _body_politician_ref_count = search_politician_in_article(staging_article, politician)

                        if (_title_politician_ref_count + _lead_politician_ref_count + _body_politician_ref_count > 0):
                            politicians_found += politician['fl_name'] + '; '
                            if politician['is_candidate'] == 'TRUE':
                                candidate_referenced = True
                        
                        title_politician_ref_count += _title_politician_ref_count
                        lead_politician_ref_count  += _lead_politician_ref_count
                        body_politician_ref_count  += _body_politician_ref_count  

                        # if (title_politician_ref_count + lead_politician_ref_count + body_politician_ref_count > 0 and not politician['is_candidate']):
                        #     candidate_referenced = True
            
            political_references_count_party_wise = title_party_ref_count + lead_party_ref_count + body_party_ref_count + \
                                        title_politician_ref_count + lead_politician_ref_count + body_politician_ref_count    
            
            political_references.append(party_reference_counts(
                                            party_name= party_category,
                                            title_party_ref_count= title_party_ref_count,
                                            lead_party_ref_count= lead_party_ref_count,
                                            body_party_ref_count= body_party_ref_count,
                                            title_politician_ref_count= title_politician_ref_count,
                                            lead_politician_ref_count= lead_politician_ref_count,
                                            body_politician_ref_count= body_politician_ref_count,
                                            political_references_count_party_wise = political_references_count_party_wise                                            
                                            ))
        
            political_references_count += political_references_count_party_wise

        updated_values = { "$set": { "political_references":  political_references,
                                     "political_references_count":  political_references_count,
                                     "candidate_referenced": candidate_referenced,
                                     "party_names_found": party_names_found,
                                     "politicians_found": politicians_found  } }
        update_query = { "_id": staging_article['_id'] }
        staging_collection.update_one(update_query, updated_values)
    
    print('Augmentation Phase: political references have been updated.')
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))


def search_party_in_article(article, party):

    matches_found_body = matches_found_title = matches_found_lead = 0
    party_names_found = ''

    # The party name is not part of aliases, so add it to the aliases list so that it can be matched as well
    party['aliases'].append(party['party_name'])

    for party_name_alias in party['aliases']:
    
        regex = r"\b" + party_name_alias + '\\b'

        _matches_found_title = len(list(re.finditer(regex, article['title'], re.MULTILINE)))
        _matches_found_lead  = len(list(re.finditer(regex, article['lead'], re.MULTILINE)))
        _matches_found_body  = len(list(re.finditer(regex, article['body'], re.MULTILINE)))

        if (_matches_found_title + _matches_found_lead + _matches_found_body > 0):
            party_names_found += party_name_alias + "; "
            matches_found_title += _matches_found_title
            matches_found_lead  += _matches_found_lead
            matches_found_body  += _matches_found_body

    return matches_found_title, matches_found_lead, matches_found_body, party_names_found     


def search_politician_in_article(article, politician):

    matches_found_body = matches_found_title = matches_found_lead = 0

    regex_full_name = r"\b" + politician['full_name'] + "\\b"
    regex_lastname_with_firstname = r"(?<="+ politician['first_name'] + "\s)" + politician['last_name']
    regex_lastname_without_firstname = r"(?<!"+ politician['first_name'] + "\s)" + politician['last_name'] 
    regex_firstname_without_lastname = r"" + politician['first_name'] + "(?!\s+" + politician['last_name'] + ")"
    
    # If the full name is equal to (first + last) name then apply the regex_lastname_with_firstname
    # otherwise match the full name
    if politician['full_name'] == politician['fl_name']:
        full_name_match_found_in_body = len(list(re.finditer(regex_lastname_with_firstname, article['body'], re.MULTILINE | re.IGNORECASE)))      
    else:
        full_name_match_found_in_body = len(list(re.finditer(regex_full_name, article['body'], re.MULTILINE | re.IGNORECASE)))

    if full_name_match_found_in_body > 0:
    
        matches_found_body += full_name_match_found_in_body
        matches_found_body += len(list(re.finditer(regex_lastname_without_firstname, article['body'], re.MULTILINE | re.IGNORECASE)))
        matches_found_body += len(list(re.finditer(regex_firstname_without_lastname, article['body'], re.MULTILINE | re.IGNORECASE)))
        # print("Matches found for body:", matches_found_body)

        matches_found_title += len(list(re.finditer(regex_lastname_with_firstname, article['title'], re.MULTILINE | re.IGNORECASE)))
        matches_found_title += len(list(re.finditer(regex_lastname_without_firstname, article['title'], re.MULTILINE | re.IGNORECASE)))
        matches_found_title += len(list(re.finditer(regex_firstname_without_lastname, article['title'], re.MULTILINE | re.IGNORECASE)))
        # print("Matches found for title:", matches_found_title)

        matches_found_lead += len(list(re.finditer(regex_lastname_with_firstname, article['lead'], re.MULTILINE | re.IGNORECASE)))
        matches_found_lead += len(list(re.finditer(regex_lastname_without_firstname, article['lead'], re.MULTILINE | re.IGNORECASE)))
        matches_found_lead += len(list(re.finditer(regex_firstname_without_lastname, article['lead'], re.MULTILINE | re.IGNORECASE)))
        # print("Matches found for lead:", matches_found_lead)

    return matches_found_title, matches_found_lead, matches_found_body


def update_primay_category(staging_collection, categories_collection):

    start_time = datetime.now()
    staging_cursor = staging_collection.find({ '$and': [ 
                                                        { 'body_word_count': { '$gte': 150 } },
                                                        { 'political_references_count' : { '$gt' : 0 }} 
                                                        ] })
    for staging_article in staging_cursor:

        if staging_article['primary_category'] == "":
            primary_category = 0 # means this does not exist in the categories collection
        else:
            primary_category = categories_collection.count_documents({ "$and": [
                    {'outlet': staging_article['outlet'].replace('WISO-','')},
                    {'primary_category': {'$regex': staging_article['primary_category'], '$options': 'i'} } 
                ] })
        if primary_category == 0:
            updated_values = { "$set": { "primary_category":  'Panorama' } }
            update_query = { "_id": staging_article['_id'] }
            staging_collection.update_one(update_query, updated_values)


    print('Augmentation Phase: primary category has been updated.')
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))


def update_image_urls(staging_collection, categories_collection):

    start_time = datetime.now()
    staging_cursor = staging_collection.find({ })
    for staging_article in staging_cursor:

        if staging_article['primary_category'] == "":
            category = None
        else:
            category = categories_collection.find_one({"$and": [
                {'outlet': staging_article['outlet'].replace('WISO-','')},
                {'primary_category': {'$regex': staging_article['primary_category'], '$options': 'i'} } 
                ] })
        
        # Only update the image URL for the articles whose categories are present in the "categories" collection. 
        if category is not None:        
            updated_values = { "$set": { "image_url": category['image_url'] } }
            update_query = { "_id": staging_article['_id'] }
            staging_collection.update_one(update_query, updated_values)

    # Fill the image_url with an empty string for all the articles whose category is not listed in the categories collection.
    staging_collection.update_many(        
        { "image_url": { '$exists': False } }, 
        { "$set": { "image_url": '' } }
    )

    print('Augmentation Phase: image urls have been updated.')
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))


def calculateWordCountLength(title):    

    doc = nlp(title.replace('-',' '))
    words_count = len([token.text for token in doc if not (token.is_space or token.is_punct) ])
    return words_count


def validateArticle(staging_collection):

    start_time = datetime.now()

    staging_cursor = staging_collection.find({})
    for staging_article in staging_cursor:

        reason = ''

        # Exclude the article if the body length is less than 150 words
        if (int(staging_article['body_word_count']) < 150):
            reason += 'Body text is less than 150 words; '

        # Exclude article if both title and Lead are empty;
        elif (staging_article['title'].strip() == '' and staging_article['lead'].strip() == ''):
            reason += 'Both title and Lead are empty; '  

        # If the article belongs to a category that is not in the allowed list (categories collection)
        # then the image_url would be empty. So we can safely check image_url and invalidate that particular article
        elif (staging_article['image_url'] is None or staging_article['image_url'] == ''):
            reason += 'Category is not in allowed list; '

        # This should be checked in the end, as the time to calculate the title length is high.
        # Title is less than 2 words
        if (calculateWordCountLength(staging_article['title'].strip()) < 2):
            reason = 'Title is less than 2 words; '            
           
        if reason != '':
            updated_values = { "$set": { "is_valid": False, "invalidity_reason": reason } }
        else:
            updated_values = { "$set": { "is_valid": True, "invalidity_reason": reason } }

        update_query = { "_id": staging_article['_id'] }
        staging_collection.update_one(update_query, updated_values)

    print('Augmentation Phase: valiation flag and reason have been updated.')
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))

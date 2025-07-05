import re

REGEXES = [
    (r'&quot;', '"'), # convert this to doube quotes
    (r'&amp;', '&'), # convert this to ampersand  
    (r'\"\s*([^\"]*?)\"', '\"\\1\"'), #remove space after the first double quote  
    (r'^xyxHTMLyxy<genios:style.*?xHTMLyxy<\/genios:style>xyxHTMEyxy',''), #remove author or location information mentioned in the beginning
    (r'^xyxHTMLyxy<genios:style.*?xHTMLyxy<\/genios:style>xyxHTMEyxy',''), #repeating this check in case both author and location are mentioned
    (r'xyxHTMLyxy.*?xyxHTMEyxy',''), #remove these tags from rest of the document
    (r'\.[^.]*$','.') #remove everything coming after last dot/full stop
]

def normalize(staging_collection):
    
    # Now apply regex to Title, Lead, and Body   
    staging_cursor = staging_collection.find({})
    for staging_article in staging_cursor:

        title_normalized = staging_article['title']
        lead_normalized = staging_article['lead']
        body_normalized = staging_article['body']

        for regex in REGEXES:
            compiled_regex = re.compile(regex[0])
            title_normalized = re.sub(compiled_regex, regex[1], title_normalized)
            lead_normalized = re.sub(compiled_regex, regex[1], lead_normalized)
            body_normalized = re.sub(compiled_regex, regex[1], body_normalized)

        # only for categories
        # compiled_regex_for_categories = re.compile('\<(.+?)\>')
        # sub_categories = sorted(re.findall(compiled_regex_for_categories, staging_article['sub_categories']))        
        
        updated_values = { "$set": { "title": title_normalized,
                                     "lead": lead_normalized,
                                     "body": body_normalized
                                    } }
        update_query = { "_id": staging_article['_id'] }
        staging_collection.update_one(update_query, updated_values)   

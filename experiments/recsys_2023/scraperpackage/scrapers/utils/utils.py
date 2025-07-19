from bson.objectid import ObjectId
from datetime import datetime
import os
import bson


def generate_id():
    return str(ObjectId())

class Article:
    def __init__(self, 
                    serial_number="",
                    published_date=datetime.now(),    
                    title="",
                    lead="",
                    language="de-de",
                    outlet="",
                    article_id="",
                    body="",
                    primary_category="",
                    sub_categories = "",
                    guid=""):
        self.serial_number = serial_number
        self.published_date = published_date
        self.title = title
        self.lead = lead
        self.language = language
        self.outlet = outlet
        self.article_id = article_id
        self.body = body
        self.primary_category = primary_category
        self.sub_categories = sub_categories
        self.guid = guid


    def getArticleObject(self):
        return {
            "_id": generate_id(), # Generate custom ID because the backend uses strings instead of ObjectId()s
            "serial_number": self.serial_number,
            "published_date": datetime.strptime(self.published_date, "%Y%m%d"), # add current timestamp to this        
            "title": self.title,
            "lead": self.lead,
            "scraped_date": datetime.now(), 
            "language": self.language,
            "outlet": self.outlet,
            "article_id": self.article_id, 
            "body": self.body,
            "primary_category": self.primary_category,
            "sub_categories": self.sub_categories,
            "guid": self.guid
        }

def create_article(
    *,
    guid,
    url,
    primary_category,
    sub_categories = [],
    title,
    lead,
    date_published,
    language,
    outlet,
    image_url = '',
    body,    
    is_valid = True,
    reason = '',
):
    return {
        "_id": generate_id(), # Generate custom ID because the backend uses strings instead of ObjectId()s
        "guid": guid,
        "url": url,
        "primaryCategory": primary_category, #this should be changed to primaryCategory
        "subCategories": sub_categories,   # to be changed to subCategories
        "title": title,
        "lead": lead,
        "datePublished": datetime.strptime(date_published, "%Y%m%d"), # to be changed to datePublished
        "dateScraped": datetime.now(), # to be changed to dateScraped
        "language": language,
        "outlet": outlet,
        "image": image_url, # to be changed to image
        # "body": list({"type":"text","text":body}), 
        "body": body, 
        "is_valid": is_valid,
        "reason": reason,
    }


def create_politician(
    *,
    full_name,    
    title,
    first_name,
    middle_name,
    last_name,
    party_name,
    parliament,
    state,
):
    return {
        "_id": generate_id(), # Generate custom ID because the backend uses strings instead of ObjectId()s
        "full_name": full_name,
        "title": title,        
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "fl_name": first_name + ' ' + last_name, #First and Last name
        "party_name": party_name,
        "parliament": parliament,
        "state": state,
        "is_candidate": False,
    }

def party_reference_counts(
    party_name,
    title_party_ref_count=0,
    lead_party_ref_count=0,
    body_party_ref_count=0,
    title_politician_ref_count=0,
    lead_politician_ref_count=0,
    body_politician_ref_count=0,
    political_references_count_party_wise=0,
):
    return {
        "party_name": party_name,
        "title_party_ref_count": title_party_ref_count,  
        "lead_party_ref_count": lead_party_ref_count,
        "body_party_ref_count": body_party_ref_count,
        "title_politician_ref_count": title_politician_ref_count,
        "lead_politician_ref_count": lead_politician_ref_count,
        "body_politician_ref_count": body_politician_ref_count,
        "political_references_count_party_wise": political_references_count_party_wise,
    }

def backup_mongodb_database(db, backup_path):

    filter = {"name": {"$regex": r"^(?!system\.)"}}
    collections = db.list_collection_names(filter=filter)

    for coll in collections:
        with open(os.path.join(backup_path, f'{coll}.bson'), 'wb+') as f:
            for doc in db[coll].find():
                f.write(bson.BSON.encode(doc))


def restore_mongodb_database(db, restore_from_path):
    for coll in os.listdir(restore_from_path):
        if coll.endswith('.bson'):
            with open(os.path.join(restore_from_path, coll), 'rb+') as f:
                db[coll.split('.')[0]].insert_many(bson.decode_all(f.read()))

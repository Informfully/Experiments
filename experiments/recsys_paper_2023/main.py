from scraperpackage.scrapers import wisoscraper, politiciansscraper
from scraperpackage.pipeline import duplicatedetector
from scraperpackage.pipeline import normalizer
from scraperpackage.pipeline import augmentation
from scraperpackage.pipeline import recommender
from scraperpackage.mongomanager import MongoManager
from scraperpackage.logger import Logger
from dotenv import load_dotenv
from traceback import print_exc
import os
from os import getenv
from datetime import datetime, timedelta
from scraperpackage.scrapers.utils.utils import backup_mongodb_database
import time


def main():
    load_dotenv() # Set environment variables from .env file

    scraper_modules = [ wisoscraper ]

    with Logger() as logger:
        with MongoManager() as db:

            ###################################################################################################################
            # First of all take the database backup, in case something goes wrong, we would be able to restore from the backup
            print('DB backup Phase started at: ', datetime.now())
            backup_path = os.path.join(getenv("MONGODBBACKUPPATH"), str(time.time()))
            os.mkdir(backup_path)
            backup_mongodb_database(db, backup_path)
            print('DB backup Phase ended at: ', datetime.now())
            
            ###################################################################################################################
            # Initialize PyMongo collections
            prestaging_collection = db[getenv("COLLECTIONPRESTAGING")]      
            staging_collection = db[getenv("COLLECTIONSTAGING")]       
            staging_archive_collection = db[getenv("COLLECTIONSTAGINGARCHIVE")]            
            politicians_collection = db[getenv("COLLECTIONPOLITICIANS")]
            parties_collection = db[getenv("COLLECTIONPARTIES")]
            categories_collection = db[getenv("COLLECTIONCATEGORIES")]
            articles_collection = db[getenv("COLLECTIONARTICLES")]
            recommendations_collection = db[getenv("COLLECTIONRECOMMENDATIONS")]
            recommendations_archive_collection = db[getenv("COLLECTIONRECOMMENDATIONSARCHIVE")]
            recommendation_lists_collection = db[getenv("COLLECTIONRECOMMENDATIONLISTS")]
            users_collection = db[getenv("COLLECTIONUSERS")]          

            ###################################################################################################################
            current_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0, 0)

            print('Data Clearing Phase started at: ', datetime.now())
            # For the scenarios in which we have to run the script again for any day, then the following collection
            # should be cleaned up, i.e. remove any data inserted in them for today.
            # need not to remove anything from staging as that would be refreshed with prestaging data everytime this script is run
            staging_archive_collection.delete_many({ "published_date": { "$gte": current_date }})
            articles_collection.delete_many({ "datePublished": { "$gte": current_date }})
            recommendations_collection.delete_many({ "published_date": { "$gte": current_date }})
            recommendations_archive_collection.delete_many({ "published_date": { "$gte": current_date }})
            recommendation_lists_collection.delete_many({ "createdAt": { "$gte": current_date }})
            print('Data Clearing Phase ended at: ', datetime.now())

            ###################################################################################################################
            # # Refresh Politicians Collection 
            # refreshPoliticiansCollection = getenv("REFRESHPOLITICIANS").upper() == "TRUE"
            # if (refreshPoliticiansCollection):
            #     try:
            #         result = politiciansscraper.scrapePoliticians(parties_collection, politicians_collection)
            #         logger.log(f'Inserted {result} politicians\' names into Politicians collection', 'Politicians Scraping Phase')
            #     except Exception as e:
            #         logger.log(str(e), "Politicians Scraping Phase", is_error=True)
            #         print_exc()
          
            ###################################################################################################################
            # Scraping phase
            print('Scraping Phase started at: ', datetime.now())
            # First empty Pre Staging collection for new articles            
            prestaging_collection.delete_many({ "published_date": { "$lt": current_date }})
            print('Data prior to ' + current_date.strftime('%Y-%m-%d %H:%M:%S') + ' has been cleared from Pre Staging collection.', )

            for scraper_module in scraper_modules:
                try:
                    scraped_articles_count = scraper_module.scrape(prestaging_collection)
                    logger.log(f'Inserted {scraped_articles_count} articles into prestaging from {scraper_module.NEWS_OUTLET}', 'Scraping Phase')
                except Exception as e:
                    logger.log(str(e), scraper_module.NEWS_OUTLET, is_error=True)
                    print_exc()            
            print('Scraping Phase ended at: ', datetime.now())
                 
            ###################################################################################################################
            # Copy all the articles from pre staging to staging
            print('Copy Phase started at: ', datetime.now())
            prestaging_collection.aggregate([ {'$match': {} }, { '$out': getenv("COLLECTIONSTAGING") } ])
            print('Copy Phase ended at: ', datetime.now())
            
            ###################################################################################################################
            # Perform Data Cleaning
            print('Normalization Phase started at: ', datetime.now())
            try:
                normalizer.normalize(staging_collection)
                logger.log('Articles in staging have been normalized', 'Normalization phase')
            except Exception as e:
                logger.log(str(e), 'Normalization phase', is_error=True)
            print('Normalization Phase ended at: ', datetime.now())

            ###################################################################################################################
            # Perform Data Augmentation
            print('Augmentation Phase started at: ', datetime.now())
            try:
                valid_articles_count = augmentation.augment(staging_collection, categories_collection, parties_collection, politicians_collection)
                logger.log(f'Articles in staging has been augmented. {valid_articles_count} are potential candidates for articles collection.', 'Augmentation phase')
            except Exception as e:
                logger.log(str(e), 'Augmentation phase', is_error=True)
            print('Augmentation Phase ended at: ', datetime.now())
                      
            ################################################################################################################### 
            # Duplication detection
            print('Duplication Phase started at: ', datetime.now())
            try:
                new_count, duplicate_count = duplicatedetector.duplicate_check(staging_collection, articles_collection)                
                logger.log(f'Duplication detection finished. {new_count} new articles / {duplicate_count} duplicates', 'Duplication Detection')
            except Exception as e:
                logger.log(str(e), 'Duplication detection phase', is_error=True)
            print('Duplication Phase ended at: ', datetime.now())

            ###################################################################################################################
            # Recommendations generation
            print('Recommendations Generation Phase started at: ', datetime.now())
            try:
                # First empty recommendations collection            
                recommendations_collection.delete_many({ "published_date": { "$lt": current_date }})
                print('Recommendation collection has been cleared.')
                recommender.prepare_recommendations(articles_collection, recommendations_collection, recommendation_lists_collection, users_collection)
                logger.log(f'Recommendation generation phase is completed', 'Recommendation Generation')
            except Exception as e:
                logger.log(str(e), 'Recommendation Generation phase', is_error=True)
            print('Recommendations Generation Phase ended at: ', datetime.now())               

            ###################################################################################################################
            # Copy all the data in staging and recommendations to archives for analysis purposes 
            # and secondly, the next day the staging collection will be refreshed from articles from prestaging
            print('Copy Phase to Archives started at: ', datetime.now())
            staging_archive_collection.insert_many([d for d in staging_collection.find({})])
            recommendations_archive_collection.insert_many([d for d in recommendations_collection.find({})])
            print('Copy Phase to Archives ended at: ', datetime.now())


if __name__ == "__main__":
    main()
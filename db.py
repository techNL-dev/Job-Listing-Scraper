from pymongo.mongo_client import MongoClient
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


cluster = MongoClient(os.environ["MONGO_URI"])
db = cluster["JobListingScraper"]
listing_collection = db["Listing"]


def upload_listings(data):
    all_listings = []
    for company in data:
        listings = data[company]
        for listing in listings:
            listing["company"] = company
            listing["posting_date"] = datetime.now()
            all_listings.append(listing)
    listing_collection.insert_many(all_listings)


def delete_all_listings():
    listing_collection.delete_many({})

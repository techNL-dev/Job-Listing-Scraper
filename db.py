from pymongo.mongo_client import MongoClient
import os
from datetime import datetime


cluster = MongoClient(os.environ["MONGO_URI"])
db = cluster["JobListingScraper"]
listings_collection = db["Listings"]


def upload_listings(data):
    all_listings = []
    for company in data:
        listings = data[company]
        for listing in listings:
            listing["company"] = company
            listing["posting date"] = datetime.now()
            all_listings.append(listing)
    listings_collection.insert_many(all_listings)


def delete_all_listings():
    listings_collection.delete_many({})

from pymongo.mongo_client import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

cluster = MongoClient(os.environ["MONGO_URI"])
db = cluster["JobListingScraper"]
listings_collection = db["Listings"]


def upload_listings(data):
    all_listings = []
    for company in data:
        listings = data[company]
        for listing in listings:
            listing["company"] = company
            all_listings.append(listing)
    listings_collection.insert_many(all_listings)


def delete_all_listings():
    listings_collection.delete_many({})

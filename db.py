from pymongo.mongo_client import MongoClient
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


cluster = MongoClient(os.environ["MONGO_URI"])
db = cluster["JobListingScraper"]
listing_collection = db["Listing"]


def upload_listings(data):
    # Initalize a few empty lists
    new_listings = []
    existing_listings = []
    removed_ids = []
    # For every listing from every company
    for company in data:
        listings = data[company]
        for listing in listings:
            # Check if the listing is already in the database
            existing_listing = listing_collection.find_one(
                {
                    "company": company,
                    "title": listing["title"],
                    "location": listing["location"],
                }
            )
            # If it isn't, add it to the new listings list
            if existing_listing == None:
                listing["company"] = company
                listing["posting_date"] = datetime.now()
                new_listings.append(listing)
            else:
                # Otherwise add it to the list of existing listings
                existing_listings.append(existing_listing)
    # For every listing currently in the database
    current_listings = list(listing_collection.find())
    for listing in current_listings:
        # If it's not in the exiting listings list, add it to the removed list
        if listing not in existing_listings:
            removed_ids.append(listing.get("_id"))
    # Delete all of the listings in the removed list if there are any
    if len(removed_ids) > 0:
        listing_collection.delete_many({"_id": {"$in": removed_ids}})
    # Add all of the listings in the new listings list if there are any
    if len(new_listings) > 0:
        listing_collection.insert_many(new_listings)

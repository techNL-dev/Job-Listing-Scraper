from pymongo.mongo_client import MongoClient
import os
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0"}

cluster = MongoClient(os.environ["MONGO_URI"])
db = cluster["JobListingScraper"]
listing_collection = db["Listing"]
previous_listing_collection = db["PreviousListing"]


def upload_listings(data):
    # Initalize a few empty lists
    new_listings = []
    existing_listings = []
    removed_ids = []
    removed_listings = []
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
                listing["languages_used"] = None
                listing["category"] = None
                new_listings.append(listing)
            else:
                # Otherwise add it to the list of existing listings
                existing_listings.append(existing_listing)
    # For every listing currently in the database
    current_listings = list(listing_collection.find())
    print("Checking which listings were removed...")
    for listing in current_listings:
        # If it's not in the exiting listings list, add it to the removed list
        if listing not in existing_listings:
            removed_listings.append(listing)
            removed_ids.append(listing.get("_id"))
    # Delete all of the listings in the removed list if there are any
    print("Deleting removed listings from the database...")
    if len(removed_ids) > 0:
        listing_collection.delete_many({"_id": {"$in": removed_ids}})
        previous_listing_collection.insert_many(removed_listings)
    # Add all of the listings in the new listings list if there are any
    print("Adding new listings...")
    if len(new_listings) > 0:
        listing_collection.insert_many(new_listings)

    # Trigger spreadsheet sync
    print("Syncing Spreadsheet...")
    response = requests.get(
        "https://script.google.com/macros/s/AKfycbyX_mV9c7EDPvJDRVukhfIat06WvsW-1QKbEC7IbjIZ42dxerh36tMTvG1_ILBhhPsw/exec?current=current"
    )
    print(response)
    response = requests.get(
        "https://script.google.com/macros/s/AKfycbyX_mV9c7EDPvJDRVukhfIat06WvsW-1QKbEC7IbjIZ42dxerh36tMTvG1_ILBhhPsw/exec?current=previous"
    )
    print(response)
    print("Finished syncing")

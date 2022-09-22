import os
from typing import Union
from fastapi import FastAPI, Header
from scrape import scrape_listings

app = FastAPI()


@app.get("/")
def get_root():
    # Let the user know that the server is still running
    return "Still running!"


@app.get("/api")
def scrape(authorization: Union[str, None] = Header(default=None)):
    # If the request has a specified header run the scrape
    if authorization == os.environ["API_SECRET_KEY"]:
        listing_count = scrape_listings()
        return f"Scraped {listing_count} job listings!"
    # Otherwise return "Unauthorized"
    else:
        return "Unauthorized"

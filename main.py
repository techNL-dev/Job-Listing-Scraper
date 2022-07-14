import os
from typing import Union
from fastapi import FastAPI, Header
from scrape import scrape_listings

app = FastAPI()


@app.get("/")
def get_root():
    return "Still running!"


@app.get("/api")
def scrape(authorization: Union[str, None] = Header(default=None)):
    if authorization == os.environ["API_SECRET_KEY"]:
        listing_count = scrape_listings()
        return f"Scraped {listing_count} job listings!"
    else:
        return "Unauthorized"

import os
from typing import Union
from fastapi import FastAPI, Header
from scrape import scrape_listings
import json

app = FastAPI()

company_name_list = []

with open("data.json", "r", encoding="utf-8") as data_json:
    data = json.loads(data_json.read())
    result = map(lambda company: company["name"], data["companies"])
    company_name_list = list(result)


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


@app.get("/companies")
def get_companies():
    return {"companies": company_name_list}

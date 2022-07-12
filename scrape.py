import json
import requests
from bs4 import BeautifulSoup, Tag
from db import upload_listings, delete_all_listings
from selenium_scrape import get_page_body, quit_selenium

REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0"}


def conditional_slice(content, slice_indices: list[int]):
    start_slice = slice_indices[0] if len(slice_indices) > 0 else None
    end_slice = slice_indices[1] if len(slice_indices) > 1 else None
    return content[start_slice:end_slice]


def get_listing_data(listing: Tag, data: dict):
    if data == None:
        return None
    return conditional_slice(listing.select(data["selector"])[0].text, data["indices"])


def get_listing_description(listing: Tag, data: dict):
    if data == None:
        return None
    description_parent = listing.select(data["selector"])[0]
    children = description_parent.find_all(recursive=False)
    children = conditional_slice(children, data["indices"])
    return list(map(lambda x: str(x), children))


def get_apply_link(listing: Tag, selector: str):
    if selector == None:
        return None
    link_tag = listing.select(selector)[0]
    return link_tag["href"]


def scrape_listings():
    output = {}
    count = 0

    with open("data.json", "r", encoding="utf-8") as data_json:
        data = json.loads(data_json.read())
        for company in data["companies"]:
            print(company["name"])
            response = requests.get(company["url"], headers=REQUEST_HEADERS)
            soup = BeautifulSoup(response.text, features="html.parser")
            listings = soup.find_all(
                company["listing"]["tag"],
                {"class": company["listing"]["class"]},
            )
            print(f"{len(listings)} listings found...")
            if len(listings) == 0:
                print("Trying Selenium...")
                body = get_page_body(company)
                soup = BeautifulSoup(body, features="html.parser")
                listings = soup.find_all(
                    company["listing"]["tag"],
                    {"class": company["listing"]["class"]},
                )
                print(f"{len(listings)} listings found...")
            count += len(listings)
            listing_data_list = []
            listing: Tag
            for listing in listings:
                listing_data = {}
                if company["details_link"] != None:
                    page_response = requests.get(
                        listing.select(company["details_link"])[0]["href"],
                        headers=REQUEST_HEADERS,
                    )
                    page_soup = BeautifulSoup(
                        page_response.text, features="html.parser"
                    )
                    listing = page_soup
                for key in company["data"]:
                    listing_data[key] = get_listing_data(listing, company["data"][key])
                listing_data["description"] = get_listing_description(
                    listing, company["description"]
                )
                listing_data["apply_link"] = get_apply_link(
                    listing, company["apply_link_selector"]
                )
                listing_data_list.append(listing_data)
            output[company["name"]] = listing_data_list
            print()

    with open("output.json", "w", encoding="utf-8") as output_json:
        json.dump(output, output_json, ensure_ascii=True, indent=2)

    delete_all_listings()
    upload_listings(output)

    print()
    quit_selenium()
    return count

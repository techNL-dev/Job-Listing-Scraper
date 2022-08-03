import json
from time import sleep
import requests
from bs4 import BeautifulSoup, Tag
from db import upload_listings
from selenium_scrape import get_page_body, quit_selenium
import os

REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0"}


def conditional_slice(content, slice_indices: list[int]):
    start_slice = slice_indices[0] if len(slice_indices) > 0 else None
    end_slice = slice_indices[1] if len(slice_indices) > 1 else None
    step_slice = slice_indices[2] if len(slice_indices) > 2 else None
    return content[start_slice:end_slice:step_slice]


def get_listing_data(listing: Tag, data: dict):
    if data == None:
        return None
    return conditional_slice(
        listing.select(data["selector"])[0].text.strip(), data["indices"]
    )


def get_listing_description(listing: Tag, data: dict):
    if data == None:
        return None
    description_parent = None
    if data["selector"] == "":
        description_parent = listing
    else:
        description_parent = listing.select(data["selector"])[0]
    children = description_parent.find_all(recursive=False)
    children = conditional_slice(children, data["indices"])
    return list(map(lambda x: str(x), children))


def get_link(listing: Tag, selector: str, url: str):
    if selector == None:
        return None
    link = listing.select(selector)[0]["href"]
    if link[0] == "/":
        link = "/".join(url.split("/")[:3]) + link
    return link


def scrape_listings():
    output = {}
    count = 0

    with open("data.json", "r", encoding="utf-8") as data_json:
        data = json.loads(data_json.read())
        for company in data["companies"]:
            print(company["name"])
            response = requests.get(company["url"], headers=REQUEST_HEADERS)
            soup = BeautifulSoup(response.text, features="html.parser")
            if company["listing"].get("parent_selector"):
                soup = soup.select(company["listing"].get("parent_selector"))[0]
            listings = soup.find_all(
                company["listing"]["tag"],
                {"class": company["listing"]["class"]},
            )
            print(f"{len(listings)} listings found...")
            if len(listings) == 0:
                print("Trying Selenium...")
                body = get_page_body(company["url"], company["listing"]["class"])
                soup = BeautifulSoup(body, features="html.parser")
                if company["listing"].get("parent_selector"):
                    soup = soup.select(company["listing"].get("parent_selector"))[0]
                listings = soup.find_all(
                    company["listing"]["tag"],
                    {"class": company["listing"]["class"]},
                )
                print(f"{len(listings)} listings found...")
            count += len(listings)
            listing_data_list = []
            listing: Tag
            for listing in conditional_slice(listings, company["listing"]["indices"]):
                listing_data = {}
                if company["details_page"] != None:
                    page_response_text = None
                    details_link = get_link(
                        listing,
                        company["details_page"]["link_selector"],
                        company["url"],
                    )
                    if company["details_page"]["static"]:
                        print("static")
                        page_response = requests.get(
                            details_link,
                            headers=REQUEST_HEADERS,
                        )
                        page_response_text = page_response.text
                    else:
                        print("dynamic")
                        page_response_text = get_page_body(
                            details_link, company["details_page"]["check_class"]
                        )
                    page_soup = BeautifulSoup(
                        page_response_text, features="html.parser"
                    )
                    listing = page_soup
                for key in company["data"]:
                    listing_data[key] = get_listing_data(listing, company["data"][key])
                listing_data["description"] = get_listing_description(
                    listing, company.get("description")
                )
                listing_data["apply_link"] = get_link(
                    listing, company.get("apply_link_selector"), company["url"]
                )
                listing_data_list.append(listing_data)
            output[company["name"]] = listing_data_list
            print()

    with open("output.json", "w", encoding="utf-8") as output_json:
        json.dump(output, output_json, ensure_ascii=True, indent=2)

    # upload_listings(output)

    print()
    quit_selenium()
    return count


if __name__ == "__main__":
    scrape_listings()

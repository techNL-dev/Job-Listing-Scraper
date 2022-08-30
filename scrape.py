import json
from operator import truediv
from time import sleep
import requests
from bs4 import BeautifulSoup, Tag
from db import upload_listings
from selenium_scrape import get_page_body, quit_selenium
import os
from urllib.parse import urljoin

REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0"}


def conditional_slice(content, slice_indices: list[int]):
    start_slice = slice_indices[0] if len(slice_indices) > 0 else None
    end_slice = slice_indices[1] if len(slice_indices) > 1 else None
    step_slice = slice_indices[2] if len(slice_indices) > 2 else None
    return content[start_slice:end_slice:step_slice]


def get_listing_data(listing: Tag, data: dict):
    if data == None:
        return None
    # print(listing.select(data["selector"]))
    data_text = (
        listing.select(data["selector"])[0].text
        if data["selector"] != ""
        else listing.text
    )
    data_text = data_text.strip()
    print(conditional_slice(data_text, data["indices"]))
    return conditional_slice(data_text, data["indices"])


def get_listing_description(listing: Tag, data: dict):
    if data == None:
        return None
    description_parent = None
    if data["selector"] == "":
        description_parent = listing
    else:
        print()
        print(listing)
        print(listing.select(data["selector"]))
        description_parent = listing.select(data["selector"])[0]
    children = description_parent.find_all(recursive=data["recursive"])
    children = conditional_slice(children, data["indices"])
    return list(map(lambda x: str(x), children))


def get_link(listing: Tag, selector: str, url: str):
    if selector == None:
        return url
    """print(listing)
    print(selector)
    print()
    print(listing.select(selector)[0])"""
    link = None
    if selector == "":
        print("sdfsdfsds")
        link = listing["href"]
    else:
        link = listing.select(selector)[0]["href"]
    link = urljoin(url, link)
    print(link)
    return link


def scrape_listings():
    output = {}
    count = 0

    with open("data.json", "r", encoding="utf-8") as data_json:
        data = json.loads(data_json.read())
        current_company = 8
        for company in data["companies"]:
            print(company["name"])
            response = requests.get(company["url"], headers=REQUEST_HEADERS)
            soup = BeautifulSoup(response.text, features="html.parser")
            valid_parent = True
            if company["listing"].get("parent_selector"):
                parent_selector_list = soup.select(
                    company["listing"].get("parent_selector")
                )
                """f = open("demofile3.html", "wb")
                f.write(parent_selector_list[0].encode("utf8"))
                f.close()
                quit_selenium()
                return"""
                if len(parent_selector_list) > 0:
                    soup = soup.select(company["listing"].get("parent_selector"))[0]
                else:
                    print("Parent not found...")
                    valid_parent = False
            listings = soup.find_all(
                company["listing"]["tag"],
                {"class": company["listing"]["class"]}
                if company["listing"]["class"]
                else None,
                recursive=company["listing"]["recursive"],
            )
            print(f"{len(listings)} listings found...")
            if len(listings) == 0 or not valid_parent:
                print("Trying Selenium...")
                check = (
                    company["listing"]["selector"]
                    if company["listing"]["find_by_selector"]
                    else company["listing"]["class"]
                )
                body = get_page_body(
                    company["url"],
                    check,
                    company["listing"]["find_by_selector"],
                )
                f = open("demofile3.html", "wb")
                f.write(body.encode("utf8"))
                f.close()
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
                details_link = None
                listing_data = {}
                print(listing)
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
                    print()
                    print(page_soup.select(company["data"]["title"]["selector"]))
                    listing = page_soup
                for key in company["data"]:
                    print(key)
                    listing_data[key] = get_listing_data(listing, company["data"][key])
                listing_data["description"] = get_listing_description(
                    listing, company.get("description")
                )
                print(details_link if details_link else company["url"])
                listing_data["apply_link"] = get_link(
                    listing,
                    company.get("apply_link_selector"),
                    details_link if details_link else company["url"],
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

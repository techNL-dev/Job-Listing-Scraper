import json
import requests
from bs4 import BeautifulSoup, Tag
from db import upload_listings
from selenium_scrape import get_page_body, quit_selenium
from urllib.parse import urljoin
from purifier.purifier import HTMLPurifier

# Headers for web requests
REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0"}
# Options for the HTML purifier
purifier = HTMLPurifier({"div": [], "span": [], "ul": [], "li": []})


def conditional_slice(content, slice_indices: list[int]):
    """Slice something depending on a list of indicies"""
    start_slice = slice_indices[0] if len(slice_indices) > 0 else None
    end_slice = slice_indices[1] if len(slice_indices) > 1 else None
    step_slice = slice_indices[2] if len(slice_indices) > 2 else None
    return content[start_slice:end_slice:step_slice]


def get_listing_data(listing: Tag, data: dict):
    """Get some listing data (title, location, etc...)"""
    if data == None:
        return None
    data_text = (
        listing.select(data["selector"])[0].text
        if data["selector"] != ""
        else listing.text
    )
    data_text = data_text.strip()
    # print(conditional_slice(data_text, data["indices"]))
    return conditional_slice(data_text, data["indices"])


def get_listing_description(listing: Tag, data: dict):
    """Get the description of a job listing"""
    if data == None:
        return None
    description_parent = None
    if data["selector"] == "":
        description_parent = listing
    else:
        # print()
        # print(listing)
        # print(listing.select(data["selector"]))
        description_parent = listing.select(data["selector"])[0]
    children = description_parent.find_all(recursive=data["recursive"])
    children = conditional_slice(children, data["indices"])
    return list(map(lambda x: purifier.feed(str(x)), children))


def get_link(listing: Tag, selector: str, url: str):
    """Get the link from the tag, and fix it if it's a fragment"""
    if selector == None:
        return url
    link = None
    if selector == "":
        link = listing["href"]
    else:
        link = listing.select(selector)[0]["href"]
    link = urljoin(url, link)
    # print(link)
    return link


def scrape_listings():
    """Scrape the job listings from the websites in data.json"""

    output = {}
    count = 0

    with open("data.json", "r", encoding="utf-8") as data_json:
        data = json.loads(data_json.read())
        for company in data["companies"][:2]:
            try:
                print(company["name"])
                response = requests.get(company["url"], headers=REQUEST_HEADERS)
                soup = BeautifulSoup(response.text, features="html.parser")
                valid_parent = True
                if company["listing"].get("parent_selector"):
                    parent_selector_list = soup.select(
                        company["listing"].get("parent_selector")
                    )
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
                    soup = BeautifulSoup(body, features="html.parser")
                    if company["listing"].get("parent_selector"):
                        soup = soup.select(company["listing"].get("parent_selector"))[0]
                    listings = soup.find_all(
                        company["listing"]["tag"],
                        {"class": company["listing"]["class"]},
                    )
                count += len(listings)
                listing_data_list = []
                listings = conditional_slice(listings, company["listing"]["indices"])
                listing: Tag
                actual_listing_count = len(listings)
                print(f"{actual_listing_count} listings found..")
                for i in range(actual_listing_count):
                    listing = listings[i]
                    print(f"Scraping {i+1}/{actual_listing_count}...")
                    details_link = None
                    listing_data = {}
                    # print(listing)
                    if company["details_page"] != None:
                        page_response_text = None
                        details_link = get_link(
                            listing,
                            company["details_page"]["link_selector"],
                            company["url"],
                        )
                        if company["details_page"]["static"]:
                            # print("static")
                            page_response = requests.get(
                                details_link,
                                headers=REQUEST_HEADERS,
                            )
                            page_response_text = page_response.text
                        else:
                            # print("dynamic")
                            page_response_text = get_page_body(
                                details_link, company["details_page"]["check_class"]
                            )
                        page_soup = BeautifulSoup(
                            page_response_text, features="html.parser"
                        )
                        # print()
                        # print(page_soup.select(company["data"]["title"]["selector"]))
                        listing = page_soup
                    for key in company["data"]:
                        # print(key)
                        listing_data[key] = get_listing_data(
                            listing, company["data"][key]
                        )
                    listing_data["description"] = get_listing_description(
                        listing, company.get("description")
                    )
                    # print(details_link if details_link else company["url"])
                    listing_data["apply_link"] = get_link(
                        listing,
                        company.get("apply_link_selector"),
                        details_link if details_link else company["url"],
                    )
                    listing_data_list.append(listing_data)
                output[company["name"]] = listing_data_list
                print()
            except:
                print(f"An error occurred while scraping {company.get('name')}")
                print()

    print(f"Scraped {count} listings in total")

    # Write the output of the scrape to a local file
    # with open("output.json", "w", encoding="utf-8") as output_json:
    #     json.dump(output, output_json, ensure_ascii=True, indent=2)

    # Upload the output of the scrape to MongoDB
    upload_listings(output)

    # Close the selenium controlled Chrome browser
    quit_selenium()
    return count


# Run the scrape_listings function if the file is run directly (from terminal)
if __name__ == "__main__":
    scrape_listings()

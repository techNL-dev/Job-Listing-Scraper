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


def conditional_slice(content, slice_indices: "list[int]"):
    """Slice something depending on a list of indicies"""
    start_slice = slice_indices[0] if len(slice_indices) > 0 else None
    end_slice = slice_indices[1] if len(slice_indices) > 1 else None
    step_slice = slice_indices[2] if len(slice_indices) > 2 else None
    return content[start_slice:end_slice:step_slice]


def get_listing_data(listing: Tag, data: dict):
    """Get some listing data (title, location, etc...)"""
    # If there's no data don't do anything
    if data == None:
        return None
    # Get the text of the data
    data_text = (
        listing.select(data["selector"])[0].text
        if data["selector"] != ""
        else listing.text
    )
    # Strip out any leading or trailing spaces
    data_text = data_text.strip()
    # Return the data text, sliced according to the indices
    return conditional_slice(data_text, data["indices"])


def get_listing_description(listing: Tag, data: dict):
    """Get the description of a job listing"""
    # If there's no data don't do anything
    if data == None:
        return None
    # Get the parent of the description if one is provided
    description_parent = None
    if data["selector"] == "":
        description_parent = listing
    else:
        description_parent = listing.select(data["selector"])[0]
    # Get all tags that are children of the parent
    children = description_parent.find_all(recursive=data["recursive"])
    # Slice the set of children according to the indices
    children = conditional_slice(children, data["indices"])
    # Map the set of children into a list
    children_list = list(map(lambda x: purifier.feed(str(x)), children))
    # Return the list as a string, joined by newline characters
    return "\n".join(children_list)

def get_category(title: str):
    # Gets the job title and makes it lower case for easier comparison to categories dictionary 
    title = title.lower()
    # Opens categories dictionary file
    with open("categories.json", "r", encoding="utf-8") as categories_json:
        cat = json.loads(categories_json.read())
        # Adds category tag based on keywords in the title of the job
        for category in cat["categories"]:
            if any(keyword in title for keyword in category["keywords"]):
                return category["title"]
        # if the job title has none of the keywords return the 'other' category tag
        return "Other"

def get_link(listing: Tag, selector: str, url: str):
    """Get the link from the tag, and fix it if it's a fragment"""
    # If there's no selector just return the URL
    if selector == None:
        return url
    link = None
    # If the selector is an empty string
    if selector == "":
        # Get the URL from the main listing tag
        link = listing["href"]
    else:
        # Otherwise get the URL from the tag specified by the selector
        link = listing.select(selector)[0]["href"]
    # Fix the link with urljoin if it's a fragment
    link = urljoin(url, link)
    # Return the link
    return link


def scrape_listing(company: dict, listing: Tag):
    """Scrape the details from an individual listing"""
    details_link = None
    listing_data = {}
    # If the listing has a separate page containing its details
    if company["details_page"] != None:
        page_response_text = None
        # Get the link to that page
        details_link = get_link(
            listing,
            company["details_page"]["link_selector"],
            company["url"],
        )
        # If the details page is static
        if company["details_page"]["static"]:
            # Get it with a normal request
            page_response = requests.get(
                details_link,
                headers=REQUEST_HEADERS,
            )
            page_response_text = page_response.text
        else:
            # Otherwise, get it with selenium
            page_response_text = get_page_body(
                details_link, company["details_page"]["check_class"]
            )
        # Get the soup for the details page and treat it as the listing tag
        page_soup = BeautifulSoup(page_response_text, features="html.parser")
        listing = page_soup
    # For each piece of data (title and location)
    for key in company["data"]:
        # Add it to the listing data object
        listing_data[key] = get_listing_data(listing, company["data"][key])
    # Get the description and add it to the data object
    listing_data["description"] = get_listing_description(
        listing, company.get("description")
    )
    # Get the job category based on the title and add it to the data object
    listing_data["category"] = get_category(
        listing_data["title"]
    )
    # Get the application link and add it to the data object
    listing_data["apply_link"] = get_link(
        listing,
        company.get("apply_link_selector"),
        details_link if details_link else company["url"],
    )
    return listing_data


def scrape_listings():
    """Scrape the job listings from the websites in data.json"""

    output = {}
    count = 0

    # Open the json file and load in its data
    with open("data.json", "r", encoding="utf-8") as data_json:
        data = json.loads(data_json.read())
        # For every company
        for company in data["companies"]:
            try:
                print(company["name"])
                # Get a soup of the pages body through a request
                response = requests.get(company["url"], headers=REQUEST_HEADERS)
                soup = BeautifulSoup(response.text, features="html.parser")
                valid_parent = True
                # If there is a defined "parent" selector for the listings
                if company["listing"].get("parent_selector"):
                    # Get the tag of that parent
                    parent_selector_list = soup.select(
                        company["listing"].get("parent_selector")
                    )
                    # If the parent is found
                    if len(parent_selector_list) > 0:
                        # Set the main soup to that tag
                        soup = soup.select(company["listing"].get("parent_selector"))[0]
                    else:
                        # Otherwise record that a valid parent was not found
                        print("Parent not found...")
                        valid_parent = False
                # Try to get the listings from the current soup
                listings = soup.find_all(
                    company["listing"]["tag"],
                    {"class": company["listing"]["class"]}
                    if company["listing"]["class"]
                    else None,
                    recursive=company["listing"]["recursive"],
                )
                # If no listings are found or no valid parent is found (when one is specified)
                if len(listings) == 0 or not valid_parent:
                    print("Trying Selenium...")
                    # Get the pages body with selenium
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
                    # Parse that body with BeautifulSoup
                    soup = BeautifulSoup(body, features="html.parser")
                    # If a parent selector is defined
                    if company["listing"].get("parent_selector"):
                        # Get it and set it as the main soup
                        soup = soup.select(company["listing"].get("parent_selector"))[0]
                    # Try to get the listings from the current soup
                    listings = soup.find_all(
                        company["listing"]["tag"],
                        {"class": company["listing"]["class"]},
                    )
                count += len(listings)
                listing_data_list = []
                # Discard some listings depending on the specified indices
                listings = conditional_slice(listings, company["listing"]["indices"])
                listing: Tag
                actual_listing_count = len(listings)
                print(f"{actual_listing_count} listings found... {listings}")
                # For each listing found
                for i in range(actual_listing_count):
                    listing = listings[i]
                    print(f"Scraping {i+1}/{actual_listing_count}...")
                    # Scrape the data from that listing
                    listing_data = scrape_listing(company, listing)
                    # Append it to the list of listing data
                    listing_data_list.append(listing_data)
                # Add the list of listing data to the output dict with the company name as the key
                output[company["name"]] = listing_data_list
                print()
            except:
                print(f"An error occurred while scraping {company.get('name')}")
                print()

    print(f"Scraped {count} listings in total")

    # Write the output of the scrape to a local file (uncomment the next to lines to test & see output)
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

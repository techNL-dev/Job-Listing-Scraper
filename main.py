import json
import requests
from bs4 import BeautifulSoup, Tag

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
    children = description_parent.find_all()
    children = conditional_slice(children, data["indices"])
    print()
    print()
    print()
    for child in children:
        print(child)
    return list(map(lambda x: str(x), children))


def main():
    output = {}

    with open("data.json", "r", encoding="utf-8") as data_json:
        data = json.loads(data_json.read())
        for company in data["companies"]:
            response = requests.get(company["url"], headers=REQUEST_HEADERS)
            soup = BeautifulSoup(response.text, features="html.parser")
            listings = soup.find_all("div", {"class": company["listing class"]})
            # print(len(listings))
            listing_data_list = []
            listing: Tag
            for listing in listings:
                listing_data = {}
                for key in company["data"]:
                    listing_data[key] = get_listing_data(listing, company["data"][key])
                listing_data["description"] = get_listing_description(
                    listing, company["description"]
                )
                # print(listing_data)
                listing_data_list.append(listing_data)
            output[company["name"]] = listing_data_list

    with open("output.json", "w", encoding="utf-8") as output_json:
        json.dump(output, output_json, ensure_ascii=True, indent=2)

    print()


if __name__ == "__main__":
    main()

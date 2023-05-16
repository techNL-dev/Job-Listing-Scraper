import json

def get_category(title: str, cat_file_location: str):
    # Gets the job title and makes it lower case for easier comparison to categories dictionary 
    title = title.lower()
    # Opens categories dictionary file
    with open(cat_file_location, "r", encoding="utf-8") as categories_json:
        cat = json.loads(categories_json.read())
        # Adds category tag based on keywords in the title of the job
        for category in cat["categories"]:
            if any(keyword in title for keyword in category["keywords"]):
                return category["title"]
        # if the job title has none of the keywords return the 'other' category tag
        return "Other"
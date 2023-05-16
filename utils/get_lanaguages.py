import json

def get_lanaguages(description: str, lang_file_location: str):
    # creates a blank language list array
    lang_list = []
    # Gets the job description and makes it lower case for comparison
    description = description.lower()
    # Opens the langauges dictionary file
    with open(lang_file_location, "r", encoding="utf-8") as languages_json:
        lang = json.loads(languages_json.read())
        # Adds language to language list array if found in the job description
        for language in lang["languages"]:
            if any(keyword in description for keyword in language["keywords"]):
                lang_list.append(language["language"])
    return lang_list
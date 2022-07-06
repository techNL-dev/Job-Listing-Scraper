import json
import requests
from bs4 import BeautifulSoup

REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0"}


def main():
    with open("data.json", "r", encoding="utf-8") as data_json:
        data = json.loads(data_json.read())
        for company in data["companies"]:
            response = requests.get(company["URL"], headers=REQUEST_HEADERS)
            soup = BeautifulSoup(response.text, features="html.parser")
            print(soup)
    print()


if __name__ == "__main__":
    main()

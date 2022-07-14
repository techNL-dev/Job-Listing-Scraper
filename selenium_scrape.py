from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import os

chrome_options = None
driver_path = "chromedriver.exe"
if os.environ.get("PYTHON_ENV") == "production":
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver_path = os.environ.get("CHROMEDRIVER_PATH")
driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)


def get_page_body(company):
    stuff = ""
    driver.get(company["url"])
    delay = 3  # seconds
    try:
        WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.CLASS_NAME, company["listing"]["class"]))
        )
        print("Page is ready!")
        stuff = driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML")
    except TimeoutException:
        print("Loading took too much time!")
    return stuff


def quit_selenium():
    driver.close()

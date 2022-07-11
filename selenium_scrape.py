from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

PATH = "chromedriver.exe"

driver = webdriver.Chrome(PATH)


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

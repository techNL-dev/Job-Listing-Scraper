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


def get_page_body(url: str, check: str, is_selector: bool = False):
    print(url)
    body = ""
    driver.get(url)
    delay = 5  # seconds
    try:
        by = By.CSS_SELECTOR if is_selector else By.CLASS_NAME
        print(check)
        print(by)
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((by, check)))
        print("Page is ready!")
        body = driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML")
    except TimeoutException:
        print("Loading took too much time!")
    return body


def quit_selenium():
    driver.close()

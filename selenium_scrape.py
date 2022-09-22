from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import os

chrome_options = None
driver_path = "chromedriver.exe"
# If the environment is set to "production" add these arguments to the chrome options
if os.environ.get("PYTHON_ENV") == "production":
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    # Set the driver path
    driver_path = os.environ.get("CHROMEDRIVER_PATH")
# Start the webdriver (computer controlled Chrome browser)
driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)


def get_page_body(url: str, check: str, is_selector: bool = False):
    """Get the body of the spage at the given URL"""
    print(url)
    body = ""
    # Open the given URL in a tab
    driver.get(url)
    delay = 5  # seconds
    try:
        # Is the element to be found specified by Class or CSS Selector?
        by = By.CSS_SELECTOR if is_selector else By.CLASS_NAME
        print(check)
        print(by)
        # Wait until a specified element is on screen, or the duration of delay
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((by, check)))
        print("Page is ready!")
        # Get the outter HTML (the body) of the page
        body = driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML")
    # If the element is not found after the delay
    except TimeoutException:
        # Print a message
        print("Loading took too much time!")
    # Return the body regardless of whether or not there is a timeout
    return body


def quit_selenium():
    """Close the webdriver"""
    driver.close()

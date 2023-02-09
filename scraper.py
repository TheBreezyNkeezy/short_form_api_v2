import time
import requests, pprint
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

TOKEN_LENGTH = 4

def parse_website(url: str, dyn: bool) -> str:
    if dyn == "dyn":
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        driver = webdriver.Chrome(
            # Try commenting/uncommenting the following if you get webdriver errors
            # ChromeDriverManager().install(),
            options=options
        )
        driver.get(url)
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "lxml")
        passage = soup.find_all(['p','h1','h2','h3','h4','h5','h6','th','td','div'])
        result = " ".join(
            [" ".join(elem.text.split()) for elem in passage]
        )
        driver.quit()
        return result
    elif dyn == "notdyn":
        result = requests.get(url)
        soup = BeautifulSoup(result.content, "lxml")
        passage = soup.find_all(['p','h1','h2','h3','h4','h5','h6','th','td','div'])
        result = " ".join(
            [" ".join(elem.text.split()) for elem in passage]
        )
        return result
    else:
        return "Please define either \"dyn\" or \"notdyn\" verbatim."
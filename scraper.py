import time
import requests, pprint
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

TOKEN_LENGTH = 4
MAX_TOKEN_COUNTS = 4096

def prepare_prompts(text):
    groups = []
    tokens = text.split()
    token_count = len(tokens)
    if token_count > MAX_TOKEN_COUNTS:
        split_factor = (token_count // MAX_TOKEN_COUNTS) + 1
        group_size, remainder = divmod(token_count, split_factor)
        for idx in range(split_factor):
            left = idx * group_size + min(idx, remainder)
            right = (idx + 1) * group_size + min(idx + 1, remainder)
            groups.append(" ".join(tokens[left:right]))
    else:
        groups = [" ".join(tokens)]
    return groups

def parse_website(url: str, dyn: bool) -> str:
    if dyn == "dyn":
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        driver = webdriver.Chrome(
            # Try commenting/uncommenting the following if you get webdriver errors
            ChromeDriverManager().install(),
            options=options
        )
        time.sleep(8)
        driver.get(url)
        time.sleep(10)
        soup = BeautifulSoup(driver.page_source, "lxml")
        passage = soup.find_all(['p','h1','h2','h3','h4','h5','h6'])
        result = " ".join(
            [" ".join(elem.text.split()) for elem in passage]
        )
        driver.quit()
        return result
    elif dyn == "notdyn":
        result = requests.get(url)
        soup = BeautifulSoup(result.content, "lxml")
        passage = soup.find_all('p')
        return " ".join([elem.text for elem in passage])
    else:
        return "Please define either \"dyn\" or \"notdyn\" verbatim."
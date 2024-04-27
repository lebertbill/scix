from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from time import sleep
import requests
from bs4 import BeautifulSoup
import re
import sys
from crossref.restful import Works
import pdfx

def downloadfromlink(link):

    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    driver.get('https://sci-hub.tw/')
    a = driver.find_element_by_xpath(".//*[@id='input']/form/input[2]").send_keys(link)
    driver.find_element_by_xpath(".//*[@id='open']").click()

    # wait = WebDriverWait(driver, 1)
    iframes = driver.find_elements_by_xpath("//iframe")
    for i in iframes:
        a = i.get_attribute("src")
        print(i.get_attribute("src"))

    r = requests.get(a, allow_redirects=True)

    open('test.pdf', 'wb').write(r.content)
    newurl = driver.current_url

    res = requests.get(newurl)
    soup = BeautifulSoup(res.text, "html5lib")
    pattern = re.compile(r"var doi = '(.*?)';$", re.MULTILINE | re.DOTALL)
    script = soup.find("script", text=pattern)
    doi = pattern.search(script.text).group(1)

    works = Works()
    meta = works.doi(doi)

    try:
        title = meta['title']
        title = title[0]
    except KeyError:
        title = None
    try:
        authors = meta['author']
        authordict = []
        for i in range(len(authors)):
            authordict.append(authors[i])
        author = []
        for i in range(len(authordict)):
            author.append(authordict[i]['given'] + authordict[i]['family'])
    except KeyError:
        author = None
    try:
        journal = meta['container-title']
        journal = journal[0]
    except KeyError:
        journal = None
    try:
        yr = meta['created']
        yrs = yr['date-time']
        year = yrs[:4]
    except KeyError:
        year = None
    print(journal)
    print(author)
    print(year)
    print(title)
    driver.close()

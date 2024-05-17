from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time, json, os

URL = 'https://id.indeed.com'

# Configure Chrome options for headless browsing
chrome_options = Options()
chrome_options.add_argument("--headless")  

# Creating a webdriver instance
chrome_driver_path = "C:\\Users\\Vigneswaran\\OneDrive - Datanetiix Solutions Inc\\Desktop\\Indeed_Scraper\\chromedriver.exe"
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# This instance will be used to log into indeed
def open_page(query, loc):
    driver.get(URL)
    # fill the form for job_title and location
    job_title = driver.find_element(By.NAME, 'q')
    job_title.send_keys(query)
    location = driver.find_element(By.NAME, 'l')
    location.send_keys(loc)
    location.send_keys(Keys.ENTER)
    time.sleep(1)

def next_page(page):
    if page > 1:
        link_list = driver.find_elements(By.CLASS_NAME, "css-ho7khd")
        link_list[page - 2].click()
        time.sleep(5)

def get_all_items(query, loc, page):
    # retrieve the html data
    page_source = driver.page_source

    # soup the html
    soup = BeautifulSoup(page_source, 'html.parser')

    # scraping process
    contents = soup.find_all('table', 'jobCard_mainContent big6_visualChanges')
    jobs_list = []
    for item in contents:
        title = item.find('h2', 'jobTitle').text
        company = item.find('span', 'companyName')
        company_name = company.text
        try:
            company_link = URL + company.find('a')['href']
        except:
            company_link = "Link is not available"

        # sorting data
        data_dict = {
            'title': title,
            'company name': company_name,
            'link': company_link,
        }
        jobs_list.append(data_dict)

    return jobs_list

def run():
    query = input("Enter your query: ")
    loc = input("Enter your location: ")
    open_page(query, loc)
    page = 1
    while True:
        items = get_all_items(query=query, loc=loc, page=page)
        if items:
            for item in items:
                print(item)
            page += 1
            next_page(page=page)
        else:
            break

if __name__ == "__main__":
    run()

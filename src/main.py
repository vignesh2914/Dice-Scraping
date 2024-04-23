from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

def scrape_job_data_from_website(webpage, keywords, page_number, location_name):
    next_page = webpage.format(keywords, location_name, page_number)
    print(next_page)

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    service = Service('C:\\Users\\Vigneswaran\\OneDrive - Datanetiix Solutions Inc\\Desktop\\Dice_Scraping\\chromedriver.exe')  # Set the path to your chromedriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(next_page)

    time.sleep(5)  

    # Get page source after JavaScript execution
    page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'html.parser')

    jobs = soup.find_all('div', class_='d-flex justify-content-between title-container')
    job_data = []
    for job in jobs:
        company_name = job.find('a', class_='ng-star-inserted').text.strip() 
        job_title = job.find('div', class_='overflow-hidden').text.strip()
        job_location_element = job.find('span', class_='search-result-location')
        job_location = job_location_element.text.strip() if job_location_element else "Location not found"

        job_data.append({"company_name": company_name, "job_title": job_title, "job_location": job_location})

    driver.quit()
    return job_data

def dice_scraper(webpage, keywords, page_number, num_pages, location_name):
    for page in range(page_number, page_number + num_pages):
        job_data = scrape_job_data_from_website(webpage, keywords, page, location_name)
        
        if not job_data:
            print("No job data found. Retrying in 10 seconds...")
            time.sleep(10)  # Cooldown time
            job_data = scrape_job_data_from_website(webpage, keywords, page, location_name)
            
            if not job_data:
                print("Still no job data found. Exiting...")
                return
            
        for job in job_data:
            print("Company Name:", job["company_name"])
            print("Job Title:", job["job_title"])
            print("Job Location:", job["job_location"])
            print()

filter_number = int(input("Enter the filter number: "))
user_keywords = input("Enter the job keywords: ")
num_pages = int(input("Enter the number of pages to scrape: "))
location_name = input("Enter the location name: ")

filter_option = {
    1: 'https://www.dice.com/jobs?q={}&location={}&page={}&pageSize=20&language=en&eid=0904',
    2: 'https://www.dice.com/jobs?q={}&location={}&page={}&pageSize=20&filters.postedDate=SEVEN&language=en&eid=0904',
    3: 'https://www.dice.com/jobs?q={}&location={}&page={}&pageSize=20&filters.postedDate=THREE&language=en&eid=0904',
    4: 'https://www.dice.com/jobs?q={}&location={}&page={}&pageSize=20&filters.postedDate=ONE&language=en&eid=0904'
}

if filter_number not in filter_option:
    print("Invalid filter number")
else:
    print("Scraping started...")
    selected_url = filter_option[filter_number]
    dice_scraper(selected_url, user_keywords, page_number=1, num_pages=num_pages, location_name=location_name)
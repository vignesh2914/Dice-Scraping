import time
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from dotenv import load_dotenv


def make_url(job_keyword: str, location_keyword: str, filter_option: int, num_of_pages: int):
    try:
        base_url = {
            1: 'https://www.dice.com/jobs?q={}&location={}&page={}&pageSize=20&language=en&eid=0904',
            2: 'https://www.dice.com/jobs?q={}&location={}&page={}&pageSize=20&filters.postedDate=SEVEN&language=en&eid=0904',
            3: 'https://www.dice.com/jobs?q={}&location={}&page={}&pageSize=20&filters.postedDate=THREE&language=en&eid=0904',
            4: 'https://www.dice.com/jobs?q={}&location={}&page={}&pageSize=20&filters.postedDate=ONE&language=en&eid=0904'
        }
       
        if 1 <= filter_option <= 4:
            user_selected_base_url = base_url[filter_option]
           
            final_urls = [] 
            for page in range(1, num_of_pages + 1):  
                url = user_selected_base_url.format(job_keyword, location_keyword, page)
                final_urls.append(url)  
 
            return final_urls  
        else:
            raise ValueError("Filter number must be between 1 and 4.")
    except Exception as e:
        print('An error occurred while making the URL: ', e)


def scrap_job_data(job_urls):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  
        cwd = os.getcwd()
        chromedriver_path = os.path.join(cwd, 'chromedriver.exe')
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)       

        job_data = []  # Create an empty list to store job data

        for url in job_urls:
            driver.get(url)
            time.sleep(5)  # Add a delay to ensure the page is fully loaded

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            jobs = soup.find_all('div', class_='d-flex justify-content-between title-container')

            for job in jobs:
                company_name = job.find('a', class_='ng-star-inserted').text.strip()
                job_title_element = job.find('div', class_='overflow-hidden')
                job_title = job_title_element.text.strip() if job_title_element else "Job Title not found"
                
                location_name = job_title.split(company_name)[-1].strip()
                if location_name:
                    job_title = job_title.replace(location_name, "").strip()
                
                if job_title.endswith(company_name):
                    job_title = job_title[0:len(job_title) - len(company_name)].strip()
                
                job_location_element = job.find('span', class_='search-result-location')
                job_location = job_location_element.text.strip() if job_location_element else "Location not found"
                
                job_data.append({"company_name": company_name, "job_title": job_title, "job_location": job_location})

        driver.quit()
        return job_data
   
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return None


# def scrap_job_data(url):
#     try:
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")  
#         cwd = os.getcwd()
#         chromedriver_path = os.path.join(cwd, 'chromedriver.exe')
#         service = Service(chromedriver_path)
#         driver = webdriver.Chrome(service=service, options=chrome_options)       

#         job_data = []  # Create an empty list to store job data

#         for url in job_urls:
#             driver.get(url)
#             time.sleep(5)  # Add a delay to ensure the page is fully loaded

#             page_source = driver.page_source
#             soup = BeautifulSoup(page_source, 'html.parser')

#             jobs = soup.find_all('div', class_='d-flex justify-content-between title-container')

#             for job in jobs:
#                 company_name = job.find('a', class_='ng-star-inserted').text.strip()
#                 job_title = job.find('div', class_='overflow-hidden').text.strip()
#                 job_location_element = job.find('span', class_='search-result-location')
#                 job_location = job_location_element.text.strip() if job_location_element else "Location not found"
#                 job_data.append({"company_name": company_name, "job_title": job_title, "job_location": job_location})

#         driver.quit()
#         return job_data
   
#     except Exception as e:
#         print(f"An error occurred during scraping: {e}")
#         return None
    
    
def create_dataframe_of_job_data():

    job_data = scrap_job_data(job_urls)
    if job_data:
        df = pd.DataFrame(job_data)
        return df
    else:
        print("No job data available.")
        return None

  


job_urls = make_url('python', 'canada', 1, 2)
print(job_urls)

job_data = scrap_job_data(job_urls)
print(job_data)

job_df = create_dataframe_of_job_data()
print(job_df.head(1000))  


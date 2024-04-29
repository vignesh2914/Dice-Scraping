import os
import time
import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from database import connect_to_mysql_database, create_cursor_object
from dotenv import load_dotenv
from utils import get_current_utc_datetime, extract_utc_date_and_time


def configure():
    load_dotenv()


configure()
host = os.getenv("database_host_name")
user = os.getenv("database_user_name")
password = os.getenv("database_user_password")
database = os.getenv("database_name")



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
        logging.error('An error occurred while making the URL: %s', e)  # Log the error


def scrap_job_data(job_urls):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  
        cwd = os.getcwd()
        chromedriver_path = os.path.join(cwd, 'chromedriver.exe')
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)       

        job_data = [] 

        for url in job_urls:
            driver.get(url)
            time.sleep(5) 

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
        logging.error("An error occurred during scraping: %s", e)  
        return None


def create_dataframe_of_job_data(job_data):
    if job_data:
        df = pd.DataFrame(job_data)
        return df
    else:
        logging.warning("No job data available.")  
        return None
    
def get_unique_companies_df(df: pd.DataFrame, column_name: str) -> pd.DataFrame:

    try:
        #data_frame = create_dataframe_of_job_data(job_data)
        filtered_df = df.drop_duplicates(subset=[column_name])
        logging.info("unique company name dataframe created")
        return filtered_df
    except Exception as e:
        logging.error(f"An error occurred: {e}")


def save_job_data_dataframe_to_mysql(df: pd.DataFrame) -> None:
    try:
        mydb = connect_to_mysql_database(host, user, password, database)
        cursor = create_cursor_object(mydb)

        utc_datetime = get_current_utc_datetime()
        date, time = extract_utc_date_and_time(utc_datetime)

        for index, row in df.iterrows():
            sql = "INSERT INTO dice.job_data (DATE, TIME, company_name, job_title, job_location) VALUES (%s,%s,%s, %s, %s)"
            values = (date, time, row['company_name'], row['job_title'], row['job_location'])
            cursor.execute(sql, values)
            logging.info("Job details saved in DB successfully")

        mydb.commit()
        mydb.close()
        logging.info("DB closed successfully")

    except Exception as e:
        logging.error(f"An error occurred: {e}")


def save_filtered_job_data_dataframe_to_mysql(df: pd.DataFrame) -> None:

    try:
        mydb = connect_to_mysql_database(host, user, password, database)
        cursor = create_cursor_object(mydb)

        utc_datetime = get_current_utc_datetime()
        date, time = extract_utc_date_and_time(utc_datetime)

        for index, row in df.iterrows():
            sql = "INSERT INTO dice.job_filtered_data (DATE, TIME, company_name, job_title, job_location) VALUES (%s,%s,%s, %s, %s)"
            values = (date, time, row['company_name'], row['job_title'], row['job_location'])
            cursor.execute(sql, values)
            logging.info("Job details saved in DB successfully")

        mydb.commit()
        mydb.close()
        logging.info("DB closed successfully")

    except Exception as e:
        logging.error(f"An error occurred: {e}")








job_urls = make_url('python', 'canada', 1, 1)
logging.info("Job URLs: %s", job_urls)  # Log the job URLs

job_data = scrap_job_data(job_urls)
logging.info("Job data: %s", job_data)  

job_df = create_dataframe_of_job_data(job_data)
print(job_df)

unique_companies_df = get_unique_companies_df(job_df, "company_name")
print(unique_companies_df)

save_job_data_dataframe_to_mysql(job_df)

save_filtered_job_data_dataframe_to_mysql(unique_companies_df)




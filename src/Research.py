import os
import time
import pandas as pd
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from database import connect_to_mysql_database, create_cursor_object
from dotenv import load_dotenv
from utils import get_current_utc_datetime, extract_utc_date_and_time
from webdriver_manager.chrome import ChromeDriverManager
import concurrent.futures  # New line added

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

def scrape_single_page(url):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        driver.get(url)
        time.sleep(5)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        jobs = soup.find_all('div', class_='d-flex justify-content-between title-container')

        job_data = []

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

def scrap_job_data(job_urls):
    job_data = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:  # New line added
        future_to_url = {executor.submit(scrape_single_page, url): url for url in job_urls}  # New line added
        for future in concurrent.futures.as_completed(future_to_url):  # New line added
            try:
                data = future.result()  # New line added
                if data:
                    job_data.extend(data)  # New line added
            except Exception as e:
                logging.error("An error occurred: %s", e)  # New line added

    return job_data

def create_dataframe_of_job_data(job_data):
    if job_data:
        df = pd.DataFrame(job_data)
        return df
    else:
        logging.warning("No job data available.")
        return None

def get_unique_companies_df(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    try:
        filtered_df = df.drop_duplicates(subset=[column_name])
        logging.info("Unique company name dataframe created")
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
        logging.error(f"An error occurred: %e")

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
        logging.error(f"An error occurred: %e")

def save_job_data_to_csv(job_data: List) -> None:
    try:
        if job_data:
            column_names = ["ID", "DATE", "TIME", "company_name", "job_title", "job_location"]
            df = pd.DataFrame(job_data, columns=column_names)
            
            df["ID"] = range(1, len(df) + 1)
            df["DATE"] = datetime.now().strftime("%Y-%m-%d")
            df["TIME"] = datetime.now().strftime("%H:%M:%S")
        
            folder_name = "Job_Data"
            os.makedirs(folder_name, exist_ok=True)  # New line added
            current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            csv_file_path = os.path.join(folder_name, f"{current_datetime}.csv")

            df.to_csv(csv_file_path, index=False)
            logging.info("Fetched job data saved in CSV file successfully")
        else:
            logging.info("No recent data found to save.")
    except Exception as e:
        logging.error(f"An error occurred: %e")

def save_unique_job_data_to_csv(job_filtered_data: pd.DataFrame) -> None:
    try:
        if not job_filtered_data.empty:
            column_names = ["ID", "DATE", "TIME", "company_name", "job_title", "job_location"]
            df = pd.DataFrame(job_filtered_data, columns=column_names)
            
            df["ID"] = range(1, len(df) + 1)
            df["DATE"] = datetime.now().strftime("%Y-%m-%d")
            df["TIME"] = datetime.now().strftime("%H:%M:%S")
        
            folder_name = "Unique_Job_Data"
            os.makedirs(folder_name, exist_ok=True)  # New line added

            current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            csv_file_path = os.path.join(folder_name, f"{current_datetime}.csv")

            df.to_csv(csv_file_path, index=False)
            logging.info("Unique job data saved in CSV file successfully")
        else:
            logging.info("No unique data found to save.")
    except Exception as e:
        logging.error(f"An error occurred: %e")

job_urls = make_url('developer', 'new york', 1, 5)
job_data = scrap_job_data(job_urls)
df = create_dataframe_of_job_data(job_data)
save_job_data_to_csv(job_data)
unique_df = get_unique_companies_df(df, 'company_name')
save_unique_job_data_to_csv(unique_df)

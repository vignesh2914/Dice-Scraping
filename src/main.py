import os
from scraper import generate_job_url, scrape_job_data

def main():
    try:
        job_url = generate_job_url(job_keyword='python', location_keyword='canada', filter_option=1)

        job_data = scrape_job_data(job_url, max_pages=100, time_limit=120)

        print("Job URL:", job_url)

        print("Scraped Job Data:", job_data)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

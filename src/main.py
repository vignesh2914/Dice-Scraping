from scraper import (
                    make_url,
                    scrap_job_data, 
                    create_dataframe_of_job_data, 
                    get_unique_companies_df, 
                    save_job_data_dataframe_to_mysql, 
                    save_filtered_job_data_dataframe_to_mysql
)

job_urls = make_url('Developer', 'canada', 1, 2)

job_data = scrap_job_data(job_urls)

job_df = create_dataframe_of_job_data(job_data)

unique_companies_df = get_unique_companies_df(job_df, "company_name")

save_job_data_dataframe_to_mysql(job_df)

save_filtered_job_data_dataframe_to_mysql(unique_companies_df)
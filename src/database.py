import mysql.connector as conn
import pandas as pd
from dotenv import load_dotenv
import os

def configure():
    load_dotenv()


configure()
host = os.getenv("database_host_name")
user = os.getenv("database_user_name")
password = os.getenv("database_user_password")
database = os.getenv("database_name")

 
def create_database(host, user, password):
    try:
        mydb = conn.connect(host=host, user=user, password=password)
        cursor = mydb.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS dice")
        print("Database created successfully")
    except Exception as e:
        print(f"An error occurred while creating database: {e}")


def connect_to_mysql_database(host, user, password, database):
    try:
        mydb = conn.connect(host=host, user=user, password=password, database=database)
        print("Connected to MySQL successfully!")
        return mydb
    except Exception as e:
        print(f"An error occurred: {e}")
   
def create_cursor_object(mydb):
    try:
        cursor = mydb.cursor()
        print("Cursor object obtained successfully!")
        return cursor
    except Exception as e:
        print(f"An error occurred: {e}")

def create_tables(host, user, password, database):
    try:
        mydb = connect_to_mysql_database(host, user, password, database)
        cursor = create_cursor_object(mydb)
        table_queries = [
            """
            CREATE TABLE IF NOT EXISTS dice.job_data(
                ID INT AUTO_INCREMENT PRIMARY KEY,
                DATE DATE,
                TIME TIME,
                COMPANY_NAME VARCHAR(255),
                JOB_TITLE VARCHAR(255),
                JOB_LOCATION VARCHAR(255)  
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS dice.job_filtered_data(
                ID INT AUTO_INCREMENT PRIMARY KEY,
                DATE DATE,
                TIME TIME,
                COMPANY_NAME VARCHAR(255),
                JOB_TITLE VARCHAR(255),
                JOB_LOCATION VARCHAR(255) 
            )
            """,
        ]
 
        # Execute table creation queries
        for query in table_queries:
            cursor.execute(query)
 
        print("Tables and columns created successfully")
    except Exception as e:
        print(f"An error occurred: {e}")



# mydb = connect_to_mysql_database(host, user, password, database)
# cursor = create_cursor_object(mydb)

# create_tables(host, user, password, database)

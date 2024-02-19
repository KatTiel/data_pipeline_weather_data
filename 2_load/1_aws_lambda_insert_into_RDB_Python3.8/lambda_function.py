import boto3
import logging
import os
import pandas as pd
import psycopg2 as ps
import sys
from io import StringIO

# RDB and S3 settings
user_name = os.environ['USER_NAME']
password = os.environ['PASSWORD']
host = os.environ['HOST']
db_name = os.environ['DB_NAME']
port = os.environ['PORT']
s3_bucket = os.environ['BUCKET']
s3_key = 'weather_data.csv'

# Initiate logger for logging feedback and easier debugging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Set S3 client
s3_client = boto3.client('s3')

# Connect to AWS RDS PostgreSQL database 
try:
    conn2 = ps.connect(
        dbname=db_name,
        user=user_name,
        password=password,
        host=host,
        port=port
    )
    conn2.autocommit = True
    cur = conn2.cursor()
    print('Connection to AWS RDS established.')
except ps.Error as e:
    logging.error("ERROR: Could not connect to AWS RDS.")
    logging.error(e)
    sys.exit(1)

logging.info("SUCCESS: Connection to AWS RDS succeeded.")

# Define lambda_handler function
def lambda_handler(event, context):
    # Retrieve the weather_data.csv file from S3 bucket
    try:
        s3_Bucket_Name = event["Records"][0]["s3"]["bucket"]["name"]
        s3_File_Name = event["Records"][0]["s3"]["object"]["key"]
        
        object = s3_client.get_object(Bucket=s3_Bucket_Name, Key=s3_File_Name)
        body = object['Body']
        csv_string = body.read().decode('utf-8')
        dataframe = pd.read_csv(StringIO(csv_string))
        print(dataframe.head(3))
    except Exception as err:
        print(err)

    # Insert current weather data into current_weather table
    try:
        logging.info("Inserting data into current_weather table...")
        for i, row in dataframe.iterrows():
            cur.execute(
                "insert into current_weather (city_name, date_column, \"main.temp\", \"rain.1h\", Y) values (%s, %s, %s, %s, %s) on conflict (city_name) do update set date_column = excluded.date_column, \"main.temp\" = excluded.\"main.temp\", \"rain.1h\" = excluded.\"rain.1h\", Y = excluded.Y",
                (row['city_name'], row['date_column'], row['main.temp'], row['rain.1h'], row['Y']))
        logging.info("Data successfully inserted into current_weather table.")
    except Exception as e:
        logging.error(f"Error while inserting data into table: {e}")
        return False
        
    # Move data from current_weather table into combined_filtered_weather_history_2024 table
    try:
        logging.info("Moving data into combined_filtered_weather_history_2024 table...")
        cur.execute("insert into combined_filtered_weather_history_2024 select * from current_weather")
        logging.info("Data moved successfully.")
    except Exception as e:
        logging.error(f"Error while moving the data: {e}")
        return False

    # Delete CSV from S3 bucket   
    try:
        logging.info("Deleting CSV file from S3...")
        s3_client.delete_object(Bucket=s3_bucket, Key=s3_key)
        logging.info('CSV file successfully deleted from S3.')
    except Exception as e:
        logging.error(f'Error deleting CSV from S3: {e}')
        return False
        
    # Commit changes and close AWS RDS connections
    try:
        logging.info("Committing changes...")
        conn2.commit()
        cur.close()
        conn2.close()
        logging.info("Changes committed and connections closed.")
    except Exception as e:
        logging.error(f"Error during commit or closing connections: {e}")
        return False

    return True

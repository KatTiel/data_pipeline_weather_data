import datetime
import logging
import os
import pandas as pd
import requests
import boto3
from botocore.exceptions import NoCredentialsError

# Initiate logger for logging feedback and easier debugging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define variables
weather_api_key = os.environ['WEATHER_API_KEY']
s3_bucket_name = os.environ['BUCKET']

# Define lambda_handler function for OpenWeather API call
def lambda_handler(event, context):
    locations = pd.DataFrame({
        'city_name': ['Berlin', 'Tulum', 'Ko Tao', 'Parque Nacional Corcovado', 'San Diego'],
        'latitude': [52.520007, 20.211419, 10.095610, 8.540835, 32.715738],
        'longitude': [13.404954, -87.465350, 99.840396, -83.570964, -117.161084]
    })

    openweathermap_api_key = weather_api_key

    def current_weather(city_name, latitude, longitude):
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={openweathermap_api_key}"
        response = requests.get(url)
        response_json = response.json()
        date = datetime.datetime.fromtimestamp(response_json["dt"])
        today = date.today()
        today_year = today.year
        return {
            "city_name": city_name,
            "date_column": date,
            "main.temp": response_json["main"]["temp"] - 273.15,
            "rain.1h": response_json.get("rain", {}).get("1h", 0.0),
            "Y": today_year
        }

    # Create a list to store the curent weather data for each city
    weather_data = []

    # Iterate through each city and request current weather data
    for index, row in locations.iterrows():
        city_data = current_weather(row['city_name'], row['latitude'], row['longitude'])
        weather_data.append(city_data)

    # Create a DataFrame from the requested data and convert it to CSV
    combined_df = pd.DataFrame(weather_data)
    csv_data = combined_df.to_csv(index=False)

    # Save CSV data to S3 bucket
    s3 = boto3.client('s3')
    try:
        s3.put_object(Body=csv_data, Bucket=s3_bucket_name, Key='weather_data.csv')
        logger.info("Weather data successfully saved to S3 bucket.")
    except NoCredentialsError:
        logger.error("Credentials are not available to save data to S3 bucket.")

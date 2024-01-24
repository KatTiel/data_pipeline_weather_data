from prefect import flow, task
import datetime
import json
import pandas as pd
import requests
import pandas.io.sql as sqlio 
import psycopg2 as ps

f = open("credentials.json")
credentials = json.load(f)

my_path = list(credentials.values())[0]
weather_key = list(credentials.values())[1]
aws_access_key = list(credentials.values())[2]
aws_secret_key = list(credentials.values())[3]
rds_host = list(credentials.values())[4]
rds_user = list(credentials.values())[5]
rds_password = list(credentials.values())[6]
rds_database = list(credentials.values())[7]
rds_charset = list(credentials.values())[8]
rds_port = list(credentials.values())[9]

# Request current weather data and insert the data into AWS postgresql RDS 
@task
def current_weather_request():
    try:
        conn2 = ps.connect(dbname = rds_database, 
                           user = rds_user, 
                           password = rds_password, 
                           host = rds_host, 
                           port = rds_port)
        conn2.autocommit = True
        cur = conn2.cursor()
        print('Connection established.')
    except:
        print("Error while connecting to PostgreSQL.")

    locations = pd.DataFrame({
        'city_name': ['Berlin', 'Tulum', 'Ko Tao', 'Parque Nacional Corcovado', 'San Diego'],
        'latitude': [52.520007, 20.211419, 10.095610, 8.540835, 32.715738],
        'longitude': [13.404954, -87.465350, 99.840396, -83.570964, -117.161084]
    })
    openweathermap_api_key = weather_key

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

    # Create a list to store the results for each city
    weather_data = []

    # Iterate through each city and request weather data
    for index, row in locations.iterrows():
        city_data = current_weather(row['city_name'], row['latitude'], row['longitude'])
        weather_data.append(city_data)

    # Create a DataFrame from the list of results and print it
    combined_df = pd.DataFrame(weather_data)
    print(combined_df)
    
    # Create RDS tables for current_weather, combined_combined_filtered_weather_history_2024 table and filtered_weather_history for all cities.
    # SQL code can be found in the /load directory

    # Insert current weather data into table
    try:
        for i, row in combined_df.iterrows():
            cur.execute(
                "insert into current_weather (city_name, date_column, \"main.temp\", \"rain.1h\", Y) values (%s, %s, %s, %s, %s) on conflict (city_name) do update set date_column = excluded.date_column, \"main.temp\" = excluded.\"main.temp\", \"rain.1h\" = excluded.\"rain.1h\", Y = excluded.Y",
                (row['city_name'], row['date_column'], row['main.temp'], row['rain.1h'], row['Y']))
        print("Data inserted or updated successfully in current_weather")
    except:
        print("Error while inserting or updating data in table")

    # Move data into combined_filtered_weather_history_2024 table
    try:
        cur.execute("insert into combined_filtered_weather_history_2024 select * from current_weather")
        print("Data moved successfully")
    except:
        print("Error while moving the data")

    conn2.commit()    
    cur.close()
    conn2.close()

# Define the flow
@flow(name='current_weather_flow_private',log_prints=True)
def flow_run():
    current_weather_request()
    
flow_run()
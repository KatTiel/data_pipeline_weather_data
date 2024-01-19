/* Create a table for the current weather. This data is automatically transfered 
into the combined_filtered_weather_history_2024 table
*/
CREATE TABLE IF NOT EXISTS current_weather (
    city_name VARCHAR(255) PRIMARY key,
    date_column TIMESTAMP,
    "main.temp" FLOAT8,
    "rain.1h" FLOAT8,
    Y INT
   );

/* 
 Create a table for the current year to continuously receive data from the current_weather table.
 The collected data serves for mean annual temp/rainfall analysis at the end of the year
 */

CREATE TABLE IF NOT EXISTS combined_filtered_weather_history_2024 (
    city_name VARCHAR(255),
    date_column TIMESTAMP,
    "main.temp" FLOAT8,
    "rain.1h" FLOAT8,
    Y INT,
    FOREIGN KEY (city_name) REFERENCES current_weather(city_name)
   );

/*
 Insert city name for CITY
 */

CREATE TABLE IF NOT EXISTS CITY_filtered_weather_history (
    city_name VARCHAR(255),
    date_column TIMESTAMP,
    "main.temp" FLOAT8,
    "rain.1h" FLOAT8,
    Y INT,
    FOREIGN KEY (city_name) REFERENCES current_weather(city_name)
   );

/* 
After creating the last table, import csv filtered_weather_history via DBeaver or other database management programs
*/
 

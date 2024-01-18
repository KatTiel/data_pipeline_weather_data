/*
 Insert city name for CITY
 */

CREATE TABLE IF NOT EXISTS CITY_filtered_weather_history (
    city_name VARCHAR(255),
    date_column TIMESTAMP,
    "main.temp" FLOAT8,
    "rain.1h" FLOAT8,
    Y INT,
    FOREIGN KEY (city_name) REFERENCES weather_current(city_name)
);

/* 
After creating the table, import csv filtered_weather_history via DBeaver or other database management programs
*/
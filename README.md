## ETL Data Pipeline For Current and Historical Weather Data :sunrise_over_mountains:
This project aims at analyzing yearly temperature and rainfall changes since 1979.
I decided to take a look on five beautiful places in the world - **Berlin, Ko Tao, Parque Nacional Corcovado, San Diego and Tulum**.
It is split into two parts - historical and current weather data collection and analysis.

### Prerequisites 
- [OpenWeather Free API Key](https://openweathermap.org/appid) 1000 API calls per day for ***free***.
- [Amazon Web Service Account](https://aws.amazon.com/de/) There is a ***free tier*** option but definitely check out the AWS cost explorer as some ***additional costs might arise***.
-- [AWS RDS PostgreSQL Database](https://www.youtube.com/watch?v=Ng_zi11N4_c) You can follow the steps in the video and choose PostgreSQL instead of MySQL for this project
-- [AWS S3](https://www.youtube.com/watch?v=e6w9LwZJFIA)
-- [AWS Lambda](https://www.youtube.com/watch?v=eOBq__h4OJ4)
- A database administration tool, for example [DBeaver 23.3.5](https://dbeaver.io) which has to be [connected to your AWS RDS Database](https://www.youtube.com/watch?v=_Yzr7yBGWQI&ab_channel=AWSMadeEasy)
- [Python 3.11](https://www.python.org/downloads/release/python-3110/)
- Jupyter Notebook ```pip install notebook ```

### Architecture
<img width="815" alt="workflow_weather" src="https://github.com/KatTiel/data_pipeline_weather_data/assets/76701992/d0df9557-2b55-41d5-a52b-1d33122fde6a">

### How It Works 
#### Historical Weather Data
##### Extract
- [Download historical weather data](https://home.openweathermap.org/history_bulks/new) of your cities of interest as .json - ***9€/location***
- Save the data as "weather_history_bulk.json"

##### Transform
- Create an AWS S3 bucket for historical weather data 
- Configure a credentials.json file containing all values which are required in the historical_weather_data.ipynb file
- [Install the required dependencies](https://github.com/KatTiel/data_pipeline_weather_data/tree/main/1_transform) by executing ```pip install -r requirements.txt ```
- [Run the Jupyter notebook for historical data transformation](https://github.com/KatTiel/data_pipeline_weather_data/tree/main/1_transform)

##### Load 
- Using DBeaver, create RDS weather tables by executing the queries provided in the [.sql file](https://github.com/KatTiel/data_pipeline_weather_data/tree/main/2_load)
- In DBeaver, import the historical weather data into the designated table for each city

#### Current Weather Data
This part of the project is accomplished by using two different AWS Lambda functions. 
The initial function is scheduled to execute every hour automatically, while the second function triggers upon the upload of a .csv file into the designated S3 bucket. This upload marks the concluding step of the first function's execution.

AWS Lambda functions need to be initialized with a specific Python runtime. If additional dependencies, such as psycopg2 for database connections, are required, [they must to be uploaded, along with the lambda_function](https://www.youtube.com/watch?v=Jtlxf_kn5zY&ab_channel=DevAndBeyond). Pandas should be integrated as an AWS Lambda function layer  rather than being part of the uploaded dependencies.

:exclamation:I highly recommend downloading the approach of downloading dependencies for the second AWS Lambda load function in Python 3.8 runtime [as shown in the video](https://www.youtube.com/watch?v=80h9lXE07z0&ab_channel=ZyroTech) as it resolves several compatibility issues encountered with alternative methods.:exclamation:

##### Extract & Transform
**AWS Lambda :exclamation:Python 3.10:exclamation:**
- Create an AWS Lambda function in Python 3.10 runtime
- Add Pandas 3.10 layer
- Upload the [function and its dependencies](https://github.com/KatTiel/data_pipeline_weather_data/tree/main/0_extract) as a .zip file, as described in the [video](https://www.youtube.com/watch?v=Jtlxf_kn5zY&ab_channel=DevAndBeyond)
- Create an [AWS CloudWatch Event](https://www.youtube.com/watch?v=-WyNf_8Ke4E&ab_channel=BeABetterDev) to activate the function at hourly intervals

##### Load
**AWS Lambda :exclamation:Python 3.8:exclamation:**
- Create an AWS Lambda function in Python 3.8 runtime
- Add Pandas 3.8 layer
- Download the required dependencies [as described here](https://www.youtube.com/watch?v=80h9lXE07z0&ab_channel=ZyroTech), using AWS Cloud9
- Upload the [function and its dependencies](https://github.com/KatTiel/data_pipeline_weather_data/tree/main/2_load/aws_lambda_insert_into_RDB_Python3.8) as a .zip file, as described in the [video](https://www.youtube.com/watch?v=80h9lXE07z0&ab_channel=ZyroTech)
- [Add an event trigger](https://www.youtube.com/watch?v=OJrxbr9ebDE) to invoke the function whenever a .csv file is uploaded into the S3 bucket  

### License
[MIT](https://choosealicense.com/licenses/mit/)

Have fun collecting weather data for your personal analysis!:herb:
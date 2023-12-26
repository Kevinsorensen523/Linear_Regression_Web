from flask import Flask, jsonify
import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
CORS(app, origins=["http://localhost:3000"])  # Allow only requests from http://localhost:3000

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

filtered_data = None
sales_data = None

# Load sales data
file_path = 'DatasetSalesCoffeeShop.csv'
sales_data = pd.read_csv(file_path, sep=";")

@app.route('/api/get_weather_data')
def get_weather_data():
    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": -6.1781,
        "longitude": 106.63,
        "start_date": "2023-07-11",
        "end_date": "2023-11-30",
        "hourly": "temperature_2m"
    }

    try:
        global filtered_data
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]

        # Process hourly data
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s"),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )}
        hourly_data["temperature_2m"] = hourly_temperature_2m

        hourly_dataframe = pd.DataFrame(data=hourly_data)

        filtered_data = hourly_dataframe[hourly_dataframe['date'].dt.time == pd.to_datetime('10:00:00').time()]
        average_temperature  = filtered_data['temperature_2m'].mean()
        filtered_data['temperature_2m'].fillna(average_temperature, inplace=True)
        filtered_data['date'] = filtered_data['date'].dt.date
        
        # Convert DataFrame to JSON and return
        return jsonify(filtered_data.to_dict(orient='records'))

    except Exception as e:
        return jsonify({"error": str(e)})
    

@app.route('/api/get_sales_data')
def get_sales_data():
    try:
        global sales_data
        # Return sales data as JSON
        return jsonify(sales_data.to_dict(orient='records'))

    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route('/api/get_merged_data')
def get_merged_data():
    try:
        global filtered_data, sales_data
        if filtered_data is None or sales_data is None:
            # If not, call the functions to get the data
            get_weather_data()
            get_sales_data()
        
        filtered_data.rename(columns={'temperature_2m': 'Temperature At 10 AM'}, inplace=True)

        filtered_data['date'] = pd.to_datetime(filtered_data['date'])

        sales_data['Date'] = pd.to_datetime(sales_data['Date'], format='%d/%m/%Y')

        merged_data = pd.merge(filtered_data, sales_data, left_on='date', right_on='Date', how='inner')

        merged_data.drop('Date', axis=1, inplace=True)

        return jsonify(merged_data.to_dict(orient='records'))
    
    
    except Exception as e:
        return jsonify({"error": str(e)})    
        

if __name__ == '__main__':
    app.run(debug=True)

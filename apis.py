import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import requests
import json


def get_weather_info(latitude, longitude):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ["temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min"],
        "hourly": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation_probability", "wind_speed_10m"],
        "timezone": "Europe/Berlin",
        "forecast_days": 1,
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
    hourly_apparent_temperature = hourly.Variables(2).ValuesAsNumpy()
    hourly_precipitation_probability = hourly.Variables(3).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(4).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
    hourly_data["apparent_temperature"] = hourly_apparent_temperature
    hourly_data["precipitation_probability"] = hourly_precipitation_probability
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

    hourly_dataframe = pd.DataFrame(data = hourly_data)

    # Add hour column extracted from the date column
    hourly_dataframe['hour'] = hourly_dataframe['date'].dt.hour
    day_data = hourly_dataframe[(hourly_dataframe['hour'] >= 8) & (hourly_dataframe['hour'] <= 19)]
    night_data = hourly_dataframe[(hourly_dataframe['hour'] > 19) & (hourly_dataframe['hour'] < 22)]

    # Extract the date (without time) from the first entry
    forecast_date = day_data['date'].iloc[0].date()
    
    weather_info = {
        "date": forecast_date,
        "max_temperature_day": day_data['temperature_2m'].max(),
        "min_temperature_day": day_data['temperature_2m'].min(),
        "max_relative_humidity_day": day_data['relative_humidity_2m'].max(),
        "min_relative_humidity_day": day_data['relative_humidity_2m'].min(),
        "max_apparent_temperature_day": day_data['apparent_temperature'].max(),
        "min_apparent_temperature_day": day_data['apparent_temperature'].min(),
        "max_precipitation_probability_day": day_data['precipitation_probability'].max(),
        "min_precipitation_probability_day": day_data['precipitation_probability'].min(),
        "max_temperature_night": night_data['temperature_2m'].max(),
        "min_temperature_night": night_data['temperature_2m'].min(),
        "max_relative_humidity_night": night_data['relative_humidity_2m'].max(),
        "min_relative_humidity_night": night_data['relative_humidity_2m'].min(),
        "max_apparent_temperature_night": night_data['apparent_temperature'].max(),
        "min_apparent_temperature_night": night_data['apparent_temperature'].min(),
        "max_precipitation_probability_night": night_data['precipitation_probability'].max(),
        "min_precipitation_probability_night": night_data['precipitation_probability'].min(),
    }

    return weather_info


def get_random_quote():
    """
    Fetches a random quote from the ZenQuotes API and returns a dictionary
    with the quote content and author.
    
    Returns:
        dict: Dictionary containing 'quote' and 'author' keys
    """
    url = "https://zenquotes.io/api/random"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        # Parse the JSON response
        data = response.json()
        
        # Extract quote and author from the first (and only) item in the list
        quote_data = data[0]
        
        return {
            "quote": quote_data["q"],  # ZenQuotes uses 'q' for quote
            "author": quote_data["a"]  # ZenQuotes uses 'a' for author
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching quote: {e}")
        return {
            "quote": "Error fetching quote",
            "author": "Unknown"
        }
    except (KeyError, IndexError) as e:
        print(f"Error parsing quote data: {e}")
        return {
            "quote": "Error parsing quote data",
            "author": "Unknown"
        }


def get_random_fact():
    """
    Fetches a random useless fact from the uselessfacts API and returns
    the fact text as a string.
    
    Returns:
        str: The random fact text
    """
    url = "https://uselessfacts.jsph.pl/random.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        # Parse the JSON response
        data = response.json()
        
        # Extract the fact text
        return data["text"]
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching fact: {e}")
        return "Error fetching fact"
    except KeyError as e:
        print(f"Error parsing fact data: {e}")
        return "Error parsing fact data"
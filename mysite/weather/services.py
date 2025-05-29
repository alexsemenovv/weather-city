import json
import os
from typing import Dict, Optional

import openmeteo_requests
import pandas as pd
import requests
import requests_cache
from retry_requests import retry

API_KEY = os.getenv("GEOAPIFY_KEY")


def create_session():
    """Создание клиента сессии"""
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    return openmeteo


def get_location_coordinates(location: str) -> Optional[tuple]:
    """

    :param location (str) - Название локации
    :return: Кортеж из долготы и широты | None
    """
    url = "https://api.geoapify.com/v1/geocode/search"
    params = dict(
        text=location,
        apiKey=API_KEY,
    )
    response = requests.get(url=url, params=params)
    if response.status_code == 200:
        data = json.loads(response.text)
        if len(data["features"]) > 0:
            location_data = data["features"][0]["properties"]
            return location_data["lat"], location_data["lon"]
        else:
            return None
    else:
        return None


def get_weather_by_latitude_and_longitude(lat: float, long: float) -> Optional[Dict]:
    """
    Поиск погоды при помощи open-meteo API, по переданным - долготе и широте
    :param lat(float) - широта локации
    :param long(float) - долгота локации
    :return: Словарь с параметрами погоды найденной локации | None
    """
    client = create_session()
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": long,
        "hourly": ["temperature_2m", "apparent_temperature", "wind_speed_10m", "rain"],
        "timezone": "auto",
        "wind_speed_unit": "ms",
    }
    responses = client.weather_api(url, params=params)
    response = responses[0]
    if not response:
        return None
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_apparent_temperature = hourly.Variables(1).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(2).ValuesAsNumpy()
    hourly_rain = hourly.Variables(3).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        )
    }

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["apparent_temperature"] = hourly_apparent_temperature
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
    hourly_data["rain"] = hourly_rain

    hourly_dataframe = pd.DataFrame(data=hourly_data)

    decoded_timezone = response.Timezone().decode("utf-8")
    result = {
        "Coordinates": {
            "latitude": response.Latitude(),
            "longitude": response.Longitude(),
        },
        "Elevation": response.Elevation(),
        "Timezone": decoded_timezone,
        "Timezone_diff_GMT_0": response.UtcOffsetSeconds(),
        "hourly_dataframe": hourly_dataframe.to_json(orient="records"),
    }
    return result

import json
from typing import Dict, List

import pandas as pd
from django.contrib.sessions.backends.db import SessionStore
from django.core.exceptions import BadRequest

from .models import City
from .services import get_location_coordinates, get_weather_by_latitude_and_longitude


def save_or_increase_count_location(location: str) -> None:
    """
    Ищет локацию в БД.
    Если такая локация есть - то увеличивает счетчик просмотров,
    иначе - создаёт новую запись.
    :param location(str) - Локация
    :return: None
    """
    location = location.capitalize()
    city = City.objects.filter(name=location).first()
    if city:
        city.count += 1
    else:
        city = City(name=location)
    city.save()


def update_search_history(session: SessionStore, location: str, weather_data: Dict, hourly_data: List) -> None:
    """
    Обновляет историю поиска
    :param session: Сессия пользователя
    :param location: str - Локация
    :param weather_data: Dict - словарь с данными о погоде
    :param hourly_data: List - список с данными о погоде по часам
    :return: None
    """
    history = session.get("search_history", [])
    history.append({
        "location": location,
        "weather_data": weather_data,
        "hourly": hourly_data,
    })
    if len(history) > 10:
        history = history[-10:]
    session["search_history"] = history


def prepare_weather_data(location: str) -> tuple[dict, list[dict]]:
    """
    Подготовка данных по выбранной локации
    :param location: str - Локация
    :return: tuple - Кортеж с данными о погоде, данными о погоде по часам
    """
    coordinates = get_location_coordinates(location)
    if not coordinates:
        raise BadRequest(f"Location {location} not found")

    save_or_increase_count_location(location=location)
    latitude, longitude = coordinates
    weather_data = get_weather_by_latitude_and_longitude(latitude, longitude)

    hourly_json = weather_data.get("hourly_dataframe")
    hourly_data = json.loads(hourly_json)
    hourly_table = pd.DataFrame(hourly_data)
    hourly_table["date"] = pd.to_datetime(hourly_table["date"], unit="ms").dt.strftime("%Y-%m-%d %H:%M")

    for col in hourly_table.columns:
        if col != "date" and col != "rain":
            hourly_table[col] = hourly_table[col].round(0).astype(int)
        elif col == "rain":
            hourly_table[col] = hourly_table[col].round(2).astype(float)

    hourly_table_list = hourly_table.to_dict(orient="records")
    return weather_data, hourly_table_list

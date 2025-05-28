import json

import pandas as pd
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import BadRequest
from requests import session

from .forms import SearchCity
from .services import get_location_coordinates, get_weather_by_latitude_and_longitude


def city_form(request: HttpRequest) -> HttpResponse:
    """Получение локации"""
    # request.session.delete()
    if request.method == "POST":
        form = SearchCity(request.POST)
        if form.is_valid():
            location = form.cleaned_data.get('city')
            if "search_history" in request.session:
                search_history = request.session["search_history"]
            else:
                search_history = []

            coordinates = get_location_coordinates(location=location)
            if coordinates:
                latitude, longitude = coordinates
                weather_data = get_weather_by_latitude_and_longitude(latitude, longitude)
                hourly_json = weather_data.get("hourly_dataframe")
                hourly_data = json.loads(hourly_json)
                hourly_table = pd.DataFrame(hourly_data)
                hourly_table["date"] = pd.to_datetime(hourly_table["date"], unit="ms").dt.strftime("%Y-%m-%d %H:%M")
                hourly_table_list = hourly_table.to_dict(orient="records")
                request.session['weather_data'] = weather_data
                request.session['hourly'] = hourly_table_list
                request.session['location'] = location
                search_history.append({
                    "weather_data": weather_data,
                    "hourly": hourly_table_list,
                    "location": location,
                })
                if len(search_history) > 10:
                    search_history = search_history[-10:]
                request.session['search_history'] = search_history
            else:
                raise BadRequest(f"Location {location} is not find")
            return redirect(reverse("weather:result"))
    else:
        form = SearchCity()
        search_history = request.session.get('search_history')
    return render(request, 'weather/city-index.html',
                  context={"form": form, "search_history": search_history})


def get_weather_for_city(request: HttpRequest) -> HttpResponse:
    """Получение погоды для введённой локации"""
    weather_data = request.session.get("weather_data")
    hourly = request.session.get("hourly")
    location = request.session.get("location")
    context = {
        "weather_data": weather_data,
        "hourly": hourly,
        "location": location,
    }
    return render(request, "weather/result.html", context=context)


def get_weather_from_history(request: HttpRequest, index: int) -> HttpResponse:
    """
    Достаёт прогноз погоды из истории поиска
    :param request: HttpRequest
    :param index: int - индекс локации из request.session["search_history]
    :return: HttpResponse
    """
    search_history = request.session.get("search_history", [])
    if index < 0 or index >= len(search_history):
        raise Http404("Элемент истории не найден")
    location = search_history[index]
    context = {
        "weather_data": location["weather_data"],
        "hourly": location["hourly"],
        "location": location["location"],
    }

    return render(request, "weather/result.html", context=context)


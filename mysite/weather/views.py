from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import BadRequest

from .forms import SearchCity
from .utils import prepare_weather_data, update_search_history


def city_form(request: HttpRequest) -> HttpResponse:
    search_history = request.session.get("search_history", [])
    if request.method == "POST":
        form = SearchCity(request.POST)
        if form.is_valid():
            location = form.cleaned_data.get("city")
            try:
                weather_data, hourly_data = prepare_weather_data(location)
            except BadRequest as e:
                form.add_error("city", str(e))
            else:
                request.session["weather_data"] = weather_data
                request.session["hourly"] = hourly_data
                request.session["location"] = location
                update_search_history(request.session, location, weather_data, hourly_data)
                return redirect(reverse("weather:result"))
    else:
        form = SearchCity()
    return render(request, "weather/city-index.html", context={"form": form, "search_history": search_history})


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

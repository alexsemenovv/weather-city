from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def weather_index(request: HttpRequest) -> HttpResponse:
    """Эндпоинт для прогноза погоды"""
    return render(request, 'weather/weather-index.html')
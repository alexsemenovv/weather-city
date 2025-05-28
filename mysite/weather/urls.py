from django.urls import path

from .views import city_form, get_weather_for_city

app_name = 'weather'

urlpatterns = [
    path("city/", city_form, name='search_city'),
    path("result/", get_weather_for_city, name='result')
]

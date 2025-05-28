from django.urls import path

from .views import weather_index

appname = 'weather'

urlpatterns = [
    path("", weather_index, name='index')
]

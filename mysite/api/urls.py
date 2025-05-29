from django.urls import path
from .views import CityListView

app_name = "api"

urlpatterns = [
    path("city-count/", CityListView.as_view(), name="city_count"),
]

"""
Модуль для тестирования функций приложения api
"""

from django.test import TestCase
from django.urls import reverse

from weather.models import City


class CityListViewTestCase(TestCase):
    def setUp(self):
        data = [
            {"name": "Moscow", "count": 1},
            {"name": "Berlin", "count": 100},
            {"name": "Paris", "count": 999},
        ]
        City.objects.bulk_create(City(**kwargs) for kwargs in data)

    def test_city_list_view(self):
        """Тест на получение списка всех введённых локаций"""
        response = self.client.get(reverse("api:city_count"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Moscow")
        self.assertContains(response, "Berlin")
        self.assertEqual(response.json()["locations"]["Paris"], 999)

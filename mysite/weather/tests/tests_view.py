"""
Модуль для тестирования функций приложения weather
"""
from django.core.exceptions import BadRequest
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class CityFormTestCase(TestCase):
    @patch("weather.views.prepare_weather_data")
    def test_city_form_valid_city(self, mock_prepare_weather_data):
        """Тест при успешном вводе локации - перенаправление на страницу result/"""
        mock_prepare_weather_data.return_value = ({'temp': 20}, {'hourly': []})
        response = self.client.post(reverse("weather:search_city"), {"city": "Moscow"})
        self.assertRedirects(response, reverse("weather:result"))

    def test_city_form_not_valid(self):
        """Тест на получение ошибки валидации ввода локации с цифрами в форму"""
        response = self.client.post(reverse("weather:search_city"), {"city": "Mo66576scow"})
        self.assertEqual(response.context.get('form').errors.get("city")[0], "Локация должна содержать только буквы")

    @patch("weather.views.prepare_weather_data")
    def test_city_form_invalid_city_adds_error(self, mock_prepare_weather_data):
        """Тест на невалидное значение для ввода локации"""
        mock_prepare_weather_data.side_effect = BadRequest("Город не найден")

        response = self.client.post(reverse("weather:search_city"), {"city": "вамывамдтфывс"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "weather/city-index.html")

        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("city", form.errors)
        self.assertIn("Город не найден", form.errors["city"])

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_city(location: str) -> None:
    """Валидатор для обработки названия города"""
    if not location.isalpha():
        raise ValidationError(
            _(f"Локация должна содержать только буквы"), params={"location": location}
        )


class SearchCity(forms.Form):
    """Форма для ввода города"""

    city = forms.CharField(label="Название города", validators=[validate_city])

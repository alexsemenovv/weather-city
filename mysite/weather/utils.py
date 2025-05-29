from .models import City


def save_or_increase_count_location(location: str) -> None:
    """
    Ищет локацию в БД.
    Если такая локация есть - то увеличивает счетчик просмотров,
    иначе - создаёт новую запись.
    :param location(str) - Локация
    :return: None
    """
    city = City.objects.filter(name=location).first()
    if city:
        city.count += 1
    else:
        city = City(name=location)
    city.save()

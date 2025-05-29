from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from weather.models import City


class CityListView(APIView):
    def get(self, request: Request) -> Response:
        """Получение списка всех введённых локаций"""
        locations = City.objects.all()
        data = {
            loc.name: loc.count
            for loc in locations
        }
        return Response({"locations": data})

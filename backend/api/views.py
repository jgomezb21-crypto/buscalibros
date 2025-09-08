from typing import Any
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Registro
from .serializers import RegistroSerializer


@api_view(["GET"])  # GET /api/health/
@permission_classes([AllowAny])
def health(request: Request) -> Response:
    """Endpoint de vida: devuelve 200 con un payload simple."""
    return Response({"status": "OK"})


class RegistroViewSet(viewsets.ModelViewSet):
    """
    CRUD para Registro con soporte de:
      - Filtros exactos (?nombre=...)
      - Búsqueda de texto (?search=...)
      - Ordenamiento (?ordering=nombre,-id)
    """

    queryset = Registro.objects.all()
    serializer_class = RegistroSerializer

    # Habilita filter/search/ordering (coincide con REST_FRAMEWORK en settings)
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # Ajusta estos campos a tu modelo real
    filterset_fields = ["nombre"]  # p.ej.: ["nombre", "autor", "area", "codigo"]
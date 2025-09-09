from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Registro
from .serializers import RegistroSerializer

# Vista para health check
@api_view(["GET"])
def health(_):
    return Response({"ok": True})

# ViewSet para manejar los registros
class RegistroViewSet(viewsets.ModelViewSet):
    queryset = Registro.objects.all().order_by("id")
    serializer_class = RegistroSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "categoria", "fecha", "valor"]  # campos que puedes buscar
    ordering_fields = ["nombre", "categoria", "fecha", "valor"]  # campos por los cuales ordenar

    # Filtros exactos vía ?categoria=Ficcion (requiere django-filter activo en settings)
    filterset_fields = {"categoria": ["exact"]}

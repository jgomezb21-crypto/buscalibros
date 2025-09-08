from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Registro
from .serializers import RegistroSerializer

@api_view(["GET"])
def health(_):
    return Response({"ok": True})

class RegistroViewSet(viewsets.ModelViewSet):
    queryset = Registro.objects.all().order_by("id")
    serializer_class = RegistroSerializer

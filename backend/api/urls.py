from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import health, RegistroViewSet

router = DefaultRouter()
router.register("registros", RegistroViewSet, basename="registro")

urlpatterns = [
    path("health/", health),
    path("", include(router.urls)),
]

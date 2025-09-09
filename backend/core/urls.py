from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse, JsonResponse

def health(_request):
    return JsonResponse({"status": "OK"})

def home(_request):
    return HttpResponse("Backend OK")

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("health", health, name="health"),  # sin slash (lo que usa tu front)
    path("health/", health),                # con slash (por si acaso)
    path("api/", include("api.urls")),
]


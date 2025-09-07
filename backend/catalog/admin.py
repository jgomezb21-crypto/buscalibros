from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('code','title','author','area','shelf','available')
    search_fields = ('code','title','author','area')
    list_filter = ('area','available')

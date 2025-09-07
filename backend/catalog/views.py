from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter
from django.db.models import Q
from .models import Book
from .serializers import BookSerializer

class BookListView(ListAPIView):
    serializer_class = BookSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['title', 'author', 'area', 'code', 'created_at']
    ordering = ['title']  # orden por defecto

    def get_queryset(self):
        qs = Book.objects.all()
        q = self.request.query_params.get('q')
        author = self.request.query_params.get('author')
        area = self.request.query_params.get('area')
        code = self.request.query_params.get('code')
        available = self.request.query_params.get('available')

        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(author__icontains=q) |
                Q(area__icontains=q) |
                Q(code__icontains=q)
            )
        if author:
            qs = qs.filter(author__icontains=author)
        if area:
            qs = qs.filter(area__icontains=area)
        if code:
            qs = qs.filter(code__iexact=code)
        if available is not None:
            val = available.lower()
            if val in ['true','1','yes','y','t']:
                qs = qs.filter(available=True)
            elif val in ['false','0','no','n','f']:
                qs = qs.filter(available=False)
        return qs

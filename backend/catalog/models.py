from django.db import models

class Book(models.Model):
    code = models.CharField(max_length=32, unique=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    area = models.CharField(max_length=120)
    shelf = models.CharField(max_length=50, blank=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['author']),
            models.Index(fields=['area']),
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return f"{self.code} — {self.title}"

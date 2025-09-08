from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Registro(models.Model):
    # Cambiar a AutoField o UUIDField si no necesitas un CharField personalizado
    id = models.CharField(
        primary_key=True,
        max_length=64,
        unique=True,  # Asegura unicidad explícitamente
        help_text="Identificador único del registro"
    )
    nombre = models.CharField(
        max_length=255,
        help_text="Nombre del registro"
    )
    categoria = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        help_text="Categoría del registro (opcional)"
    )
    fecha = models.DateField(
        blank=True,
        null=True,
        help_text="Fecha asociada al registro (opcional)"
    )
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Valor monetario o numérico (opcional)"
    )
    lat = models.FloatField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(-90.0),
            MaxValueValidator(90.0)
        ],
        help_text="Latitud de la ubicación (opcional, -90 a 90)"
    )
    lon = models.FloatField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(-180.0),
            MaxValueValidator(180.0)
        ],
        help_text="Longitud de la ubicación (opcional, -180 a 180)"
    )

    class Meta:
        indexes = [
            models.Index(fields=["categoria"]),
            models.Index(fields=["lat", "lon"])
        ]
        # Ejemplo de unicidad en nombre y categoría (descomentar si es necesario)
        # unique_together = [["nombre", "categoria"]]
        verbose_name = "Registro"
        verbose_name_plural = "Registros"

    def __str__(self):
        return f"{self.nombre} ({self.id})"
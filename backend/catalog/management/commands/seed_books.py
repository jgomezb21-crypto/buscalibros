from django.core.management.base import BaseCommand
from backend.catalog.models import Book

SAMPLE = [
    {"code":"MAT-001","title":"Álgebra Lineal","author":"Gil Strang","area":"Matemáticas","shelf":"M1","available":True},
    {"code":"MAT-002","title":"Cálculo I","author":"James Stewart","area":"Matemáticas","shelf":"M2","available":True},
    {"code":"CS-001","title":"Automate the Boring Stuff","author":"Al Sweigart","area":"Computación","shelf":"C1","available":True},
    {"code":"CS-002","title":"Eloquent JavaScript","author":"Marijn Haverbeke","area":"Computación","shelf":"C2","available":False},
    {"code":"HIS-001","title":"Historia de Colombia","author":"J. O. Melo","area":"Historia","shelf":"H1","available":True},
    {"code":"PHY-001","title":"Física Universitaria","author":"Sears & Zemansky","area":"Física","shelf":"P1","available":False},
    {"code":"BIO-001","title":"Biología","author":"Campbell","area":"Biología","shelf":"B1","available":True},
    {"code":"LIT-001","title":"Cien años de soledad","author":"García Márquez","area":"Literatura","shelf":"L1","available":True},
    {"code":"ECO-001","title":"Principios de Economía","author":"Mankiw","area":"Economía","shelf":"E1","available":True},
    {"code":"QUI-001","title":"Química","author":"Zumdahl","area":"Química","shelf":"Q1","available":True},
]

class Command(BaseCommand):
    help = "Carga libros de ejemplo"
    def handle(self, *args, **opts):
        c,u = 0,0
        for item in SAMPLE:
            obj, created = Book.objects.update_or_create(code=item["code"], defaults=item)
            c += 1 if created else 0
            u += 0 if created else 1
        self.stdout.write(self.style.SUCCESS(
            f"Listo. Creados:{c} Actualizados:{u} Total:{Book.objects.count()}"
        ))

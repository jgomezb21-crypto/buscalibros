# backend/api/management/commands/import_registros.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Smoke test: verificar que Django carga este comando."

    def add_arguments(self, parser):
        parser.add_argument("--ping", action="store_true", help="Imprime OK si se cargó el comando")

    def handle(self, *args, **opts):
        self.stdout.write(self.style.SUCCESS("OK: import_registros cargado"))

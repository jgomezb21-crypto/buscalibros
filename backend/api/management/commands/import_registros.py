from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from api.models import Registro
import pandas as pd

class Command(BaseCommand):
    help = "Importa registros desde .xlsx o .csv (formato en columnas). Upsert por (nombre, categoria)."

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", required=True, help="Ruta al .xlsx o .csv")
        parser.add_argument("-s", "--sheet", default=0, help="Nombre/índice de hoja (solo .xlsx)")
        parser.add_argument("--clear", action="store_true", help="Borra antes de importar")
        parser.add_argument("--dry-run", action="store_true", help="No guarda, solo muestra")

    def handle(self, *args, **opts):
        path = Path(opts["file"])
        if not path.exists():
            raise CommandError(f"No existe el archivo: {path}")

        # === LECTURA ROBUSTA ===
        try:
            if path.suffix.lower() in (".xlsx", ".xls", ".xlsm"):
                df = pd.read_excel(path, sheet_name=opts["sheet"])
                if isinstance(df, dict):              # si vienen varias hojas
                    df = next(iter(df.values()))       # toma la primera
            elif path.suffix.lower() == ".csv":
                df = pd.read_csv(path)
            else:
                raise CommandError("Extensión no soportada. Usa .xlsx o .csv")
        except Exception as e:
            raise CommandError(f"Error leyendo el archivo: {e}")

        if df.empty:
            self.stdout.write(self.style.WARNING("No hay filas para importar."))
            return

        # Normaliza nombres de columnas
        cols = {c.strip().lower(): c for c in df.columns if isinstance(c, str)}
        def pick(*names):
            for n in names:
                c = cols.get(n)
                if c: return c
            return None

        c_nombre = pick("nombre", "titulo", "signatura", "nombre/signatura")
        c_categoria = pick("categoria", "categoría")
        c_fecha = pick("fecha", "anio", "año", "year")

        if not c_nombre:
            raise CommandError("No encuentro columna 'nombre' (o 'titulo'/'signatura').")

        if opts["clear"] and not opts["dry-run"]:
            total = Registro.objects.count()
            Registro.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Se borraron {total} registros."))

        created = updated = 0
        for _, row in df.iterrows():
            nombre = str(row.get(c_nombre, "")).strip()
            if not nombre:
                continue
            categoria = (str(row.get(c_categoria, "")).strip() if c_categoria else None) or ""
            fecha = str(row.get(c_fecha)) if c_fecha and pd.notna(row.get(c_fecha)) else None

            data = dict(nombre=nombre, categoria=categoria or None, fecha=fecha or None)

            if opts["dry_run"]:
                created += 1
                continue

            obj, was_created = Registro.objects.update_or_create(
                nombre=nombre, categoria=categoria or None, defaults=data
            )
            created += 1 if was_created else 0
            updated += 0 if was_created else 1

        self.stdout.write(self.style.SUCCESS(
            f"Importación registros: creados={created}, actualizados={updated}"
        ))

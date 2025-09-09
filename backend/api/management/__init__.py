# backend/api/management/commands/import_anaqueles.py
from pathlib import Path
import re
from typing import Optional, Tuple, List

from django.core.management.base import BaseCommand, CommandError
from api.models import Registro

try:
    import pandas as pd
except Exception as e:
    raise CommandError("Faltan dependencias. Instala: pip install pandas openpyxl") from e


ANAQUEL_RE = re.compile(r"anaquel\s*(\d+)", re.I)
ESTANTE_RE = re.compile(r"estante\s*(\d+)", re.I)
COD_RE     = re.compile(r"\((\d+)\)")
EJ_RE      = re.compile(r"(?i)\bej\.?\s*(\d+)")
YEAR_RE    = re.compile(r"\b(19|20)\d{2}\b")
SEP_RE     = re.compile(r"\s*/\s+")


def parse_cell(text: str) -> List[str]:
    text = str(text).strip()
    if not text or text.lower() in ("nan", "none"):
        return []
    return SEP_RE.split(text)


def extract_fields(item: str) -> Tuple[str, Optional[str], Optional[str], Optional[str]]:
    raw = item.strip()
    cod = (COD_RE.search(raw) or [None, None])[1]
    ej  = (EJ_RE.search(raw)  or [None, None])[1]
    yr  = (YEAR_RE.search(raw) or [None, None])[1]
    sign = raw.split("(", 1)[0].strip()
    sign = re.sub(r"\s{2,}", " ", sign).strip(" .;,")
    return sign, ej, yr, cod


def anaquel_num(label, idx):
    if isinstance(label, str):
        m = ANAQUEL_RE.search(label)
        if m:
            return int(m.group(1))
    return idx


def estante_num(label, idx):
    if isinstance(label, str):
        m = ESTANTE_RE.search(label)
        if m:
            return int(m.group(1))
    return idx


class Command(BaseCommand):
    help = ("Importa un Excel matriz de Anaqueles/Estantes. "
            "Explota cada celda y crea Registros con "
            "nombre=signatura y categoria='Anaquel X / Estante Y'.")

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", required=True, help="Ruta al .xlsx")
        parser.add_argument("-s", "--sheet", help="Hoja (nombre o índice). Por defecto, 0.")
        parser.add_argument("--clear", action="store_true", help="Borra todo antes de importar")
        parser.add_argument("--dry-run", action="store_true", help="No guarda, solo muestra")

    def handle(self, *args, **opts):
        path = Path(opts["file"])
        if not path.exists():
            raise CommandError(f"No existe el archivo: {path}")

        # Leer hoja (por defecto 0)
        try:
            df = pd.read_excel(path, sheet_name=opts.get("sheet", 0), header=0)
        except Exception as e:
            raise CommandError(f"Error leyendo el archivo: {e}")

        # Limpiar filas/columnas vacías
        df = df.dropna(how="all").dropna(axis=1, how="all")
        if df.empty:
            self.stdout.write(self.style.WARNING("No hay datos válidos."))
            return

        cols = list(df.columns)
        if not cols:
            self.stdout.write(self.style.WARNING("El archivo no tiene columnas."))
            return

        est_col = cols[0]
        ana_cols = cols[1:] if len(cols) > 1 else []

        if opts["clear"] and not opts["dry_run"]:
            total = Registro.objects.count()
            Registro.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Se borraron {total} registros."))

        created = updated = skipped = 0
        preview = 0

        for r_idx, row in df.iterrows():
            e_num = estante_num(row.get(est_col, None), r_idx + 1)

            for i, c in enumerate(ana_cols, start=1):
                a_num = anaquel_num(c, i)
                cell = row.get(c, None)
                if pd.isna(cell):
                    continue

                for item in parse_cell(cell):
                    sign, ej, yr, cod = extract_fields(item)
                    if not sign:
                        skipped += 1
                        continue

                    categoria = f"Anaquel {a_num} / Estante {e_num}"
                    data = {
                        "nombre": sign,
                        "categoria": categoria,
                        "fecha": (f"{yr}-01-01" if yr else None),
                        "valor": None, "lat": None, "lon": None,
                    }

                    if opts["dry_run"]:
                        created += 1
                    else:
                        obj, was_created = Registro.objects.update_or_create(
                            nombre=data["nombre"], categoria=data["categoria"], defaults=data
                        )
                        if was_created:
                            created += 1
                        else:
                            updated += 1

                    if preview < 5:
                        preview += 1
                        self.stdout.write(
                            f"→ {data['nombre']}  [{data['categoria']}]  año={yr or '-'}  cod={cod or '-'}  ej={ej or '-'}"
                        )

        self.stdout.write(self.style.SUCCESS(
            f"Importación anaqueles: creados={created}, actualizados={updated}, omitidos={skipped}"
        ))

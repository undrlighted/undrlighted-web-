#!/usr/bin/env python3
"""Crítica de sesión de Undrlighted: datos de las fotos y Excel con el formato fijo.

1) Sacar datos y miniaturas de una carpeta de JPG (hora, focal, f, velocidad, ISO):
    python3 critica_excel.py datos <carpeta_jpg> <salida.json> [--miniaturas <carpeta>]

   Crea un JSON con una entrada por foto para completarlo con la valoración, y
   miniaturas de 1200 px para revisarlas una a una.

2) Generar el Excel a partir del JSON ya valorado:
    python3 critica_excel.py excel <valoracion.json>

valoracion.json:
{
  "sesion": "Nombre · Lugar · 2026-11-01",
  "salida": "/ruta/Nombre-Lugar_critica_2026-11-02.xlsx",
  "veredicto": [["Nivel global", "..."], ["Lo mejor", "..."], ["Qué mejorar", "..."],
                ["Entregar", "194, 196, ..."], ["Publicar", "..."]],
  "fotos": [   # las que se valoran a fondo (normalmente las de 4 estrellas o la selección)
    {"foto": "194", "miniatura": "/ruta/194.jpg", "hora": "16:47",
     "datos": "82 mm · f/2.8 · 1/1250 · ISO 1000", "etiqueta": "Rosa",
     "nivel": "Avanzado", "decision": "Entregar",
     "funciona": "...", "falla": "...", "edicion": "..."}
  ],
  "resto": [   # opcional: el resto de la sesión, una línea por foto
    {"foto": "191", "miniatura": "/ruta/191.jpg", "hora": "16:47", "datos": "...",
     "nivel": "Básico-avanzado", "decision": "No", "valoracion": "...", "foco": "Sí"}
  ]
}
"""
import json
import sys
from pathlib import Path

NIVELES = ["Básico", "Básico-avanzado", "Avanzado", "Avanzado-profesional", "Profesional"]
DECISIONES = ["Entregar", "Publicar", "Entregar y publicar", "Recuperar", "Descartar", "No"]
NOCHE, CREMA, AMBAR, BURDEOS = "151B24", "F2EEE7", "A8692B", "682F3C"
COLOR_DECISION = {"Entregar": "F4D3DE", "Publicar": "E2D6EE", "Entregar y publicar": "EBD5E6",
                  "Recuperar": "F6E7C8", "Descartar": "E6E6E6", "No": "EFEFEF"}


def fraccion(v):
    try:
        v = float(v)
    except Exception:
        return str(v)
    return f"1/{round(1 / v)}" if 0 < v < 1 else f"{v:g}"


def datos(carpeta, salida, mini=None):
    from PIL import Image, ImageOps
    from PIL.ExifTags import TAGS
    filas = []
    exts = {".jpg", ".jpeg", ".tif", ".tiff", ".png"}
    for f in sorted(p for p in Path(carpeta).iterdir() if p.suffix.lower() in exts):
        im = Image.open(f)
        ex = {}
        try:
            raw = im._getexif() or {}
            ex = {TAGS.get(k, k): v for k, v in raw.items()}
        except Exception:
            pass
        hora = str(ex.get("DateTimeOriginal", ""))[11:16]
        partes = []
        if ex.get("FocalLength"):
            partes.append(f"{float(ex['FocalLength']):g} mm")
        if ex.get("FNumber"):
            partes.append(f"f/{float(ex['FNumber']):g}")
        if ex.get("ExposureTime"):
            partes.append(fraccion(ex["ExposureTime"]))
        if ex.get("ISOSpeedRatings"):
            partes.append(f"ISO {ex['ISOSpeedRatings']}")
        fila = {"foto": f.stem, "archivo": str(f.resolve()), "hora": hora, "datos": " · ".join(partes),
                "nivel": "", "decision": "", "funciona": "", "falla": "", "edicion": ""}
        if mini:
            Path(mini).mkdir(parents=True, exist_ok=True)
            m = ImageOps.exif_transpose(im).convert("RGB")
            m.thumbnail((1200, 1200))
            dest = Path(mini) / f"{f.stem}.jpg"
            m.save(dest, quality=82)
            fila["miniatura"] = str(dest.resolve())
        filas.append(fila)
    Path(salida).write_text(json.dumps(filas, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(filas)} fotos -> {salida}")


def excel(ruta_json):
    from openpyxl import Workbook
    from openpyxl.drawing.image import Image as XLImage
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.worksheet.datavalidation import DataValidation
    from PIL import Image, ImageOps
    import tempfile

    d = json.loads(Path(ruta_json).read_text(encoding="utf-8"))
    tmp = Path(tempfile.mkdtemp())
    wb = Workbook()
    cab = Font(bold=True, color=CREMA)
    relleno = PatternFill("solid", fgColor=NOCHE)
    envolver = Alignment(wrap_text=True, vertical="top")

    def cabecera(ws, cols, anchos):
        ws.append(cols)
        for c in ws[1]:
            c.font, c.fill = cab, relleno
            c.alignment = Alignment(vertical="center")
        for i, w in enumerate(anchos):
            ws.column_dimensions[chr(65 + i)].width = w
        ws.freeze_panes = "B2"

    def miniatura(ws, fila, ruta, col="A"):
        if not ruta or not Path(ruta).exists():
            return
        im = ImageOps.exif_transpose(Image.open(ruta)).convert("RGB")
        im.thumbnail((150, 150))
        p = tmp / f"m_{ws.title[:5]}_{fila}.jpg"
        im.save(p, quality=80)
        xl = XLImage(str(p))
        ws.add_image(xl, f"{col}{fila}")
        ws.row_dimensions[fila].height = max(ws.row_dimensions[fila].height or 15, im.height * 0.78)

    # Veredicto
    ws = wb.active
    ws.title = "Veredicto"
    ws.append([d.get("sesion", "Sesión"), ""])
    ws["A1"].font = Font(bold=True, size=14, color=BURDEOS)
    for k, v in d.get("veredicto", []):
        ws.append([k, v])
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 110
    for row in ws.iter_rows(min_row=2):
        row[0].font = Font(bold=True, color=AMBAR)
        for c in row:
            c.alignment = envolver

    # Valoración por foto
    if d.get("fotos"):
        ws = wb.create_sheet("Valoración por foto")
        cabecera(ws, ["Miniatura", "Foto", "Hora", "Etiqueta color", "Datos", "Nivel", "Decisión",
                      "Lo que funciona", "Qué falla", "Edición pendiente"],
                 [22, 10, 8, 12, 26, 20, 16, 45, 45, 45])
        for i, f in enumerate(d["fotos"], start=2):
            ws.append(["", f.get("foto"), f.get("hora"), f.get("etiqueta", ""), f.get("datos"),
                       f.get("nivel"), f.get("decision"), f.get("funciona"), f.get("falla"),
                       f.get("edicion", "—")])
            for c in ws[i]:
                c.alignment = envolver
            color = COLOR_DECISION.get(f.get("decision"))
            if color:
                ws[f"G{i}"].fill = PatternFill("solid", fgColor=color)
            miniatura(ws, i, f.get("miniatura"))
        n = len(d["fotos"]) + 1
        for col, opciones in (("F", NIVELES), ("G", DECISIONES)):
            dv = DataValidation(type="list", formula1='"' + ",".join(opciones) + '"', allow_blank=True)
            ws.add_data_validation(dv)
            dv.add(f"{col}2:{col}{n}")

    # Resto
    if d.get("resto"):
        ws = wb.create_sheet(f"Resto ({len(d['resto'])})")
        cabecera(ws, ["Miniatura", "Foto", "Hora", "Datos", "Nivel", "Decisión", "Valoración", "Foco 100 %"],
                 [22, 10, 8, 26, 20, 12, 70, 10])
        for i, f in enumerate(d["resto"], start=2):
            ws.append(["", f.get("foto"), f.get("hora"), f.get("datos"), f.get("nivel"),
                       f.get("decision"), f.get("valoracion"), f.get("foco", "")])
            for c in ws[i]:
                c.alignment = envolver
            miniatura(ws, i, f.get("miniatura"))

    salida = Path(d["salida"])
    salida.parent.mkdir(parents=True, exist_ok=True)
    wb.save(salida)
    print(f"Excel: {salida}")


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "datos":
        mini = sys.argv[sys.argv.index("--miniaturas") + 1] if "--miniaturas" in sys.argv else None
        datos(sys.argv[2], sys.argv[3], mini)
    elif len(sys.argv) == 3 and sys.argv[1] == "excel":
        excel(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)

#!/usr/bin/env python3
"""Rellena una plantilla .docx de Undrlighted (dossier v2 o guion de fotógrafo).

Uso:
    python3 rellenar_plantilla.py datos.json

datos.json:
{
  "plantilla": "/ruta/Undrlighted_Plantilla_Dossier_sesion_v2.docx",
  "salida": "/ruta/Undrlighted_Nombre_Dossier_v1.docx",
  "escenas": 3,                  # nº de escenas; duplica la página E01 (opcional, por defecto 1)
  "campos": {                    # campos globales: "[campo]" -> texto
    "[Título de la sesión]": "Luz de puerto",
    "[NOMBRE DE LA MODELO]": "ANE"
  },
  "campos_escena": {             # opcional: campos de cada escena, por número
    "1": {"[Nombre del lugar]": "Muelle", "[Idea de la escena]": "..."},
    "2": {"[Nombre del lugar]": "Faro"}
  },
  "portada": "/ruta/foto-portada.jpg",   # opcional: foto a sangre de la portada
  "imagenes": {                  # opcional: nº de imagen (orden en el documento, desde 1) -> foto
    "1": "/ruta/portada.jpg"     # se recorta al centro con la proporción del hueco de la plantilla
  },
  "pdf": true                    # convierte también a PDF con LibreOffice si está instalado
}

Para ver qué número tiene cada imagen: python3 rellenar_plantilla.py --imagenes plantilla.docx

Los campos se sustituyen dentro de su propio fragmento de texto, así se
mantienen la fuente, el color y la negrita de la plantilla. Al final lista
los campos [entre corchetes] que siguen sin rellenar.
"""
import copy
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from docx import Document

ESCENA_RE = re.compile(r"Escena\s+E0?(\d+)")


def todos_los_parrafos(doc_or_elem):
    """Párrafos del cuerpo, tablas (también anidadas), cabeceras y pies."""
    from docx.text.paragraph import Paragraph
    body = doc_or_elem.element.body if hasattr(doc_or_elem, "element") else doc_or_elem
    for p in body.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
        yield Paragraph(p, doc_or_elem if hasattr(doc_or_elem, "part") else None)
    if hasattr(doc_or_elem, "sections"):
        for s in doc_or_elem.sections:
            for parte in (s.header, s.footer, s.first_page_header, s.first_page_footer):
                try:
                    for p in parte.paragraphs:
                        yield p
                except Exception:
                    pass


def sustituir(parrafos, campos):
    for p in parrafos:
        if "[" not in p.text:
            continue
        for run in p.runs:
            for k, v in campos.items():
                if k in run.text:
                    run.text = run.text.replace(k, str(v))


def bloque_escena(body):
    """Devuelve (inicio, fin) de los elementos de la página de la escena E01."""
    hijos = list(body)
    ini = fin = None
    for i, el in enumerate(hijos):
        texto = "".join(el.itertext())
        if ini is None and ESCENA_RE.search(texto):
            ini = i
        elif ini is not None and re.search(r"0[4-9]\s+—", texto):
            fin = i
            break
    return ini, fin


def duplicar_escenas(doc, n, campos_escena):
    body = doc.element.body
    ini, fin = bloque_escena(body)
    if ini is None or fin is None:
        print("Aviso: no encuentro la página de escena E01; no se duplica.")
        return
    hijos = list(body)
    original = hijos[ini:fin]
    ancla = hijos[fin - 1]
    copias = []
    for k in range(2, n + 1):
        nuevo = [copy.deepcopy(el) for el in original]
        for el in nuevo:
            for t in el.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"):
                if t.text:
                    t.text = t.text.replace("E01", f"E{k:02d}")
        copias.append((k, nuevo))
    for k, nuevo in copias:
        for el in nuevo:
            ancla.addnext(el)
            ancla = el
    # campos por escena: se aplican a cada bloque por separado
    from docx.text.paragraph import Paragraph
    bloques = {1: original}
    bloques.update({k: els for k, els in copias})
    for k, els in bloques.items():
        cs = campos_escena.get(str(k), {})
        if not cs:
            continue
        for el in els:
            for p in el.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
                sustituir([Paragraph(p, doc.part)], cs)


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R_EMBED = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"


def imagenes_en_orden(doc):
    """(blip, cx, cy, texto cercano) de cada imagen, en orden de aparición."""
    res = []
    for dib in doc.element.body.iter(W + "drawing"):
        ext = next(dib.iter(WP + "extent"), None)
        blip = next(dib.iter(A + "blip"), None)
        if blip is None or ext is None:
            continue
        res.append((blip, int(ext.get("cx")), int(ext.get("cy"))))
    return res


def sustituir_imagenes(doc, mapa, tmpdir):
    from PIL import Image, ImageOps
    imgs = imagenes_en_orden(doc)
    for clave, ruta in mapa.items():
        i = int(clave) - 1
        if i < 0 or i >= len(imgs):
            print(f"Aviso: no hay imagen nº {clave} (hay {len(imgs)}).")
            continue
        blip, cx, cy = imgs[i]
        im = ImageOps.exif_transpose(Image.open(ruta)).convert("RGB")
        objetivo = cx / cy
        w, h = im.size
        if w / h > objetivo:
            nw = int(h * objetivo); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else:
            nh = int(w / objetivo); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
        if im.width > 2400:
            im = im.resize((2400, int(2400 / objetivo)))
        out = Path(tmpdir) / f"img_{clave}.jpg"
        im.save(out, quality=88)
        rid, _ = doc.part.get_or_add_image(str(out))
        blip.set(R_EMBED, rid)


def sustituir_portada(doc, ruta):
    """La foto de portada vive en la cabecera de la primera página (media/cover.jpg)."""
    import io
    from PIL import Image, ImageOps
    for parte in doc.part.package.parts:
        if str(parte.partname).endswith("/media/cover.jpg"):
            viejo = Image.open(io.BytesIO(parte.blob))
            objetivo = viejo.width / viejo.height
            im = ImageOps.exif_transpose(Image.open(ruta)).convert("RGB")
            w, h = im.size
            if w / h > objetivo:
                nw = int(h * objetivo); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
            else:
                nh = int(w / objetivo); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
            im = im.resize(viejo.size)
            buf = io.BytesIO(); im.save(buf, "JPEG", quality=88)
            parte._blob = buf.getvalue()
            return
    print("Aviso: no encuentro la foto de portada (media/cover.jpg).")


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--imagenes":
        doc = Document(sys.argv[2])
        for n, (blip, cx, cy) in enumerate(imagenes_en_orden(doc), 1):
            print(f"{n}: {cx/914400*2.54:.1f} x {cy/914400*2.54:.1f} cm")
        return
    datos = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    doc = Document(datos["plantilla"])
    n = int(datos.get("escenas", 1))
    campos_escena = datos.get("campos_escena", {})
    if n > 1 or campos_escena:
        duplicar_escenas(doc, max(n, 1), campos_escena)
    sustituir(list(todos_los_parrafos(doc)), datos.get("campos", {}))
    if datos.get("portada"):
        sustituir_portada(doc, datos["portada"])
    if datos.get("imagenes"):
        import tempfile
        tmp = tempfile.mkdtemp()
        sustituir_imagenes(doc, datos["imagenes"], tmp)
    salida = Path(datos["salida"])
    salida.parent.mkdir(parents=True, exist_ok=True)
    doc.save(salida)
    print(f"Guardado: {salida}")

    pendientes = sorted({m for p in todos_los_parrafos(Document(salida))
                         for m in re.findall(r"\[[^\]]+\]", p.text)})
    if pendientes:
        print(f"Campos sin rellenar ({len(pendientes)}):")
        for m in pendientes:
            print("  ", m)
    else:
        print("No quedan campos sin rellenar.")

    if datos.get("pdf"):
        soffice = shutil.which("soffice") or shutil.which("libreoffice")
        if not soffice:
            print("Sin LibreOffice: exporta el PDF desde Pages o Word en el Mac.")
            return
        subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir",
                        str(salida.parent), str(salida)], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pdf = salida.with_suffix(".pdf")
        print(f"PDF: {pdf}" if pdf.exists() else "No se pudo convertir a PDF.")


if __name__ == "__main__":
    main()

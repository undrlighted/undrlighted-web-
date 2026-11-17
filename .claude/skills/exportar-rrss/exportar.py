#!/usr/bin/env python3
"""Formatos de Instagram de Undrlighted a partir de una foto.

  post      1080x1350 (4:5) recortada
  historia  1080x1920 (9:16) a sangre, con texto opcional abajo
  marco     1080x1920 con la foto enmarcada sobre azul noche y texto eu/es debajo
  cierre    1080x1920 de cierre con logo, «Zure saioa?» y la web (sin foto)

Ejemplos:
  python3 exportar.py post foto.jpg salida.jpg --foco 0.5 0.35
  python3 exportar.py historia foto.jpg salida.jpg --titulo "KARAKATE" --sub "Igoera · 2026 · undrlighted"
  python3 exportar.py marco foto.jpg salida.jpg --etiqueta "ARGITALPEN BERRIA · NUEVA PUBLICACIÓN" \
        --titulo "Gaua da eta argiak hitz egiten digu" --sub "Durante la noche, la luz nos habla" \
        --credito "Modeloa / Modelo  @usuario" --lugar "Bilbao"
  python3 exportar.py cierre - salida.jpg [--escala 2]   (escala 2 = 2160x3840 para reels en 4K)

--foco X Y: punto que debe quedar dentro del recorte (0-1 desde arriba a la izquierda). Por defecto, el centro.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

AQUI = Path(__file__).resolve().parent
F = AQUI / "fuentes"
NOCHE = (21, 27, 36)
CREMA = (242, 238, 231)
AMBAR_CLARO = (217, 163, 95)
BURDEOS = (119, 62, 73)


def fuente(nombre, tam):
    return ImageFont.truetype(str(F / nombre), tam)


TITULO = "BodoniModa_28pt-Italic.ttf"
TEXTO = "BodoniModa_11pt-Medium.ttf"
TEXTO_IT = "BodoniModa_11pt-MediumItalic.ttf"
NEGRITA = "BodoniModa_11pt-SemiBold.ttf"


def abrir(ruta):
    im = Image.open(ruta)
    im = ImageOps.exif_transpose(im)
    if im.mode != "RGB":
        im = im.convert("RGB")
    return im


def recortar(im, w, h, foco=(0.5, 0.5)):
    """Recorte a la proporción w:h que contiene el punto de foco y escala a w x h."""
    iw, ih = im.size
    objetivo = w / h
    if iw / ih > objetivo:
        nw = round(ih * objetivo)
        x = min(max(round(foco[0] * iw - nw / 2), 0), iw - nw)
        im = im.crop((x, 0, x + nw, ih))
    else:
        nh = round(iw / objetivo)
        y = min(max(round(foco[1] * ih - nh / 2), 0), ih - nh)
        im = im.crop((0, y, iw, y + nh))
    if im.width < w:
        print(f"Aviso: la foto tiene menos resolución ({im.width}px) que el formato ({w}px).")
    return im.resize((w, h), Image.LANCZOS)


def espaciado(draw, xy, texto, f, fill, track=0, anchor="mm"):
    """Texto centrado con espaciado entre letras (para mayúsculas)."""
    if not track:
        draw.text(xy, texto, font=f, fill=fill, anchor=anchor)
        return
    anchos = [draw.textlength(c, font=f) for c in texto]
    total = sum(anchos) + track * (len(texto) - 1)
    x = xy[0] - total / 2
    for c, a in zip(texto, anchos):
        draw.text((x, xy[1]), c, font=f, fill=fill, anchor="lm")
        x += a + track


def ajustar(draw, texto, nombre, tam, ancho_max):
    """Reduce el tamaño hasta que el texto quepa en una línea."""
    while tam > 20 and draw.textlength(texto, font=fuente(nombre, tam)) > ancho_max:
        tam -= 2
    return fuente(nombre, tam)


def degradado(w, h, alto, abajo=True, alfa=0.85):
    capa = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for i in range(alto):
        a = int(255 * alfa * (i / alto) ** 1.6)
        y = h - alto + i if abajo else alto - i
        d.line([(0, y), (w, y)], fill=NOCHE + (a,))
    return capa


def post(a):
    im = recortar(abrir(a.foto), 1080, 1350, a.foco)
    guardar(im, a.salida)


def historia(a):
    w, h = 1080, 1920
    im = recortar(abrir(a.foto), w, h, a.foco).convert("RGBA")
    if a.titulo or a.sub:
        im = Image.alpha_composite(im, degradado(w, h, 620))
        d = ImageDraw.Draw(im)
        # zona segura: nada por debajo de y=1640 (respuesta) ni por encima de 250
        if a.titulo:
            espaciado(d, (w / 2, 1470), a.titulo.upper(), fuente(TEXTO, 46), CREMA, track=10)
        if a.sub:
            d.text((w / 2, 1530), a.sub, font=fuente(TEXTO_IT, 30), fill=CREMA, anchor="mm")
    guardar(im.convert("RGB"), a.salida)


def marco(a):
    w, h = 1080, 1920
    lienzo = Image.new("RGB", (w, h), NOCHE)
    foto = recortar(abrir(a.foto), 840, 1050, a.foco)  # 4:5 dentro de la historia
    lienzo.paste(foto, ((w - 840) // 2, 230))
    d = ImageDraw.Draw(lienzo)
    y = 1350
    if a.etiqueta:
        espaciado(d, (w / 2, y), a.etiqueta.upper(), fuente(NEGRITA, 22), AMBAR_CLARO, track=4)
        y += 70
    if a.titulo:
        d.text((w / 2, y), a.titulo, font=ajustar(d, a.titulo, TEXTO, 44, 900), fill=CREMA, anchor="mm")
        y += 58
    if a.sub:
        d.text((w / 2, y), a.sub, font=ajustar(d, a.sub, TEXTO_IT, 34, 900), fill=CREMA, anchor="mm")
        y += 80
    if a.credito:
        d.text((w / 2, y), a.credito, font=fuente(TEXTO, 26), fill=CREMA, anchor="mm")
        y += 42
    if a.lugar:
        d.text((w / 2, y), a.lugar, font=fuente(TEXTO, 22), fill=(170, 170, 170), anchor="mm")
    guardar(lienzo, a.salida)


def cierre(a):
    k = a.escala
    w, h = 1080 * k, 1920 * k
    im = Image.new("RGB", (w, h), NOCHE)
    d = ImageDraw.Draw(im)
    logo = Image.open(AQUI / "logo-UL-circulo.png").convert("RGBA")
    logo = logo.resize((300 * k, 300 * k), Image.LANCZOS)
    im.paste(logo, ((w - logo.width) // 2, 560 * k), logo)
    d.text((w / 2, 960 * k), a.titulo or "Zure saioa?", font=fuente(TITULO, 84 * k), fill=CREMA, anchor="mm")
    d.text((w / 2, 1060 * k), a.sub or "Idatzi iezadazu", font=fuente(TEXTO_IT, 54 * k), fill=CREMA, anchor="mm")
    d.text((w / 2, 1135 * k), a.etiqueta or "¿Tu sesión? Escríbeme", font=fuente(TEXTO_IT, 38 * k),
           fill=CREMA, anchor="mm")
    d.line([(w / 2 - 60 * k, 1185 * k), (w / 2 + 60 * k, 1185 * k)], fill=BURDEOS, width=2 * k)
    espaciado(d, (w / 2, 1240 * k), "UNDRLIGHTED.ES", fuente(TEXTO, 48 * k), CREMA, track=8 * k)
    guardar(im, a.salida)


def guardar(im, salida):
    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    im.save(salida, "JPEG", quality=92, subsampling=0, optimize=True)
    print(f"{salida}  {im.width}x{im.height}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("modo", choices=["post", "historia", "marco", "cierre"])
    p.add_argument("foto", help="foto de entrada ('-' para cierre)")
    p.add_argument("salida")
    p.add_argument("--foco", nargs=2, type=float, default=(0.5, 0.5))
    p.add_argument("--titulo")
    p.add_argument("--sub")
    p.add_argument("--etiqueta")
    p.add_argument("--credito")
    p.add_argument("--lugar")
    p.add_argument("--escala", type=int, default=1)
    a = p.parse_args()
    {"post": post, "historia": historia, "marco": marco, "cierre": cierre}[a.modo](a)


if __name__ == "__main__":
    main()

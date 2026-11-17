---
name: exportar-rrss
description: Saca de las fotos de Undrlighted los formatos de Instagram con el estilo de la marca, post 4:5 (1080×1350), historia 9:16 a sangre o enmarcada con texto en Bodoni Moda, y la diapositiva de cierre «Zure saioa?». Úsala cuando Adur pida "prepara las historias", "pásalo a 4:5", "carrusel con estas fotos", "historia de la nueva publicación" o "cierre del reel".
---

# Exportar para redes

`exportar.py` hace los cuatro formatos con las fuentes y colores fijos de la marca (Bodoni Moda en `fuentes/`, licencia OFL; logo `logo-UL-circulo.png`; azul noche `#151B24`, crema `#F2EEE7` y ámbar claro `#D9A35F`).

| Modo | Tamaño | Para qué |
|---|---|---|
| `post` | 1080×1350 | Publicación o diapositiva de carrusel (4:5) |
| `historia` | 1080×1920 | Historia a sangre, con título y subtítulo opcionales abajo |
| `marco` | 1080×1920 | Historia de "nueva publicación": foto 4:5 enmarcada, etiqueta, texto eu/es, crédito y lugar |
| `cierre` | 1080×1920 (`--escala 2` = 2160×3840) | Cierre de reel o de carrusel: logo, «Zure saioa? / Idatzi iezadazu / ¿Tu sesión? Escríbeme», UNDRLIGHTED.ES |

```bash
S=.claude/skills/exportar-rrss
python3 $S/exportar.py post foto.jpg salida_4x5.jpg --foco 0.5 0.35
python3 $S/exportar.py historia foto.jpg salida_9x16.jpg --titulo "Karakate" --sub "Igoera · 2026 · undrlighted"
python3 $S/exportar.py marco foto.jpg historia.jpg --etiqueta "Argitalpen berria · Nueva publicación" \
  --titulo "<frase en euskera>" --sub "<frase en castellano>" --credito "Modeloa / Modelo  @usuario" --lugar "Bilbao"
python3 $S/exportar.py cierre - cierre.jpg
```

## Reglas

- **Mira la foto antes de recortar** y elige `--foco` (x y entre 0 y 1) para no cortar cabezas, manos ni pies. Comprueba el resultado mirando el JPG.
- Parte de la exportación de máxima calidad (la de `output`/`lanak` en el Mac), no de una miniatura. Si el script avisa de poca resolución, pide a Adur una exportación mayor.
- **Fotos sin firma.** Las que llevan la firma de Adur no se usan: hay que exportarlas sin firma desde el RAW.
- No repitas fotos ya publicadas en el feed.
- Textos: **euskera (batua) primero** y castellano después, en cursiva. Son borradores que Adur revisa y corrige. Máximo 6 palabras por línea en las historias.
- En los textos públicos se dice "Euskal Herria", nunca "Euskadi". Nada de precios, packs ni descuentos. No inventes cifras.
- Menores (salvo su hijo o BTT con casco) y pilotos reconocibles: no se publican sin permiso.
- Zona segura de las historias: el texto no baja de y≈1640 ni sube de y≈250, porque Instagram pone ahí sus botones.
- Música, colaboradores, stickers y destacadas los pone Adur en la app. **No se publica nada sin su aprobación.**

## Dónde guardar

`/mnt/project-files/undrlighted/redes/<tema-AAAA-MM-DD>/` y, si Adur lo quiere en el Mac, `/Volumes/HD2026/Undrlighted/03_redes/<misma carpeta>/`. Para revisar varias juntas, haz una hoja de contactos (`_hoja_<tema>.jpg`).

Los reels se montan en DaVinci Resolve con la guía de `redes/estilo-reels/LEEME.md`. Esta skill solo hace las imágenes fijas.

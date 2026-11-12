# Cómo se genera la web

Desde el 27-oct-2026 los archivos `index.html` publicados se **generan**. No se editan a mano.

- **Fuente:** `src/template.html` (diseño, textos `T`, fotos `PHOTOS`).
- **Generador:** `tools/build.py` (URL, títulos, descripciones, hreflang, og, JSON-LD y sitemap).
- **Texto en el HTML:** `tools/prerender.js`. Abre cada página en Chromium y guarda el texto que pinta el script, para que Google lo lea sin ejecutar JavaScript.

```bash
python3 tools/build.py
node tools/prerender.js     # necesita Playwright (en los hilos en la nube ya está instalado)
```

Páginas generadas (21):

| URL | Idioma | Contenido |
| --- | --- | --- |
| `/` | eu | Portada (abre en euskera) |
| `/es/`, `/en/` | es, en | Portada |
| `/erretratua/`, `/es/book-retrato/` | eu, es | Book y retrato |
| `/bikoteak/`, `/es/parejas/` | eu, es | Parejas |
| `/haurdunaldia/`, `/es/embarazo/` | eu, es | Embarazo |
| `/kirola/`, `/es/deporte/` | eu, es | Deporte |
| `/familia/`, `/es/familia/` | eu, es | Familia |
| `/natura/`, `/es/naturaleza/` | eu, es | Naturaleza (página corta) |
| `/ekitaldiak/`, `/es/eventos/` | eu, es | Eventos (página corta) |
| `/markak/`, `/es/marcas/` | eu, es | Marcas (página corta) |
| `/argazki-saioa-gipuzkoa/`, `/es/sesion-de-fotos-gipuzkoa/` | eu, es | Guía local de Gipuzkoa |

Desde el 12-nov, Exteriores y Estudio son un solo tipo, «Retrato y moda» (clave `estudio`), que lleva a `/erretratua/` y `/es/book-retrato/`.

## Notas

- Las secciones siguen funcionando con `#` (`#trabajos`, `#galeria/parejas`…) dentro de cada URL.
- **Search Console:** pega el código de la etiqueta HTML en `GSC_TOKEN` (en `tools/build.py`) y vuelve a generar.
- **Testimonios:** añádelos en `testi` de cada idioma, en `src/template.html`, como `["texto", "Nombre, sesión"]`. Con la lista vacía, la sección no aparece.
- **Foto nueva:** añádela a `PHOTOS`. Su texto alternativo es el nombre del tipo de trabajo (Adur quitó las descripciones por foto el 27-oct; `ALT` queda vacío).

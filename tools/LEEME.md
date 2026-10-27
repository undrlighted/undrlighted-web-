# Cómo se genera la web

Desde el 27-oct-2026 los archivos `index.html` publicados se **generan**. No se editan a mano.

- **Fuente:** `src/template.html` (diseño, textos `T`, fotos `PHOTOS`, textos alternativos `ALT`).
- **Generador:** `tools/build.py` (URL, títulos, descripciones, hreflang, og, JSON-LD y sitemap).
- **Texto en el HTML:** `tools/prerender.js`. Abre cada página en Chromium y guarda el texto que pinta el script, para que Google lo lea sin ejecutar JavaScript.

```bash
python3 tools/build.py
node tools/prerender.js     # necesita Playwright (en los hilos en la nube ya está instalado)
```

Páginas generadas (11):

| URL | Idioma | Contenido |
| --- | --- | --- |
| `/` | eu | Portada (abre en euskera) |
| `/es/`, `/en/` | es, en | Portada |
| `/erretratua/`, `/es/book-retrato/` | eu, es | Book y retrato |
| `/bikoteak/`, `/es/parejas/` | eu, es | Parejas |
| `/haurdunaldia/`, `/es/embarazo/` | eu, es | Embarazo |
| `/kirola/`, `/es/deporte/` | eu, es | Deporte |

## Notas

- Las secciones siguen funcionando con `#` (`#trabajos`, `#galeria/parejas`…) dentro de cada URL.
- **Search Console:** pega el código de la etiqueta HTML en `GSC_TOKEN` (en `tools/build.py`) y vuelve a generar.
- **Testimonios:** añádelos en `testi` de cada idioma, en `src/template.html`, como `["texto", "Nombre, sesión"]`. Con la lista vacía, la sección no aparece.
- **Foto nueva:** añádela a `PHOTOS` y su texto alternativo a `ALT` (`[eu, es, en]`). Si no tiene texto alternativo, se usa el nombre del tipo de trabajo.

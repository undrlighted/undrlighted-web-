---
name: critica-sesion
description: Revisa las fotos de una sesión de Undrlighted (seleccionadas o la sesión completa) y entrega la crítica en el Excel de formato fijo, con miniaturas, nivel, decisión (entregar, publicar, recuperar, descartar) y edición pendiente. Úsala cuando Adur pida "valora la sesión", "crítica de las fotos", "cuáles entrego", "revisa las de 4 estrellas" o "qué tal han salido".
---

# Crítica de sesión

Sirve para revisar una sesión y entregar siempre el mismo Excel, sin rehacer el formato en cada hilo. Es de **solo lectura**: propone, y Adur decide y marca en Capture One.

## 1. Qué revisar y de dónde salen las fotos

Pregunta qué alcance quiere Adur si no lo dice: solo las de 4 estrellas, las editadas o la sesión completa.

- Las fotos están en el Mac (`/Volumes/HD2026/...`). Hace falta el Mac encendido y la carpeta conectada. **No muevas, renombres ni borres nada.**
- Editadas: carpeta `output` de la sesión (las nuevas, dentro de `lanak`). Si solo hay RAW, saca la vista previa incrustada (por ejemplo `exiftool -b -PreviewImage`, si está instalado) o pide a Adur que exporte JPG.
- Genera las miniaturas **en el Mac** (`device_bash`, con Python/PIL si está disponible) y sube solo esas, no los originales.
- **Mira cada foto tú mismo** antes de valorarla. No valores por nombre ni por los datos EXIF.

## 2. Reglas de Capture One (de Adur)

| Marca | Significado |
|---|---|
| Etiqueta rosa | Entregar a la modelo o al cliente |
| Etiqueta violeta | Publicar, las mejores |
| Etiqueta verde | Ya editadas |
| Etiqueta azul | Duplicados sin pasar por Photoshop |
| 4 estrellas | Seleccionadas |

No cambies estrellas ni etiquetas salvo que Adur lo pida expresamente, y **nunca toques las verdes ni las azules**. Si propones cambios, ponlos en el Excel.

## 3. Cómo valorar

- Nivel: `Básico`, `Básico-avanzado`, `Avanzado`, `Avanzado-profesional` o `Profesional`. Sé exigente y concreto: no infles las notas.
- Decisión: `Entregar`, `Publicar`, `Entregar y publicar`, `Recuperar` (una foto sin estrellas que merece entrar) o `Descartar`. En la hoja del resto de la sesión vale `No`.
- **Lo que funciona / Qué falla:** luz, composición, gesto y mirada, fondo, foco al 100 % y color. Nombra elementos visibles: "muro blanco detrás", "pelos sueltos", "destello magenta".
- **Edición pendiente:** acciones concretas en Capture One o Photoshop, como "recortar a 4:5 cerrando sobre la cara" o "Seleccionar y aplicar máscara en el pelo".
- Juzga cada sesión con su propio objetivo. Una prueba con luz natural o una sesión familiar no es un fallo de estilo por no llevar flash.
- Menores y pilotos reconocibles: márcalo en la valoración, porque necesitan permiso antes de publicarse.
- Ten en cuenta para quién es: para el book de la modelo, para el portfolio de Undrlighted (web y redes) o para las dos cosas.

## 4. El Excel

```bash
S=.claude/skills/critica-sesion
python3 $S/critica_excel.py datos <carpeta_jpg> datos.json --miniaturas <carpeta_miniaturas>
# completa nivel, decisión y textos en el JSON (el formato está al principio del script)
python3 $S/critica_excel.py excel valoracion.json
```

Hojas: **Veredicto** (nivel global, lo mejor, qué te separa del siguiente nivel, lista de números a entregar y a publicar), **Valoración por foto** (selección a fondo, con miniatura y desplegables) y, si se revisa la sesión completa, **Resto (N)** con una línea por foto.

Nombre del archivo: `<Modelo>-<Lugar>_critica-<alcance>_<AAAA-MM-DD>.xlsx`. Guárdalo en `/mnt/project-files/undrlighted/sesiones/<carpeta de la sesión>/` y, si Adur lo quiere en el Mac, en la carpeta de la sesión de `01_sesiones`.

Al responder, da en dos o tres frases el veredicto y los números a entregar, y adjunta el Excel.

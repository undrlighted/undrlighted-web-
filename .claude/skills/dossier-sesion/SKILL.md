---
name: dossier-sesion
description: Prepara los dos documentos de una sesión de Undrlighted, el dossier para la modelo (plantilla v2) y el guion de fotógrafo, rellenando las plantillas .docx de la marca y sacando el PDF. Úsala cuando Adur diga "prepara el dossier", "guion de la sesión", "plan de sesión" o cierre una sesión nueva con alguien.
---

# Dossier y guion de sesión

Cada sesión lleva dos documentos con la misma estética (portada a sangre, interiores crema, Didot + Avenir Next, acento ámbar):

| Documento | Para quién | Plantilla |
|---|---|---|
| Dossier de sesión v2 | La modelo. Se le envía en PDF. | `Undrlighted_Plantilla_Dossier_sesion_v2.docx` |
| Guion de sesión, versión fotógrafo | Solo Adur. **Nunca se envía a la modelo.** | `Undrlighted_Plantilla_Guion-fotografo_v1.docx` |

Las plantillas están en `/mnt/project-files/undrlighted/plantillas/v2/` (copia de `/Volumes/HD2026/Undrlighted/02_plantillas/` en el Mac, que es el original). Si en el Mac hay una versión más nueva, usa esa.

## 1. Reúne los datos antes de escribir

Pide a Adur solo lo que falte; no inventes datos de la modelo, lugares ni horarios.

- Modelo (nombre, usuario de Instagram), tipo de sesión y para qué la quiere (book, portfolio...).
- Lugar exacto, punto de encuentro y fecha y hora. Comprueba la luz de ese día: puesta de sol, hora dorada y azul, y la marea si es en la costa.
- Idea de la serie, escenas (normalmente 2–4) y looks.
- Referencias: de **Pinterest**, con pocas imágenes de IA. Firefly solo con permiso expreso de Adur, porque gasta créditos.

## 2. Reglas fijas de Undrlighted

- Textos cercanos y en segunda persona hacia la modelo. Español por defecto; euskera si Adur lo pide.
- **Entrega:** indica el plazo, pero **no el número de fotos**.
- Colaboración TFP salvo que Adur diga otra cosa. **Sin precios**: no van precios, packs ni presupuestos en ningún documento.
- Estilismo con **versión de interior y de exterior** cuando el tiempo sea dudoso, y plan B por lluvia o viento.
- Escenas de lo fácil a lo difícil, con un calentamiento que no cuenta. Situaciones y acciones en lugar de poses.
- Guion de fotógrafo: esquema de luz por escena, montaje paso a paso, ajustes de cámara de partida, potencias del flash, poses y frases, y checklist.
- Equipo real: cuerpo Micro Cuatro Tercios, 12–40 y 40–150, Godox **AD200Pro y AD100Pro**, octa 90, softbox 60, kit AK-R1, **2 pies**, fondos blanco y negro. No añadas equipo que no tiene.
- Estilo de la marca: clave baja, flash, cinematográfico. Si la sesión es de luz natural o familiar, también encaja en la marca: no la trates como un fallo de estilo.

## 3. Rellena las plantillas

`rellenar_plantilla.py` sustituye los campos `[entre corchetes]` sin perder el formato, duplica la página de escena E01 tantas veces como escenas haya, cambia las fotos y saca el PDF.

```bash
S=.claude/skills/dossier-sesion
# Ver los huecos de imagen numerados (en el documento ya duplicado, si hay varias escenas)
python3 $S/rellenar_plantilla.py --imagenes /ruta/documento.docx
# Rellenar
python3 $S/rellenar_plantilla.py datos.json
```

El formato de `datos.json` está al principio del script: `plantilla`, `salida`, `escenas`, `campos`, `campos_escena`, `portada`, `imagenes` y `pdf`. Haz el dossier y el guion con dos JSON distintos. El script lista los campos que quedan sin rellenar: no entregues nada con corchetes.

- Si hay varias escenas, primero genera el documento con `escenas`, luego lista sus imágenes con `--imagenes` y haz una segunda pasada con ese documento como `plantilla` para poner las fotos de cada escena.
- El esquema de luz base es `esquema-luz-base.svg` (en esta carpeta). Dibuja uno por escena en SVG con las posiciones reales de la modelo, la cámara, el AD200Pro y el AD100Pro, conviértelo a PNG y colócalo en su hueco.
- **El PDF que se genera en la nube usa fuentes de sustitución**, porque Didot y Avenir Next son fuentes de Mac. Sirve para revisarlo. El PDF definitivo para la modelo se exporta desde Pages o Word en el Mac.
- Revisa el PDF página a página (por ejemplo con `pdftoppm -r 40`) antes de entregarlo.

## 4. Dónde se guarda

- Carpeta de la sesión en el Mac: `/Volumes/HD2026/Undrlighted/01_sesiones/AAAA-MM-DD_modelo-lugar/` (o `por-fechar_modelo-lugar/`), subcarpeta `entrega/`.
- Copia para el proyecto: `/mnt/project-files/undrlighted/sesiones/<misma carpeta>/`.
- Nombres: `Undrlighted_<Modelo>_Dossier_vN.docx/.pdf` y `Undrlighted_<Modelo>_Guion-fotografo_vN.docx/.pdf`.

**No envíes nada a la modelo.** Entrega los archivos a Adur, que revisa y envía.

Hay guiones terminados de sesiones anteriores en `01_sesiones/` del Mac: úsalos como ejemplo de tono y nivel de detalle.

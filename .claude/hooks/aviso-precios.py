#!/usr/bin/env python3
"""Hook PreToolUse: frena cambios en la web que añadan precios mientras Adur no esté de alta.

Compara el texto antes y después del cambio. Solo bloquea si el cambio AÑADE
menciones de precio (€, euros, precio, presupuesto, prezioa, aurrekontua, -30 %)
o si quita el bloque CSS que oculta los precios. Lo que ya existe en la web
(el código oculto de los packs) no cuenta.

Para desactivarlo cuando Adur se dé de alta: quitar el bloque "hooks" de
.claude/settings.json o borrar este archivo.
"""
import json
import re
import sys
from pathlib import Path

PATRONES = [
    r"€",
    r"\b\d+[.,]?\d*\s?euros?\b",
    r"\bprecios?\b",
    r"\bpresupuestos?\b",
    r"\bprezio(?:a|ak|rik)?\b",
    r"\baurrekontu(?:a|ak|rik)?\b",
    r"(?:−|–|-)\s?30\s%|−30\s?%",
]
REGEX = re.compile("|".join(PATRONES), re.IGNORECASE)
MARCA_OCULTOS = "Precios ocultos"
EXTENSIONES = {".html", ".htm", ".js", ".json", ".xml", ".txt", ".md", ".css"}


def cuenta(texto):
    return len(REGEX.findall(texto or ""))


def main():
    try:
        datos = json.load(sys.stdin)
    except Exception:
        return 0
    entrada = datos.get("tool_input") or {}
    ruta = entrada.get("file_path") or entrada.get("notebook_path") or ""
    if not ruta:
        return 0
    p = Path(ruta)
    partes = set(p.parts)
    if p.suffix.lower() not in EXTENSIONES or {".claude", ".agents", ".git", "node_modules"} & partes:
        return 0

    herramienta = datos.get("tool_name", "")
    if herramienta == "Write":
        antes = p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""
        despues = entrada.get("content", "")
    elif herramienta == "Edit":
        antes, despues = entrada.get("old_string", ""), entrada.get("new_string", "")
    elif herramienta == "MultiEdit":
        eds = entrada.get("edits") or []
        antes = "\n".join(e.get("old_string", "") for e in eds)
        despues = "\n".join(e.get("new_string", "") for e in eds)
    else:
        return 0

    motivos = []
    nuevos = cuenta(despues) - cuenta(antes)
    if nuevos > 0:
        ejemplos = sorted({m.strip() for m in REGEX.findall(despues)})[:5]
        motivos.append(f"añade {nuevos} mención(es) de precio ({', '.join(ejemplos)})")
    if MARCA_OCULTOS in antes and MARCA_OCULTOS not in despues:
        motivos.append("quita el bloque que oculta los precios")
    if not motivos:
        return 0

    print(
        f"Bloqueado por la regla SIN PRECIOS de Undrlighted: el cambio en {p.name} {' y '.join(motivos)}. "
        "Adur no está dado de alta como autónomo y la web no debe mostrar precios, packs, descuentos ni "
        "presupuestos; solo invitar a contactar. No lo intentes de otra forma: díselo a Adur. Si él pide "
        "expresamente reactivar los precios, hay que quitar este hook de .claude/settings.json.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())

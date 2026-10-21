# Instagram agent skill (vendorizada)

Las 13 skills `ig-*` de `.claude/skills/` vienen tal cual de
https://github.com/Jakeschincariol/instagram-agent-skill (commit d03c56b, licencia MIT
en `.claude/skills/LICENSE-instagram-agent-skill`).

Las skills buscan su configuración en `~/.claude/instagram/` (voice.md, swipe.md, log.md).
En los hilos en la nube esa carpeta no persiste: la plantilla y lo que se rellene se
guardan aquí, en `.claude/instagram/`, y se leen desde esta ruta.

# Instagram agent skill (vendorizada)

Las 13 skills `ig-*` de `.claude/skills/` vienen tal cual de
https://github.com/Jakeschincariol/instagram-agent-skill (commit d03c56b, licencia MIT
en `.claude/skills/LICENSE-instagram-agent-skill`).

Las skills buscan su configuración en `~/.claude/instagram/` (voice.md, swipe.md, log.md).
En los hilos en la nube esa carpeta no persiste: la plantilla y lo que se rellene se
guardan aquí, en `.claude/instagram/`, y se leen desde esta ruta.

## Actualización del 27-nov-2026

- **marketingskills** (https://github.com/coreyhaines31/marketingskills, commit 2bf95ed, 26-nov-2026): actualizadas `social`, `content-strategy`, `customer-research`, `copywriting`, `copy-editing`, `seo-audit`, `schema`, `product-marketing`, `lead-magnets` y `offers`. La versión anterior de cada una se ha sustituido, no se duplica. Añadida `referrals` (boca a boca y recomendaciones entre clientes). `ads` y `pricing` siguen como estaban: no se usan hasta el alta.
- **ig-hashtag-strategist** (https://github.com/sergebulaev/instagram-skills, commit 823c681, 18-nov-2026, MIT en `LICENSE-instagram-skills`): solo esta skill del paquete. Sus referencias compartidas se han copiado en `references/`. Para Undrlighted, máximo 5 hashtags, como dice la guía. La parte de publicación de ese paquete (Publora) **no** se ha traído.
- **seo-local** (https://github.com/AgriciDaniel/claude-seo, commit 5d7d85e, 26-nov-2026, MIT en `LICENSE-claude-seo`): SEO local de la web y del Perfil de Empresa de Google. El Perfil sigue en pausa: no verificar ni pedir reseñas sin que Adur lo decida.
- **No** se ha traído `ig-carousel-planner`: está pensado para carruseles didácticos (listas, mitos), publica por Publora y genera ilustraciones con IA. Se mantiene `ig-carousel`.

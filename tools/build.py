#!/usr/bin/env python3
"""Genera las páginas publicadas de undrlighted.es a partir de src/template.html.

Uso (desde la raíz del repo):
    python3 tools/build.py            # genera las páginas y el sitemap
    node tools/prerender.js           # escribe el texto en el HTML (necesita Playwright)

Cada idioma y cada servicio tiene su propia URL. Toda la web sigue siendo la misma
página con secciones por #hash; lo que cambia es el idioma, la sección inicial y la
cabecera (título, descripción, hreflang, og y JSON-LD).
"""
import html, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://undrlighted.es"
LASTMOD = "2026-10-27"
# Código de verificación de Google Search Console (método «Etiqueta HTML»): solo el valor de content="…"
GSC_TOKEN = ""

LOCALE = {"eu": "eu_ES", "es": "es_ES", "en": "en_GB"}
HOME = {"eu": "/", "es": "/es/", "en": "/en/"}

# Páginas de servicio: categoría de la galería, fotos y URL por idioma
SVC = {
    "retrato": {"cat": "estudio", "url": {"eu": "/erretratua/", "es": "/es/book-retrato/"},
                "ph": ["retrato-moda-estudio-13", "retrato-moda-estudio-10", "retrato-moda-estudio-12",
                       "retrato-moda-exteriores-25", "retrato-moda-exteriores-01", "retrato-moda-exteriores-07"]},
    "parejas": {"cat": "parejas", "url": {"eu": "/bikoteak/", "es": "/es/parejas/"},
                "ph": ["retrato-moda-exteriores-22", "retrato-moda-exteriores-18", "retrato-moda-exteriores-19",
                       "embarazo-09", "embarazo-05", "naturaleza-07"]},
    "embarazo": {"cat": "embarazo", "url": {"eu": "/haurdunaldia/", "es": "/es/embarazo/"},
                 "ph": ["embarazo-02", "embarazo-03", "embarazo-09", "embarazo-06", "embarazo-08", "embarazo-05"]},
    "deporte": {"cat": "deporte", "url": {"eu": "/kirola/", "es": "/es/deporte/"},
                "ph": ["deporte-11", "deporte-12", "deporte-14", "deporte-17", "deporte-15", "deporte-07"]},
}

META = {
    "home": {
        "eu": ("Argazkilaria Eibarren · Undrlighted",
               "Erretratua, booka, bikoteak, haurdunaldia eta kirola flasharekin, Eibartik Euskal Herri osora. Saio bakoitza xehetasunez prestatua."),
        "es": ("Fotógrafo en Eibar y Euskal Herria · Undrlighted",
               "Fotógrafo en Eibar: retrato, book, parejas, embarazo y deporte con flash. Cada sesión preparada al detalle, en toda Euskal Herria."),
        "en": ("Photographer in Eibar, Basque Country · Undrlighted",
               "Portrait, couples, maternity and sports photography with flash, from Eibar across the Basque Country. Every session planned in detail."),
    },
    "retrato": {
        "eu": ("Booka eta erretratua Euskal Herrian · Undrlighted",
               "Aktore eta modeloentzako booka eta flash bidezko erretratua, estudioan edo kalean. Eibartik Euskal Herri osora, aurretiko dosierrarekin eta online galeriarekin."),
        "es": ("Book y retrato en Euskal Herria · Undrlighted",
               "Book para actores y modelos y retrato con flash en estudio o en la calle. Desde Eibar a toda Euskal Herria, con dossier previo y galería online."),
    },
    "parejas": {
        "eu": ("Bikote argazki saioa Euskal Herrian · Undrlighted",
               "Bikote saioak flasharekin, gauez hirian, kostaldean edo mendian. Katalogoko jarrerarik gabe. Eibartik Euskal Herri osora."),
        "es": ("Sesión de fotos de pareja en Euskal Herria · Undrlighted",
               "Sesiones de pareja con flash, de noche en la ciudad, en la costa o en el monte. Sin poses de catálogo. Desde Eibar a toda Euskal Herria."),
    },
    "embarazo": {
        "eu": ("Haurdunaldiko argazki saioa Euskal Herrian · Undrlighted",
               "Haurdunaldiko argazkiak estudioan edo naturan, argi gutxirekin eta giroz beteak. Egokiena 28. eta 34. asteen artean. Eibartik Euskal Herri osora."),
        "es": ("Sesión de fotos de embarazo en Euskal Herria · Undrlighted",
               "Fotos de embarazo en estudio o en la naturaleza, en clave baja y con atmósfera. Lo ideal, entre las semanas 28 y 34. Desde Eibar a toda Euskal Herria."),
    },
    "deporte": {
        "eu": ("Kirol argazkilaritza Euskal Herrian · Undrlighted",
               "Runninga, traila, BTTa, motocrossa edo skatea flasharekin eta iragarki estiloan. Kirol argazkilaria Eibartik Euskal Herri osora."),
        "es": ("Fotografía deportiva en Euskal Herria · Undrlighted",
               "Running, trail, BTT, motocross o skate con flash y estilo de anuncio. Fotógrafo deportivo desde Eibar para toda Euskal Herria."),
    },
}

# Nombres de servicio para el JSON-LD (castellano en todas las versiones: es el dato, no el texto visible)
SERVICES_LD = ["Book y retrato", "Sesión de pareja", "Sesión de embarazo", "Fotografía deportiva", "Moda y editorial", "Eventos"]
SVC_LD_NAME = {"retrato": "Book y retrato", "parejas": "Sesión de pareja", "embarazo": "Sesión de embarazo", "deporte": "Fotografía deportiva"}

BUSINESS = {
    "@type": "ProfessionalService",
    "@id": SITE + "/#negocio",
    "name": "Undrlighted",
    "description": "Fotografía de retrato, moda, parejas, embarazo y deporte con flash, desde Eibar a toda Euskal Herria.",
    "url": SITE + "/",
    "image": SITE + "/img/retrato-moda-exteriores-01.jpg",
    "logo": SITE + "/img/icon-180.png",
    "telephone": "+34623828791",
    "email": "undrlighted@gmail.com",
    "address": {"@type": "PostalAddress", "addressLocality": "Eibar", "addressRegion": "Gipuzkoa", "addressCountry": "ES"},
    "areaServed": ["Eibar", "Gipuzkoa", "Bizkaia", "Araba", "Nafarroa", "Euskal Herria"],
    "knowsLanguage": ["eu", "es", "en"],
    "founder": {"@type": "Person", "name": "Adur", "jobTitle": "Fotógrafo"},
    "sameAs": ["https://www.instagram.com/undrlighted/"],
    "hasOfferCatalog": {
        "@type": "OfferCatalog", "name": "Sesiones de fotos",
        "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": n}} for n in SERVICES_LD],
    },
}


def pages():
    """Todas las páginas: (grupo, idioma, ruta URL, ruta inicial del SPA)."""
    out = [("home", L, HOME[L], "inicio") for L in ("eu", "es", "en")]
    for k, c in SVC.items():
        for L, u in c["url"].items():
            out.append((k, L, u, "svc/" + k))
    return out


def alternates(group):
    if group == "home":
        return dict(HOME)
    return dict(SVC[group]["url"])


def lang_target(group, L):
    """A dónde lleva el botón de idioma desde esta página."""
    alt = alternates(group)
    if L in alt:
        return alt[L]
    return HOME[L] + "#galeria/" + SVC[group]["cat"]


def jsonld(group, L, url, texts):
    title, desc = META[group][L]
    graph = [
        {"@type": "WebSite", "@id": SITE + "/#web", "url": SITE + "/", "name": "Undrlighted", "inLanguage": ["eu", "es", "en"]},
        BUSINESS,
        {"@type": "WebPage", "@id": SITE + url + "#pagina", "url": SITE + url, "name": title, "description": desc,
         "inLanguage": L, "isPartOf": {"@id": SITE + "/#web"}, "about": {"@id": SITE + "/#negocio"}},
    ]
    if group != "home":
        graph.append({"@type": "Service", "name": SVC_LD_NAME[group], "serviceType": SVC_LD_NAME[group],
                      "url": SITE + url, "provider": {"@id": SITE + "/#negocio"},
                      "areaServed": "Euskal Herria", "description": desc})
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Undrlighted", "item": SITE + HOME[L]},
            {"@type": "ListItem", "position": 2, "name": texts[L]["svc"][group]["nav"], "item": SITE + url}]})
        graph.append({"@type": "FAQPage", "inLanguage": L, "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in texts[L]["faq"]]})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)


def head(group, L, url, texts):
    title, desc = META[group][L]
    e = lambda x: html.escape(x, quote=True)
    img = SITE + ("/img/retrato-moda-exteriores-01.jpg" if group == "home" else f"/img/{SVC[group]['ph'][0]}.jpg")
    alt = alternates(group)
    lines = [f'<title>{e(title)}</title>',
             f'<meta name="description" content="{e(desc)}">',
             f'<link rel="canonical" href="{SITE}{url}">']
    lines += [f'<link rel="alternate" hreflang="{l2}" href="{SITE}{u}">' for l2, u in alt.items()]
    lines.append(f'<link rel="alternate" hreflang="x-default" href="{SITE}{alt.get("eu", "/")}">')
    lines += [f'<meta property="og:type" content="website">',
              f'<meta property="og:site_name" content="Undrlighted">',
              f'<meta property="og:locale" content="{LOCALE[L]}">']
    lines += [f'<meta property="og:locale:alternate" content="{LOCALE[l2]}">' for l2 in alt if l2 != L]
    lines += [f'<meta property="og:title" content="{e(title)}">',
              f'<meta property="og:description" content="{e(desc)}">',
              f'<meta property="og:url" content="{SITE}{url}">',
              f'<meta property="og:image" content="{img}">',
              '<meta name="twitter:card" content="summary_large_image">',
              '<meta name="color-scheme" content="dark">']
    if GSC_TOKEN and group == "home" and L == "eu":
        lines.append(f'<meta name="google-site-verification" content="{e(GSC_TOKEN)}">')
    lines.append('<script type="application/ld+json">\n' + jsonld(group, L, url, texts) + '\n</script>')
    return "\n".join(lines)


def lang_links(group, L):
    out = []
    for l2 in ("eu", "es", "en"):
        cur = "true" if l2 == L else "false"
        out.append(f'        <a href="{lang_target(group, l2)}" hreflang="{l2}" lang="{l2}" data-lang="{l2}" aria-current="{cur}">{l2.upper()}</a>')
    return "\n".join(out)


def load_texts(tpl):
    """Lee T (los textos de la web) del propio template con Node, para no duplicarlos."""
    import subprocess
    i = tpl.index("const T = {")
    j = tpl.index("\n};", i) + 3
    js = tpl[i:j] + "\nprocess.stdout.write(JSON.stringify(T));"
    return json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)


def main():
    tpl = (ROOT / "src/template.html").read_text(encoding="utf-8")
    texts = load_texts(tpl)
    svc_js = {k: {"cat": c["cat"], "ph": c["ph"], "url": c["url"]} for k, c in SVC.items()}
    tpl = tpl.replace("/*SVC*/{}", json.dumps(svc_js, ensure_ascii=False), 1)
    written = []
    for group, L, url, route in pages():
        page = tpl.replace("<!--HEAD-->", head(group, L, url, texts), 1)
        page = page.replace('<html lang="eu" data-lang="eu" data-route="inicio">',
                            f'<html lang="{L}" data-lang="{L}" data-route="{route}">', 1)
        page = page.replace("<!--LANGLINKS-->", lang_links(group, L), 1)
        page = page.replace('<a class="logo" href="#inicio"', f'<a class="logo" href="{HOME[L]}"', 1)
        dest = ROOT / url.strip("/") / "index.html" if url != "/" else ROOT / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page, encoding="utf-8")
        written.append(url)

    # sitemap con alternativas por idioma
    rows = []
    for group, L, url, _ in pages():
        alts = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{l2}" href="{SITE}{u}"/>' for l2, u in alternates(group).items())
        rows.append(f"  <url>\n    <loc>{SITE}{url}</loc>\n    <lastmod>{LASTMOD}</lastmod>{alts}\n  </url>")
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(rows) + "\n</urlset>\n", encoding="utf-8")
    (ROOT / "tools/pages.json").write_text(json.dumps(written, indent=1), encoding="utf-8")
    print("\n".join(written))


if __name__ == "__main__":
    main()

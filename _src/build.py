"""Genera la web publicada a partir de la plantilla (lux_tpl.html) y los datos (data.json).
Uso: python3 build.py <carpeta_del_repo>
Cada proyecto tiene su propia URL (/proyectos/<slug> y /en/projects/<slug>) con su título, descripción y texto indexable;
la plantilla es la misma aplicación que la vista previa, en modo de rutas por URL."""
import json, sys, re, hashlib, html, datetime, pathlib
HERE = pathlib.Path(__file__).parent
OUT = pathlib.Path(sys.argv[1])
BASE = 'https://ormendiguchia.vercel.app'
NAME = 'Óscar Ramón Mendiguchía'
DATAS = json.load(open(HERE / 'data.json'))   # {'es': {...}, 'en': {...}}
tpl = (HERE / 'lux_tpl.html').read_text()

def ver(path):
    f = OUT / path.lstrip('/')
    return hashlib.md5(f.read_bytes()).hexdigest()[:8] if f.exists() else 'x'
def assets(s):
    # rutas absolutas y versión en cada archivo, porque /img y /models se cachean un año
    s = s.replace("const PATHS = false;", "const PATHS = true;").replace("const IMG = s => 'img/' + s;", "const IMG = s => '/img/' + s;")
    s = re.sub(r"IMG\('([^']+)'\)", lambda m: "'/img/%s?v=%s'" % (m.group(1), ver('/img/' + m.group(1))), s)
    s = re.sub(r"(['\"])(?:/)?models/([\w-]+)\.glb(?:\.wasm)?\1", lambda m: "%s/models/%s.glb?v=%s%s" % (m.group(1), m.group(2), ver('/models/%s.glb' % m.group(2)), m.group(1)), s)
    s = re.sub(r"(['\"])(?:/)?img/([\w.-]+)\1", lambda m: "%s/img/%s?v=%s%s" % (m.group(1), m.group(2), ver('/img/' + m.group(2)), m.group(1)), s)
    return s
data_js = assets(json.dumps(DATAS, ensure_ascii=False))
body = assets(tpl.replace('/*__DATA__*/', data_js))
# la plantilla trae su propia cabecera mínima: se separa del cuerpo
body = re.sub(r'^\s*<meta charset="utf-8">\s*<title>.*?</title>\s*<meta name="claude:viewport-fit-sides"[^>]*>\s*', '', body, flags=re.S)
person = {"@context": "https://schema.org", "@type": "Person", "@id": BASE + "/#persona", "name": NAME, "givenName": "Óscar", "familyName": "Ramón Mendiguchía",
          "alternateName": ["Mendi", "Ó. Ramón Mendiguchía"], "jobTitle": "Ingeniero de producto",
          "description": "Estudiante de 4.º de Ingeniería en Diseño Industrial y Desarrollo de Producto (UVa). Diseño industrial, DFM, tolerancias y prototipado.",
          "url": BASE + "/", "image": BASE + "/og-portada.png",
          "affiliation": {"@type": "CollegeOrUniversity", "name": "Universidad de Valladolid", "url": "https://www.uva.es"},
          "knowsAbout": ["Diseño industrial", "Desarrollo de producto", "DFM", "GD&T", "Tolerancias", "Prototipado", "CATIA V5", "Fusion 360", "Impresión 3D"],
          "sameAs": ["https://www.linkedin.com/in/oramonmendiguchia", "https://www.youtube.com/@MendiMekanik"]}
site = {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": BASE + "/", "inLanguage": "es", "author": {"@id": BASE + "/#persona"}}
E = lambda s: html.escape(str(s), quote=True)
# cada página enlaza su equivalente en el otro idioma
def urls_of(lang, slug=None):
    if slug: return f"/proyectos/{slug}" if lang == 'es' else f"/en/projects/{slug}"
    return '/' if lang == 'es' else '/en'
def head(lang, title, desc, path, alt, image, ld):
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="theme-color" content="#ECEDEE">
<link rel="canonical" href="{BASE}{path}">
<link rel="alternate" hreflang="es" href="{BASE}{alt['es']}">
<link rel="alternate" hreflang="en" href="{BASE}{alt['en']}">
<link rel="alternate" hreflang="x-default" href="{BASE}{alt['es']}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{BASE}{path}">
<meta property="og:site_name" content="{NAME}">
<meta property="og:locale" content="{'es_ES' if lang == 'es' else 'en_GB'}">
<meta property="og:image" content="{image}">
<meta property="og:image:secure_url" content="{image}">
<meta property="og:image:alt" content="{E(title)}">
<meta name="twitter:image" content="{image}">
<meta name="twitter:title" content="{E(title)}">
<meta name="twitter:description" content="{E(desc)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="google-site-verification" content="4uTWSXBqHokK83WS0hxgulw6_TuUM_2P6R0Kl9rAQEQ">
<link rel="icon" href="/assets/favicon.svg">
<style>.seo{{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}}</style>
{''.join('<script type="application/ld+json">%s</script>' % json.dumps(x, ensure_ascii=False) for x in ld)}
</head>
<body>
"""
ROLE = {'es': 'Ingeniero de producto', 'en': 'Product engineer'}
def seo_text(lang, p=None):
    # texto para buscadores y lectores de pantalla; oculto a la vista para que no aparezca un instante antes de la portada
    d = DATAS[lang]
    if p is None:
        items = ''.join(f'<li><a href="{urls_of(lang, q["slug"])}">{E(q["name"])}</a>: {E(q["tagline"])}</li>' for q in d['projects'])
        inner = f'<h1>{NAME} · {ROLE[lang]}</h1><ul>{items}</ul>'
    else:
        txt = ''.join(f'<h2>{E(b["title"])}</h2>' + ''.join(f'<p>{E(t)}</p>' for t in b.get('body') or []) + ''.join(f'<p>{E(k)}: {E(v)}</p>' for k, v in b.get('specs') or []) for b in p['blocks'] if b['type'] == 'text')
        inner = f'<h1>{E(p["name"])}</h1><p>{E(p["tagline"])}</p>{txt}'
    return f'<div class="seo">{inner}</div>'
def page(lang, path, alt, title, desc, image, ld, p=None):
    b = body.replace('<main id="app"></main>', f'<main id="app">{seo_text(lang, p)}</main>')
    if lang == 'en':   # cabecera ya en inglés antes de que arranque la aplicación
        for x, y in (('>Proyectos</a>', '>Projects</a>'), ('>Sobre mí</a>', '>About</a>'), ('>Contacto</a>', '>Contact</a>'),
                     ('hreflang="en" lang="en" aria-label="English version">EN</a>', 'hreflang="es" lang="es" aria-label="Versión en español">ES</a>')):
            b = b.replace(x, y, 1)
    return head(lang, title, desc, path, alt, image, ld) + b + '\n</body>\n</html>\n'
DESC = {'es': 'Seis proyectos de producto: bocetos, planos acotados, modelos 3D, prototipos y lo que hubo que cambiar por el camino.',
        'en': 'Six product projects: sketches, dimensioned drawings, 3D models, prototypes and what had to change along the way.'}
og = f"{BASE}/og-portada.png?v={ver('/og-portada.png')}"
urls = []
(OUT / 'proyectos').mkdir(exist_ok=True); (OUT / 'en' / 'projects').mkdir(parents=True, exist_ok=True)
for lang in ('es', 'en'):
    alt = {l: urls_of(l) for l in ('es', 'en')}
    st = dict(site, url=BASE + urls_of(lang), inLanguage=lang)
    out = OUT / ('index.html' if lang == 'es' else 'en/index.html')
    out.write_text(page(lang, urls_of(lang), alt, f'{NAME} · {ROLE[lang]}', DESC[lang], og, [person, st]))
    urls.append(urls_of(lang))
    for p in DATAS[lang]['projects']:
        short = p['name'].split(' · ')[0]
        img = BASE + '/' + p['cover']['src'].lstrip('/')
        path = urls_of(lang, p['slug']); alt = {l: urls_of(l, p['slug']) for l in ('es', 'en')}
        ld = [{"@context": "https://schema.org", "@type": "CreativeWork", "name": p['name'], "description": p['tagline'], "image": img, "inLanguage": lang,
               "url": BASE + path, "creator": {"@id": BASE + "/#persona"}}]
        f = OUT / ('proyectos' if lang == 'es' else 'en/projects') / f"{p['slug']}.html"
        f.write_text(page(lang, path, alt, f'{short} · {NAME}', p['tagline'], img, ld, p))
        urls.append(path)
today = datetime.date.today().isoformat()
(OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join(f'<url><loc>{BASE}{u}</loc><lastmod>{today}</lastmod></url>\n' for u in urls) + '</urlset>\n')
print('ok', len(urls), 'páginas')

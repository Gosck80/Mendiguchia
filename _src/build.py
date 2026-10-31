"""Genera la web publicada a partir de la plantilla (lux_tpl.html) y los datos (data.json).
Uso: python3 build.py <carpeta_del_repo>
Cada proyecto tiene su propia URL (/proyectos/<slug>) con su título, descripción y texto indexable;
la plantilla es la misma aplicación que la vista previa, en modo de rutas por URL."""
import json, sys, re, hashlib, html, datetime, pathlib
HERE = pathlib.Path(__file__).parent
OUT = pathlib.Path(sys.argv[1])
BASE = 'https://ormendiguchia.vercel.app'
NAME = 'Óscar Ramón Mendiguchía'
d = json.load(open(HERE / 'data.json'))
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
data_js = assets(json.dumps(d, ensure_ascii=False))
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
def head(title, desc, path, image, ld):
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="theme-color" content="#ECEDEE">
<link rel="canonical" href="{BASE}{path}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{BASE}{path}">
<meta property="og:site_name" content="{NAME}">
<meta property="og:locale" content="es_ES">
<meta property="og:image" content="{image}">
<meta property="og:image:secure_url" content="{image}">
<meta property="og:image:alt" content="{E(title)}">
<meta name="twitter:image" content="{image}">
<meta name="twitter:title" content="{E(title)}">
<meta name="twitter:description" content="{E(desc)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="google-site-verification" content="4uTWSXBqHokK83WS0hxgulw6_TuUM_2P6R0Kl9rAQEQ">
<link rel="icon" href="/assets/favicon.svg">
{''.join('<script type="application/ld+json">%s</script>' % json.dumps(x, ensure_ascii=False) for x in ld)}
</head>
<body>
"""
def seo_text(p=None):
    # texto que ve un buscador o un navegador sin JavaScript; la aplicación lo sustituye al cargar
    if p is None:
        items = ''.join(f'<li><a href="/proyectos/{p["slug"]}">{E(p["name"])}</a>: {E(p["tagline"])}</li>' for p in d['projects'])
        return f'<h1>{NAME} · Ingeniero de producto</h1><ul>{items}</ul>'
    txt = ''.join(f'<h2>{E(b["title"])}</h2>' + ''.join(f'<p>{E(t)}</p>' for t in b.get('body') or []) + ''.join(f'<p>{E(k)}: {E(v)}</p>' for k, v in b.get('specs') or []) for b in p['blocks'] if b['type'] == 'text')
    return f'<h1>{E(p["name"])}</h1><p>{E(p["tagline"])}</p>{txt}'
def page(path, title, desc, image, ld, p=None):
    b = body.replace('<main id="app"></main>', f'<main id="app">{seo_text(p)}</main>')
    return head(title, desc, path, image, ld) + b + '\n</body>\n</html>\n'
home_desc = 'Seis proyectos de producto: bocetos, planos acotados, modelos 3D, prototipos y lo que hubo que cambiar por el camino.'
(OUT / 'index.html').write_text(page('/', f'{NAME} · Ingeniero de producto', home_desc, f"{BASE}/og-portada.png?v={ver('/og-portada.png')}", [person, site]))
(OUT / 'proyectos').mkdir(exist_ok=True)
urls = ['/']
for p in d['projects']:
    short = p['name'].split(' · ')[0]
    img = BASE + '/' + p['cover']['src'].lstrip('/')
    ld = [{"@context": "https://schema.org", "@type": "CreativeWork", "name": p['name'], "description": p['tagline'], "image": img,
           "url": f"{BASE}/proyectos/{p['slug']}", "creator": {"@id": BASE + "/#persona"}}]
    (OUT / 'proyectos' / f"{p['slug']}.html").write_text(page(f"/proyectos/{p['slug']}", f'{short} · {NAME}', p['tagline'], img, ld, p))
    urls.append(f"/proyectos/{p['slug']}")
today = datetime.date.today().isoformat()
(OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join(f'<url><loc>{BASE}{u}</loc><lastmod>{today}</lastmod></url>\n' for u in urls) + '</urlset>\n')
print('ok', len(urls), 'páginas')

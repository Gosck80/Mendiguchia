import json
# -*- coding: utf-8 -*-
"""Genera la web estática bilingüe.

Uso:
  python3 _src/build.py vercel .            -> sitio para GitHub/Vercel (imágenes en img/, CSS/JS en assets/)
  python3 build.py preview <salida> <map>    -> vista previa (imágenes remotas, CSS/JS en línea)
"""
import html, json, os, re, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from content import (SITE, UI, PROFILE, PROJECTS, MODELS, HOME, ABOUT_TABS, FICHA, NOW,
                     FAMILIES, ELEMENTS, CARDS)

MODE = sys.argv[1]
OUT = sys.argv[2]
REMOTE = {}
if MODE == 'preview':
    for line in open(sys.argv[3]):
        old, new, ext, sha = line.split()
        REMOTE[old] = '/_blob/' + new
IMAGES = json.load(open(os.path.join(HERE, 'images.json')))

CSS = open(os.path.join(HERE, 'site.css'), encoding='utf-8').read()
JS = open(os.path.join(HERE, 'site.js'), encoding='utf-8').read()
FONTS = 'https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap'
MV_URL = 'https://cdn.jsdelivr.net/npm/@google/model-viewer@3.5.0/dist/model-viewer.min.js'
DOMAIN = 'https://www.example.com'  # cambia por tu dominio cuando lo tengas

ISO = '<svg viewBox="20 210 818 440" aria-hidden="true"><polygon points="26,644 190,441 217,484 462,215 522,294 583,240 831,644" fill="currentColor"></polygon></svg>'
ICONS = {
    'pin': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M12 21s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>',
    'cap': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M2 9l10-5 10 5-10 5-10-5z"/><path d="M6 11v5c3 2 9 2 12 0v-5"/></svg>',
    'tool': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.5-.5-.5-2.5z"/></svg>',
    'lang': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/></svg>',
}


def e(s):
    return html.escape(s, quote=True)


def t(v, lang):
    return v[lang] if isinstance(v, dict) else v


def num(s, lang):
    s = t(s, lang)
    return re.sub(r'(\d),(\d)', r'\1.\2', s) if lang == 'en' else s


def pname(p, lang):
    return t(p['name'], lang)


def home_path(lang):
    if MODE == 'preview' and lang == 'es':
        return 'inicio.html'  # en la vista previa la raíz es el marco de teléfono
    return 'index.html' if lang == 'es' else 'en/index.html'


def proj_path(slug, lang):
    return 'proyectos/%s.html' % slug if lang == 'es' else 'en/projects/%s.html' % slug


def rel(frm, to):
    return ('../' * frm.count('/') + to) or './'


# Bocetos con trazo claro sobre transparente, convertidos a tinta oscura sobre blanco (nítidos sobre papel).
INK = {
    'cfaad6563a7e5a661c05b5756b27c1e6': '871c1b16f5ed5ce3d09930a9a395a3cb',
    '080d5c5247bb546d4dc1adaebca09973': 'd4dc6a919ef775bedf6bfa6ceaf0cb83',
    '9ed85c93eec136986a655971466688b5': '698da882640f03dac9de40dc766b62d7',
    '42e1e9e04acb72ff8be30410e45f7e77': '4532bffa0ebe92050fafbcbee29bf5a0',
    '7aee43e16af9a8b1a90186d01587518e': '190e2bb87fdd983818396e45d1c27a47',
    '5b6baa985735910393c36ef6e21082c9': '33d322d9dbe67f6341c04dc52f98448b',
}


def img_src(frm, iid):
    if iid in INK:
        return ('/_blob/' + INK[iid]) if MODE == 'preview' else rel(frm, 'img/' + iid[:8] + '-boceto.png')
    return REMOTE[iid] if MODE == 'preview' else rel(frm, 'img/' + IMAGES[iid]['file'])


def kind_of(iid):
    for p in PROJECTS:
        for b in p['blocks']:
            for it in b.get('items', []):
                if isinstance(it, tuple) and it[0] == iid:
                    return it[1]
    return 'photo'


def page(frm, lang, title, desc, body, alt_path, is_root=False, gate=False):
    other = 'en' if lang == 'es' else 'es'
    head = ['<title>%s</title>' % e(title),
            '<meta name="claude:viewport-fit-sides" content="cover">',
            '<meta name="description" content="%s">' % e(desc),
            '<meta name="theme-color" content="#EEF1F4">',
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
            '<link rel="stylesheet" href="%s">' % e(FONTS)]
    if MODE == 'vercel':
        head += ['<meta property="og:title" content="%s">' % e(title),
                 '<meta property="og:description" content="%s">' % e(desc),
                 '<meta property="og:type" content="website">',
                 '<meta property="og:image" content="https://ormendiguchia.vercel.app/og.png">',
                 '<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="627">',
                 '<meta name="twitter:card" content="summary_large_image">',
                 '<link rel="alternate" hreflang="%s" href="%s/%s">' % (lang, DOMAIN, frm),
                 '<link rel="alternate" hreflang="%s" href="%s/%s">' % (other, DOMAIN, alt_path),
                 '<link rel="icon" href="%s">' % rel(frm, 'assets/favicon.svg'),
                 '<link rel="stylesheet" href="%s">' % rel(frm, 'assets/site.css')]
        foot = '<script src="%s" defer></script>' % rel(frm, 'assets/site.js')
    else:
        head.append('<style>%s</style>' % CSS)
        foot = '<script>%s</script>' % JS
    lb = ('<div class="lb" id="lb" hidden role="dialog" aria-modal="true" aria-label="%s">'
          '<div class="lb-top"><span class="lb-cap"></span><button type="button" data-close>%s</button></div>'
          '<div class="lb-stage"><img alt=""></div>'
          '<div class="lb-nav"><button type="button" data-prev aria-label="←">←</button><span class="lb-count"></span><button type="button" data-next aria-label="→">→</button></div>'
          '</div>') % (e(t(UI['zoom_hint'], lang)), e(t(UI['close'], lang)))
    g = ''
    if gate:
        g = ('<div class="gate" id="gate" hidden><div><div class="mono-c">%s</div><h1>%s</h1><p>%s</p>'
             '<div class="row"><button class="btn fill" type="button" data-enter>%s →</button><a class="btn" data-other href="%s">%s →</a></div></div></div>') % (
            ISO, e(SITE['short']), e(t(HOME['gate_sub'], lang)), e(t(HOME['gate_enter'], lang)), rel(frm, alt_path), e(t(HOME['gate_other'], lang)))
    cad = ''
    if 'data-intro=' in body:
        head.append("<script>if(!matchMedia('(prefers-reduced-motion: reduce)').matches)document.documentElement.classList.add('pintro')</script>")
    if 'id="intro"' in body:
        head.append("<script>document.documentElement.classList.add('intro-run')</script>")
    mms = list(dict.fromkeys(re.findall(r'data-model="([^"]+)"', body)))
    if mms:
        head.append('<link rel="modulepreload" href="%s">' % MV_URL)
        head.append('<script type="module" src="%s"></script>' % MV_URL)
        for u in mms:
            head.append('<link rel="preload" href="%s" as="fetch" crossorigin>' % u)
    content = '\n'.join(head) + '\n' + g + '<div class="progress" aria-hidden="true"></div>' + cad + body + lb + foot
    return ('<!doctype html>\n<html lang="%s">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n%s\n</head>\n<body>\n%s%s<div class="progress" aria-hidden="true"></div>%s%s%s%s\n</body>\n</html>\n') % (
        lang, '\n'.join(head), '', g, cad, body, lb, foot)


def header(frm, lang, alt_path, on_home):
    h = rel(frm, home_path(lang))
    anc = (lambda a: '#' + a) if on_home else (lambda a: h + '#' + a)
    items = [('obras', T2('Proyectos', 'Projects')), ('sobre', T2('Perfil', 'Profile')),
             ('habilidades', T2('Habilidades', 'Skills')), ('contacto', T2('Contacto', 'Contact'))]
    pill = ''.join('<a href="%s"><i>%02d</i>%s</a>' % (anc(k), n, e(v[lang])) for n, (k, v) in enumerate(items, 1))
    es_on = lang == 'es'
    langs = ('<span class="on">ES</span><a href="%s" hreflang="en" aria-label="English">EN</a>' % rel(frm, alt_path)) if es_on else (
        '<a href="%s" hreflang="es" aria-label="Español">ES</a><span class="on">EN</span>' % rel(frm, alt_path))
    return ('<header class="top"><div class="wrap"><a class="brand" href="%s"><span class="mono-c">%s</span><span>%s</span></a>'
            '<div class="langs">%s</div></div></header>') % (
        h, ISO, e(SITE['short']), langs)


def T2(es, en):
    return {'es': es, 'en': en}


def footer(lang):
    return '<footer><div class="wrap"><span>© 2026 %s</span><span>%s</span></div></footer>' % ('Mendi', e(t(UI['footer'], lang)))


def model_cell(frm, key, lang, kind='cell'):
    m = MODELS[key]
    src = rel(frm, 'models/' + m['file'] + ('.wasm' if MODE == 'preview' else ''))
    attrs = 'data-model="%s" data-alt="%s" data-orbit="%s"' % (src, e(m['label']), m['orbit'])
    if kind == 'stage':
        return '<div class="stage-3d" %s><span class="hint">%s</span></div>' % (attrs, e(t(UI['model_hint'], lang)))
    if kind == 'hero':
        intro = (' data-intro="%s"' % m['intro']) if m.get('intro') else ''
        if m.get('introcam'):
            intro += " data-intro-cam='%s'" % json.dumps(m['introcam'])
        skip = T2('Toca para saltar', 'Tap to skip')[lang]
        return '<div class="hero-3d" %s data-zoom%s data-skip="%s"><div class="mv-shell"></div><span class="hint">%s</span></div>' % (attrs, intro, e(skip), e(t(HOME['model_hint'], lang)))
    load = '<div class="mload"><button class="btn" type="button">%s</button></div>' % e(t(UI['model_load'], lang))
    if kind == 'big':
        return '<div class="viewer" %s>%s<div class="vbar"><span>%s · <b>3D</b></span><span>%s</span></div></div>' % (
            attrs, load, e(m['label']), e(t(UI['model_hint'], lang)))
    return '<div class="mcell" %s>%s<div class="mlabel"><b>%s</b><a href="%s">%s →</a></div><span class="mhint">%s</span></div>' % (
        attrs, load, e(m['label']), rel(frm, proj_path(m['slug'], lang)), e(t(UI['see_project'], lang)), e(t(UI['model_hint'], lang)))


def figure(frm, lang, item):
    iid, kind, alt = item
    cls = 'shot' + (' paper' if kind != 'photo' else '') + (' paper-inv' if kind == 'drawing-inv' else '')
    src, a = img_src(frm, iid), e(t(alt, lang))
    return ('<figure class="%s"><button type="button" data-lb data-src="%s" data-alt="%s" data-kind="%s">'
            '<img src="%s" alt="%s" loading="lazy" decoding="async"></button><figcaption>%s</figcaption></figure>') % (cls, src, a, kind, src, a, a)


def sec_head(n, title, sub=''):
    s = '<div class="sec-h"><span class="balloon" aria-hidden="true">%d</span><span class="leader" aria-hidden="true"></span><h2>%s</h2></div>' % (n, e(title))
    if sub:
        s += '<p class="sec-p">%s</p>' % e(sub)
    return s


# ---------- portada: un único lienzo ----------
DOMAIN_OF = {
    'belug-04': T2('Dron · aerodinámica', 'Drone · aerodynamics'),
    'mecanismo-dosificador': T2('Envase · mecanismo', 'Packaging · mechanism'),
    'ovum-g1': T2('Gafas · biomaterial', 'Eyewear · biomaterial'),
    'bmw-m6-concept': T2('Automoción · CATIA V5', 'Automotive · CATIA V5'),
    'mies': T2('Mobiliario · sistema', 'Furniture · system'),
    'ingenieria-inversa': T2('Piezas restituidas · FDM', 'Restored parts · FDM'),
}
CANVAS_IMG = {'belug-04': '17b73057d4b4df564af667ecf51afc47', 'mecanismo-dosificador': 'f2fb83944bf7c5cf3e144b43ca224514', 'ovum-g1': '2cb779c5441111daad4faae643c6e9f3',
              'bmw-m6-concept': '85a0f99ae1062ed1cd758bd146866d26', 'mies': '4d61117edfb419c6beb4f4af908cbbcc', 'ingenieria-inversa': '157ac5fa1727e53c1a3e1f62847a9bd1'}
CANVAS_KIND = {'mies': 'paper'}
SCENE_IMG = {'bmw-m6-concept': ('9ed85c93eec136986a655971466688b5', 'line'), 'mies': ('6f9e755e17069b82f653c4bc3a66a5f2', 'line-inv')}


def tabbar(frm, lang, on_home):
    return ''


def build_home(lang):
    frm = home_path(lang)
    alt = home_path('en' if lang == 'es' else 'es')
    H = lambda k: t(HOME[k], lang)
    b = [header(frm, lang, alt, True), '<main class="wrap">']
    b.append('<div class="lead"><section class="intro" id="intro"><h1 class="mendi" aria-label="Mendi"><svg viewBox="0 8 215 76" aria-hidden="true"><text x="0" y="80">MENDI</text></svg></h1><p class="role">%s</p><p class="who"><span>%s</span></p></section>' % (
        re.sub(r'(?i)(ingeniero|engineer)', r'<em>\1</em>', e(H('hero_role')), count=1), e(H('hero_tags'))))
    # --- Portada: cuadrícula 2x2 de modelos; uno activo, el resto en reposo ---
    def msrc_of(key):
        return rel(frm, 'models/' + MODELS[key]['file'] + ('.wasm' if MODE == 'preview' else ''))
    sq = ''
    SQ_R = {'belug': 'auto', 'qiub': '128%', 'ovum': 'auto', 'rev': 'auto'}
    for key in ['belug', 'qiub', 'ovum', 'rev']:
        m = MODELS[key]
        pr = [p for p in PROJECTS if p['slug'] == m['slug']][0]
        n = PROJECTS.index(pr) + 1
        sq += ('<div class="cs" tabindex="0" role="button" aria-pressed="false" aria-label="%s"><span class="cs-3d" data-model="%s" data-alt="%s" data-orbit="%s" data-static></span>'
               '<span class="tag"><b>%02d</b>%s</span><a class="go" href="%s">%s →</a></div>') % (
            e(pname(pr, lang)), msrc_of(key), e(m['label']), ' '.join(m['orbit'].split()[:2] + [SQ_R[key]]), n, e(pname(pr, lang).split(' · ')[0]),
            rel(frm, proj_path(m['slug'], lang)), e(t(UI['see_project'], lang)))
    b.append(('<section class="hero3"><div class="sq">%s<span class="cross" aria-hidden="true"></span></div>'
              '<div class="sq-foot"><p class="hint">%s</p><div class="tblock" aria-hidden="true"><span>MENDI</span><span>UVa · 2026</span><span>HOJA 01</span></div></div></section></div>') % (
        sq, e(H('hero_hint'))))
    # --- Índice limpio de proyectos ---
    rows = ''
    for i, p in enumerate(PROJECTS, 1):
        rows += ('<a class="ix" href="%s"><span class="ix-n">%02d</span><span class="ix-t"><b>%s</b><em>%s</em></span>'
                 '<span class="ix-i"><img src="%s" alt="" loading="lazy" decoding="async"></span><span class="ix-a" aria-hidden="true">→</span></a>') % (
            rel(frm, proj_path(p['slug'], lang)), i, e(pname(p, lang)), e(t(DOMAIN_OF[p['slug']], lang)), img_src(frm, p['cover']))
    b.append('<section class="index" id="proyectos"><div class="ix-h"><h2>%s</h2><span>%02d</span></div>%s</section>' % (
        e(H('projects_h')), len(PROJECTS), rows))
    now = ''.join('<li>%s</li>' % e(t(x, lang)) for x in NOW)
    links = ''.join('<a href="%s" target="_blank" rel="noopener">%s ↗</a>' % (e(u), e(n)) for n, u in SITE['links'])
    mail = ('<code>%s</code>' % e(SITE['email'])) if SITE['email'] else ''
    b.append(('<section class="outro"><div class="pt"><span class="iso">%s</span><p class="bio">%s</p><ul class="now">%s</ul></div>'
              '<div class="pk"><b>%s</b>%s<div class="links">%s</div></div></section></main>') % (
        ISO, e(t(PROFILE['body'], lang)), now, e(H('contact_h')), mail, links))
    b.append(footer(lang))
    title = SITE['short'] + (' · Ingeniero de producto' if lang == 'es' else ' · Product engineer')
    return frm, page(frm, lang, title, t(UI['hero_sub'], lang), '\n'.join(b), alt)


def hero_block(frm, lang, ghost, text_html, visual_html, extra='', hid=''):
    """Cabecera común: nombre gigante en contorno detrás y la pieza (3D o imagen) encima."""
    return ('<section class="hero"%s><div class="ghost" aria-hidden="true" style="--len:%d">%s</div><div class="wrap">'
            '<div class="hero-txt">%s</div>%s</div>%s</section>') % (
        (' id="%s"' % hid) if hid else '', max(len(ghost), 5), e(ghost), text_html, visual_html, extra)


# ---------- proyecto ----------
def build_project(i, lang):
    p = PROJECTS[i]
    frm = proj_path(p['slug'], lang)
    alt = proj_path(p['slug'], 'en' if lang == 'es' else 'es')
    b = [header(frm, lang, alt, False), '<main class="wrap">']
    hk = kind_of(p['hero'])
    ghost = pname(p, lang).split(' · ')[0].upper()
    txt = '<div class="place">%02d / %02d · %s</div><h1>%s</h1><div class="tags">%s</div><div class="row"><a class="btn" href="%s#proyectos">← %s</a></div>' % (
        i + 1, len(PROJECTS), e(t(p['meta'][0][1], lang)), e(pname(p, lang)), e(t(p['tagline'], lang)), rel(frm, home_path(lang)), e(t(UI['back'], lang)))
    if p['model']:
        vis = model_cell(frm, p['model'], lang, 'hero')
    else:
        vis = '<div class="hero-img%s"><img src="%s" alt="%s" fetchpriority="high" style="view-transition-name:img-%s"></div>' % (' paper' if p.get('cover_kind', 'photo') != 'photo' else '', img_src(frm, p['cover']), e(pname(p, lang)), p['slug'])
    b[-1] = '<main>'
    hb = hero_block(frm, lang, ghost, txt, vis)
    if not p['model']:
        hb = hb.replace('<section class="hero"', '<section class="hero has-img"', 1)
    b.append(hb)
    b.append('<div class="wrap">')
    if p['model']:
        ck = p.get('cover_kind', 'photo')
        b.append('<div class="phero"><div class="frame%s"><img src="%s" alt="%s" style="view-transition-name:img-%s"></div></div>' % (
            ' paper' if ck != 'photo' else '', img_src(frm, p['cover']), e(pname(p, lang)), p['slug']))
    rows = [('f_project', pname(p, lang))] + p['meta'] + [('f_sheet', '%02d / %02d' % (i + 1, len(PROJECTS)))]
    b.append('<dl class="titleblock">' + ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (e(t(UI[k], lang)), e(t(v, lang))) for k, v in rows) + '</dl>')
    b.append('<div class="figures">' + ''.join('<div><b>%s</b><span>%s</span></div>' % (e(num(v, lang)), e(t(l, lang))) for v, l in p['figures']) + '</div>')
    for blk in p['blocks']:
        ty = blk['type']
        if ty == 'text':
            right = ''.join('<p>%s</p>' % e(t(x, lang)) for x in blk.get('body', []))
            if 'specs' in blk:
                right += '<dl class="specs">' + ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (e(t(k, lang)), e(t(v, lang))) for k, v in blk['specs']) + '</dl>'
            if 'aside' in blk:
                right += '<div class="aside-img gallery g-full">%s</div>' % figure(frm, lang, blk['aside'])
            b.append('<div class="block-text"><div><div class="kicker">%s</div><h2>%s</h2></div><div class="body">%s</div></div>' % (
                e(t(blk['kicker'], lang)), e(t(blk['title'], lang)), right))
        elif ty == 'images':
            b.append('<div class="gallery g-%s">%s</div>' % (blk['layout'], ''.join(figure(frm, lang, it) for it in blk['items'])))
        elif ty == 'table':
            head = ''.join('<th scope="col">%s</th>' % e(t(h, lang)) for h in blk['head'])
            body = ''.join('<tr>%s</tr>' % ''.join(('<td>%s</td>') % e(num(c, lang)) for c in r) for r in blk['rows'])
            b.append('<div class="tbl-wrap"><table><caption>%s</caption><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div><p class="tnote">%s</p>' % (
                e(t(blk['title'], lang)), head, body, e(t(blk['note'], lang))))
        elif ty == 'steps':
            lis = ''.join('<li>%s</li>' % e(t(x, lang)) for x in blk['items'])
            b.append('<div class="steps"><div><div class="kicker">%s</div><h2>%s</h2><ol>%s</ol></div><div class="gallery g-full">%s</div></div>' % (
                e(t(blk['kicker'], lang)), e(t(blk['title'], lang)), lis, figure(frm, lang, blk['image'])))
    nxt = PROJECTS[(i + 1) % len(PROJECTS)]
    b.append('<a class="next" href="%s"><div class="in"><div><span class="kicker">%s →</span><b>%s</b></div><div class="thumb"><img src="%s" alt="" loading="lazy"></div></div></a>' % (
        rel(frm, proj_path(nxt['slug'], lang)), e(t(UI['next'], lang)), e(pname(nxt, lang)), img_src(frm, nxt['cover'])))
    b.append('</div></main>')
    b.append(footer(lang))
    b.append(tabbar(frm, lang, False))
    return frm, page(frm, lang, '%s · %s' % (pname(p, lang), SITE['short']), t(p['tagline'], lang), '\n'.join(b), alt)


def write(path, text):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full) or OUT, exist_ok=True)
    open(full, 'w', encoding='utf-8').write(text)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    pages = []
    for lang in ['es', 'en']:
        pages.append(build_home(lang))
        pages += [build_project(i, lang) for i in range(len(PROJECTS))]
    for path, text in pages:
        write(path, text)
    if MODE == 'vercel':
        os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
        shutil.copyfile(os.path.join(HERE, 'site.css'), os.path.join(OUT, 'assets', 'site.css'))
        shutil.copyfile(os.path.join(HERE, 'site.js'), os.path.join(OUT, 'assets', 'site.js'))
    print('\n'.join(p for p, _ in pages))

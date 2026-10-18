# -*- coding: utf-8 -*-
"""Copia tus imágenes originales a img/ con el nombre que espera la web.

Busca en la carpeta que le indiques (y subcarpetas) los archivos cuyo contenido
coincide exactamente con las imágenes del portfolio (comparando su huella sha256).

Uso:  python3 _src/import_images.py "C:/Users/oscar/Documents/Portfolio"
"""
import hashlib, json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
images = json.load(open(os.path.join(HERE, 'images.json')))
by_sha = {v['sha256']: v['file'] for v in images.values()}
os.makedirs(os.path.join(ROOT, 'img'), exist_ok=True)

found = set()
for base, _, files in os.walk(sys.argv[1]):
    for f in files:
        if not f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            continue
        p = os.path.join(base, f)
        h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
        if h in by_sha and by_sha[h] not in found:
            shutil.copyfile(p, os.path.join(ROOT, 'img', by_sha[h]))
            found.add(by_sha[h])
            print('OK  ', by_sha[h], '<-', p)

missing = sorted(set(by_sha.values()) - found)
print('\n%d de %d imágenes encontradas.' % (len(found), len(by_sha)))
if missing:
    print('Faltan (cópialas a mano en img/ con este nombre):')
    for m in missing:
        print('  ', m)

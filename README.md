# Web de proyectos · Óscar Ramón Mendiguchía

Sitio estático bilingüe (ES en `/`, EN en `/en/`). Sin frameworks ni paso de build en Vercel: lo que hay en esta carpeta es lo que se publica.

## Estructura

```
index.html, proyectos/*.html      versión en español
en/index.html, en/projects/*.html versión en inglés
assets/                           CSS, JS y favicon
models/                           modelos 3D (.glb) del visor
img/                              imágenes (ver img/LISTA.txt)
_src/                             contenido y generador (no se publica)
```

## 1. Poner las imágenes

La web espera cada imagen en `img/` con un nombre concreto (`img/LISTA.txt` dice cuál es cuál).
Si tienes las imágenes originales que subiste al portfolio, este script las encuentra y las copia solo:

```
python _src/import_images.py "C:/ruta/a/tu/carpeta/de/imagenes"
```

Las que no encuentre te las lista para que las copies a mano con ese nombre.

## 2. Editar textos o proyectos

Todo el contenido está en `_src/content.py` (cada texto en español e inglés). Después de editar:

```
python _src/build.py vercel .
```

Regenera todas las páginas. Los estilos están en `_src/site.css` y el comportamiento en `_src/site.js`.
Añade tu LinkedIn y, si quieres, un email en `SITE` dentro de `content.py`. Cuando tengas dominio, cámbialo en `DOMAIN` dentro de `build.py`.

## 3. Publicar en Vercel

1. Crea un repositorio en GitHub y sube esta carpeta tal cual.
2. En vercel.com → *Add New → Project* → importa el repositorio.
3. *Framework Preset*: **Other**. Sin comando de build. *Output directory*: la raíz (`./`).
4. *Deploy*. Tendrás una URL `tu-proyecto.vercel.app`.
5. Dominio propio: *Settings → Domains* → añade el dominio y crea en tu proveedor los registros DNS que Vercel te indique.

Cada `git push` vuelve a publicar la web automáticamente.

## Modelos 3D

Los `.glb` se generaron a partir de tus STL/OBJ/GLB: orientados, centrados y simplificados para web. Para cambiar uno, sustituye el archivo en `models/` con el mismo nombre. El encuadre inicial de cada modelo se ajusta en `MODELS` dentro de `content.py` (`orbit`: ángulo horizontal, vertical y distancia).

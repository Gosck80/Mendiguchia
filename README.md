# Web de proyectos · Óscar Ramón Mendiguchía

Sitio estático en español. Sin paso de build en Vercel: lo que hay en esta carpeta es lo que se publica.

## Estructura

```
index.html, proyectos/*.html   páginas publicadas (generadas)
models/                        modelos 3D (.glb)
img/                           imágenes
assets/favicon.svg             icono
_src/                          plantilla, datos y generador (no se publica)
```

Cada proyecto tiene su URL (`/proyectos/<slug>`), con su título, descripción y texto indexable.
La navegación entre páginas se hace sin recargar (History API).

## Editar textos o proyectos

- Textos, imágenes y modelos de cada proyecto: `_src/data.json`.
- Diseño, animaciones y textos de la portada: `_src/lux_tpl.html`.

Después de editar, regenera las páginas desde la raíz del repo:

```
python3 _src/build.py .
```

El generador añade `?v=<hash>` a cada imagen y modelo, porque `/img` y `/models` se cachean un año.

## Redirecciones

La antigua versión en inglés (`/en/...`) redirige a la española (ver `vercel.json`).

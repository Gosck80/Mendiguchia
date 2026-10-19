// Entrada: se activa antes de pintar para que no haya parpadeo.
(function () {
  var intro = document.getElementById('intro');
  if (!intro) return;
  document.documentElement.classList.add('intro-run');
  var svg = intro.querySelector('svg'), txt = svg && svg.querySelector('text');
  function fit() {
    if (!txt) return;
    try {
      var b = txt.getBBox();
      svg.setAttribute('viewBox', [b.x - 1, b.y - 1, b.width + 2, b.height + 2].join(' '));
      var px = svg.getBoundingClientRect().width || 1;
      txt.style.strokeWidth = (1.5 * (b.width + 2) / px).toFixed(3);
    } catch (e) {}
  }
  fit();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
  addEventListener('resize', fit);
})();
(function () {
  'use strict';
  var lb = document.getElementById('lb');
  if (!lb) return;
  var stage = lb.querySelector('.lb-stage');
  var img = stage.querySelector('img');
  var cap = lb.querySelector('.lb-cap');
  var count = lb.querySelector('.lb-count');
  var items = Array.prototype.slice.call(document.querySelectorAll('[data-lb]'));
  var idx = 0, scale = 1, tx = 0, ty = 0, lastFocus = null;

  function apply() { img.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + scale + ')'; stage.classList.toggle('zoomed', scale > 1); }
  function reset() { scale = 1; tx = 0; ty = 0; img.style.transformOrigin = '0 0'; img.style.transform = ''; stage.classList.remove('zoomed'); }

  function show(i) {
    idx = (i + items.length) % items.length;
    var el = items[idx];
    reset();
    img.src = el.getAttribute('data-src');
    img.alt = el.getAttribute('data-alt') || '';
    cap.textContent = el.getAttribute('data-alt') || '';
    count.textContent = (idx + 1) + ' / ' + items.length;
    var kind = el.getAttribute('data-kind') || 'photo';
    stage.classList.toggle('paper', kind !== 'photo');
    stage.classList.toggle('paper-inv', kind === 'drawing-inv');
  }
  function open(i) { lastFocus = document.activeElement; show(i); lb.hidden = false; document.body.style.overflow = 'hidden'; lb.querySelector('[data-close]').focus(); }
  function close() { lb.hidden = true; document.body.style.overflow = ''; img.removeAttribute('src'); if (lastFocus) lastFocus.focus(); }

  items.forEach(function (el, i) { el.addEventListener('click', function () { open(i); }); });
  lb.querySelector('[data-close]').addEventListener('click', close);
  lb.querySelector('[data-prev]').addEventListener('click', function () { show(idx - 1); });
  lb.querySelector('[data-next]').addEventListener('click', function () { show(idx + 1); });
  lb.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft') show(idx - 1);
    else if (e.key === 'ArrowRight') show(idx + 1);
  });

  // Zoom y desplazamiento: clic para ampliar en el punto, arrastrar para mover, rueda para zoom.
  function zoomAt(cx, cy, next) {
    var r = img.getBoundingClientRect();
    var px = (cx - r.left) / scale, py = (cy - r.top) / scale; // punto en coordenadas de imagen
    var baseLeft = r.left - tx, baseTop = r.top - ty;
    scale = Math.max(1, Math.min(6, next));
    if (scale === 1) { tx = 0; ty = 0; } else { tx = cx - baseLeft - px * scale; ty = cy - baseTop - py * scale; }
    apply();
  }
  var drag = null, moved = false;
  stage.addEventListener('pointerdown', function (e) { if (e.target !== img) return; drag = { x: e.clientX, y: e.clientY, tx: tx, ty: ty }; moved = false; stage.setPointerCapture(e.pointerId); });
  stage.addEventListener('pointermove', function (e) {
    if (!drag) return;
    var dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (Math.abs(dx) + Math.abs(dy) > 4) moved = true;
    if (scale > 1) { tx = drag.tx + dx; ty = drag.ty + dy; apply(); }
  });
  stage.addEventListener('pointerup', function (e) {
    if (drag && !moved && e.target === img) zoomAt(e.clientX, e.clientY, scale > 1 ? 1 : 2.5);
    else if (drag && !moved && e.target === stage) close();
    drag = null;
  });
  stage.addEventListener('wheel', function (e) { e.preventDefault(); zoomAt(e.clientX, e.clientY, scale * (e.deltaY < 0 ? 1.2 : 1 / 1.2)); }, { passive: false });
})();

// Visores 3D: se cargan al pulsar o al entrar en pantalla, para no pesar en la carga inicial.
(function () {
  'use strict';
  var cells = Array.prototype.slice.call(document.querySelectorAll('[data-model]'));
  if (!cells.length) return;
  var libLoaded = false;
  function loadLib() {
    if (libLoaded) return; libLoaded = true;
    var s = document.createElement('script');
    s.type = 'module';
    s.src = 'https://cdn.jsdelivr.net/npm/@google/model-viewer@3.5.0/dist/model-viewer.min.js';
    document.head.appendChild(s);
  }
  // Zoom (pellizco, Ctrl/trackpad + rueda, botones) y vuelta automática a la vista original.
  function controls(cell, mv) {
    var orbit0 = cell.getAttribute('data-orbit') || 'auto auto auto', idle = null;
    function reset() {
      clearTimeout(idle);
      mv.cameraOrbit = orbit0; mv.cameraTarget = 'auto auto auto'; mv.fieldOfView = 'auto';
      mv.setAttribute('auto-rotate', '');
    }
    function later() { clearTimeout(idle); idle = setTimeout(reset, 4000); }
    function zoom(k) {
      var o = mv.getCameraOrbit();
      mv.cameraOrbit = o.theta + 'rad ' + o.phi + 'rad ' + (o.radius * k) + 'm';
      later();
    }
    // La rueda sola desplaza la página; con Ctrl (o el pellizco del trackpad) acerca el modelo.
    cell.addEventListener('wheel', function (ev) { if (!ev.ctrlKey) ev.stopPropagation(); else later(); }, { capture: true, passive: true });
    mv.addEventListener('camera-change', function (ev) { if (ev.detail && ev.detail.source === 'user-interaction') later(); });
    mv.addEventListener('dblclick', reset);
    var bar = document.createElement('div'); bar.className = 'mv-ctl';
    bar.innerHTML = '<button type="button" data-z="in" aria-label="Acercar">+</button><button type="button" data-z="out" aria-label="Alejar">−</button><button type="button" data-z="reset" aria-label="Vista inicial">↺</button>';
    bar.addEventListener('click', function (ev) {
      var b = ev.target.closest('button'); if (!b) return;
      var z = b.getAttribute('data-z');
      if (z === 'in') zoom(0.8); else if (z === 'out') zoom(1.25); else reset();
    });
    // Botón de animación: el modelo animado solo se descarga al pulsarlo y se reproduce en su sitio.
    var animUrl = cell.getAttribute('data-anim');
    if (animUrl && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
      var pb = document.createElement('button');
      pb.type = 'button'; pb.className = 'mv-play'; pb.textContent = '▶';
      pb.setAttribute('aria-label', cell.getAttribute('data-anim-label') || 'Play');
      pb.title = pb.getAttribute('aria-label');
      bar.insertBefore(pb, bar.firstChild);
      var keys = []; try { keys = JSON.parse(cell.getAttribute('data-anim-cam') || '[]'); } catch (e) {}
      var END = parseFloat(cell.getAttribute('data-anim-end')) || 3.0, busy = false;
      function run() {
        var ki = 0;
        if (keys.length) { mv.cameraOrbit = keys[0][1]; mv.cameraTarget = keys[0][2]; ki = 1; }
        else { mv.cameraOrbit = cell.getAttribute('data-anim-orbit'); mv.cameraTarget = 'auto auto auto'; }
        if (mv.jumpCameraToGoal) mv.jumpCameraToGoal();
        mv.animationName = 'intro';
        var done = false;
        function finish() {
          if (done) return; done = true;
          mv.pause(); mv.currentTime = 0;   // t=0 es el mecanismo montado: misma pose que el modelo en reposo
          mv.cameraTarget = 'auto auto auto'; mv.cameraOrbit = orbit0; mv.setAttribute('auto-rotate', '');
          busy = false; pb.classList.remove('on');
        }
        // Una sola reproducción: repetitions:1 + evento 'finished' + corte por tiempo como respaldo.
        mv.addEventListener('finished', finish, { once: true });
        try { mv.currentTime = 0; mv.play({ repetitions: 1 }); } catch (e) {}
        var last = 0;
        (function loop() {
          if (done) return;
          var t = mv.currentTime;
          while (ki < keys.length && t >= keys[ki][0]) { mv.cameraOrbit = keys[ki][1]; mv.cameraTarget = keys[ki][2]; ki++; }
          if (t >= END || t < last - 0.5) { finish(); return; }   // fin o vuelta atrás (bucle)
          last = t;
          requestAnimationFrame(loop);
        })();
      }
      pb.addEventListener('click', function (ev) {
        ev.stopPropagation();
        if (busy) return; busy = true; pb.classList.add('on'); clearTimeout(idle);
        mv.removeAttribute('auto-rotate');
        mv.setAttribute('interpolation-decay', '160');
        if (mv.getAttribute('src') !== animUrl) {
          mv.addEventListener('load', function () { run(); }, { once: true });
          mv.setAttribute('src', animUrl);
        } else run();
      });
    }
    cell.appendChild(bar);
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { es.forEach(function (en) { if (!en.isIntersecting) reset(); }); }).observe(cell);
  }
  function mount(cell) {
    if (cell.getAttribute('data-mounted')) return;
    cell.setAttribute('data-mounted', '1');
    loadLib();
    var mv = document.createElement('model-viewer');
    mv.setAttribute('src', cell.getAttribute('data-model'));
    mv.setAttribute('loading', 'eager');
    mv.setAttribute('reveal', 'auto');
    mv.setAttribute('alt', cell.getAttribute('data-alt') || '');
    var still = cell.hasAttribute('data-static');
    var scene = cell.hasAttribute('data-scene');
    if (!still) { mv.setAttribute('camera-controls', ''); mv.setAttribute('touch-action', 'pan-y'); }
    else { mv.style.pointerEvents = 'none'; }
    if (!cell.hasAttribute('data-scrub')) mv.setAttribute('auto-rotate', '');
    mv.setAttribute('auto-rotate-delay', (still || scene) ? '0' : '600');
    mv.setAttribute('rotation-per-second', still ? '24deg' : '18deg');
    mv.setAttribute('interaction-prompt', 'none');
    mv.setAttribute('shadow-intensity', scene ? '0' : '0.9');
    mv.setAttribute('shadow-softness', '0.8');
    mv.setAttribute('exposure', scene ? '1.15' : (cell.getAttribute('data-exposure') || '0.9'));
    var zoomable = cell.hasAttribute('data-zoom');
    if (!zoomable) mv.setAttribute('disable-zoom', '');
    else { mv.setAttribute('disable-pan', ''); mv.setAttribute('min-camera-orbit', 'auto 12deg 35%'); mv.setAttribute('max-camera-orbit', 'auto 168deg 260%'); }
    if (scene) { mv.setAttribute('interpolation-decay', '120'); }
    mv.setAttribute('environment-image', 'neutral');
    if (!zoomable) mv.setAttribute('max-camera-orbit', 'auto auto 400%');
    mv.setAttribute('camera-orbit', cell.getAttribute('data-orbit') || 'auto auto auto');
    var btn = cell.querySelector('.mload');
    if (btn) btn.remove();
    var host = cell.querySelector('.mv-shell') || cell;
    host.insertBefore(mv, host.firstChild);
    cell.dispatchEvent(new CustomEvent('mv-ready', { detail: mv }));
    if (zoomable) controls(cell, mv);
    if ((still || scene) && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
      // Arranque: gira rápido al aparecer y frena hasta su giro normal.
      mv.addEventListener('load', function () {
        var t0 = performance.now(), dur = 1800, from = 540, to = 24;
        (function spin(now) {
          var k = Math.min(1, (now - t0) / dur), ease = 1 - Math.pow(1 - k, 3);
          mv.setAttribute('rotation-per-second', (from + (to - from) * ease).toFixed(1) + 'deg');
          if (k < 1) requestAnimationFrame(spin);
        })(t0);
      }, { once: true });
    }
  }
  cells.forEach(function (c) {
    var b = c.querySelector('.mload button');
    if (b) b.addEventListener('click', function () { mount(c); });
  });
  // Portada al instante; los escenarios, al acercarse a pantalla (y se liberan al alejarse).
  cells.forEach(function (c) { if (!c.hasAttribute('data-lazy')) mount(c); });
  var lazy = cells.filter(function (c) { return c.hasAttribute('data-lazy'); });
  if (lazy.length && 'IntersectionObserver' in window) {
    var lio = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (en.isIntersecting) mount(en.target);
        else { var m = en.target.querySelector('model-viewer'); if (m) { m.remove(); en.target.removeAttribute('data-mounted'); } }
      });
    }, { rootMargin: '400px 0px' });
    lazy.forEach(function (c) { lio.observe(c); });
  } else lazy.forEach(mount);
})();

// Barra de progreso y sección activa en el menú.
(function () {
  var bar = document.querySelector('.progress');
  function onScroll() {
    if (!bar) return;
    var h = document.documentElement.scrollHeight - innerHeight;
    bar.style.width = (h > 0 ? (scrollY / h) * 100 : 0) + '%';
  }
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
  var links = Array.prototype.slice.call(document.querySelectorAll('.navl a[href^="#"]'));
  if (!links.length || !('IntersectionObserver' in window)) return;
  var map = {};
  links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (en) {
      if (en.isIntersecting) { links.forEach(function (a) { a.classList.remove('on'); }); var a = map[en.target.id]; if (a) a.classList.add('on'); }
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  Object.keys(map).forEach(function (id) { var s = document.getElementById(id); if (s) io.observe(s); });
})();

// Pestañas de "Sobre mí".
(function () {
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.chip[data-tab]'));
  tabs.forEach(function (t) {
    t.addEventListener('click', function () {
      tabs.forEach(function (x) { x.setAttribute('aria-selected', x === t ? 'true' : 'false'); });
      document.querySelectorAll('.acard').forEach(function (c) { c.hidden = c.getAttribute('data-panel') !== t.getAttribute('data-tab'); });
    });
  });
})();

// Copiar email.
(function () {
  var b = document.querySelector('[data-copy]');
  if (!b) return;
  b.addEventListener('click', function () {
    var txt = b.getAttribute('data-copy'), label = b.textContent;
    function ok() { b.textContent = b.getAttribute('data-done'); setTimeout(function () { b.textContent = label; }, 1600); }
    try { navigator.clipboard.writeText(txt).then(ok, function () { sel(); }); } catch (e) { sel(); }
    function sel() { var c = document.querySelector('.mail code'); var r = document.createRange(); r.selectNodeContents(c); var s = getSelection(); s.removeAllRanges(); s.addRange(r); }
  });
})();

// ===== Composición v3 =====
(function () {
  'use strict';
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var root = document.documentElement;
  var hsEarly = document.querySelector('.hscroll');
  if (hsEarly && !reduce && innerWidth >= 1000) root.classList.add('hz');

  // Cabecera con filete al hacer scroll
  var top = document.querySelector('.top');
  function onTop() { if (top) top.classList.toggle('scrolled', scrollY > 8); }
  addEventListener('scroll', onTop, { passive: true }); onTop();

  // Taller 3D: cambiar de pieza
  var view = document.querySelector('.st-view');
  if (view) {
    var opts = Array.prototype.slice.call(document.querySelectorAll('.st-opt'));
    var link = view.querySelector('.st-link');
    opts.forEach(function (b) {
      b.addEventListener('click', function () {
        opts.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        view.setAttribute('data-model', b.getAttribute('data-src'));
        view.setAttribute('data-orbit', b.getAttribute('data-orbit'));
        if (link) link.setAttribute('href', b.getAttribute('data-href'));
        var m = view.querySelector('model-viewer');
        if (m) { m.setAttribute('src', b.getAttribute('data-src')); m.setAttribute('camera-orbit', b.getAttribute('data-orbit')); m.setAttribute('alt', b.getAttribute('data-alt')); }
        else { var btn = view.querySelector('.mload button'); if (btn) btn.click(); }
      });
    });
  }
})();

(function () {
  var tl = Array.prototype.slice.call(document.querySelectorAll('.tabbar a[href^="#"]'));
  if (!tl.length || !('IntersectionObserver' in window)) return;
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (en) { if (en.isIntersecting) tl.forEach(function (a) { a.classList.toggle('on', a.getAttribute('href') === '#' + en.target.id); }); });
  }, { rootMargin: '-40% 0px -55% 0px' });
  tl.forEach(function (a) { var s = document.getElementById(a.getAttribute('href').slice(1)); if (s) io.observe(s); });
})();

// Portada 2x2: tocar una pieza la activa (manipulable); las demás quedan en reposo, borrosas y girando.
(function () {
  var sq = document.querySelector('.sq');
  if (!sq) return;
  var cells = Array.prototype.slice.call(sq.querySelectorAll('.cs'));
  function mvOf(c) { return c.querySelector('model-viewer'); }
  function setCtl(c, on) {
    var mv = mvOf(c), box = c.querySelector('.cs-3d');
    if (!mv) return;
    if (on) {
      mv.setAttribute('camera-controls', ''); mv.setAttribute('touch-action', 'pan-y');
      mv.setAttribute('auto-rotate-delay', '2500'); mv.style.pointerEvents = 'auto';
    } else {
      mv.removeAttribute('camera-controls'); mv.setAttribute('auto-rotate-delay', '0'); mv.style.pointerEvents = 'none';
      if (box && box.getAttribute('data-orbit')) mv.setAttribute('camera-orbit', box.getAttribute('data-orbit'));
    }
  }
  function activate(c) {
    cells.forEach(function (x) {
      var on = x === c;
      if (x.classList.contains('on') !== on) setCtl(x, on);
      x.classList.toggle('on', on); x.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    sq.classList.toggle('has-on', !!c);
  }
  cells.forEach(function (c) {
    c.addEventListener('click', function (ev) {
      if (ev.target.closest('.go')) return;
      if (!c.classList.contains('on')) { ev.preventDefault(); activate(c); }
    });
    c.addEventListener('keydown', function (ev) {
      if ((ev.key === 'Enter' || ev.key === ' ') && ev.target === c) { ev.preventDefault(); activate(c.classList.contains('on') ? null : c); }
    });
  });
  document.addEventListener('click', function (ev) { if (!sq.contains(ev.target)) activate(null); });
  document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') activate(null); });
})();

// Al entrar en un proyecto, siempre desde arriba: la pieza 3D es lo primero que se ve.
(function () {
  if (!document.querySelector('.titleblock')) return;
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  function top() { if (!location.hash) window.scrollTo(0, 0); }
  top();
  addEventListener('pageshow', top);
})();


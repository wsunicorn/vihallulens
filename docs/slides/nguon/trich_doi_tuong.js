// Read the active slide of slide_hoi_dong.html (final state, ?all) as a flat list of drawing
// primitives in slide pixels (1920 x 1080), in paint order. xuat_pptx.py turns each one into a
// native PowerPoint shape. Runs inside the page: `return extract()`.
(() => {
  const slide = document.querySelector('.slide.active');
  const box0 = slide.getBoundingClientRect(), K = box0.width / 1920;
  const out = [];
  const P = (x, y) => [(x - box0.left) / K, (y - box0.top) / K];
  const cs = e => getComputedStyle(e);

  function alphaOf(e) {          // cumulative opacity up to the slide
    let a = 1;
    for (let n = e; n && n !== slide.parentElement; n = n.parentElement) {
      const s = cs(n);
      if (s.display === 'none' || s.visibility === 'hidden') return 0;
      a *= parseFloat(s.opacity || 1);
    }
    return a;
  }
  function col(c) {               // 'rgb(a, b, c)' / 'rgba(...)' / '#hex' / 'none' -> [hex, alpha] or null
    if (!c || c === 'none' || c === 'transparent' || c.startsWith('url(')) return null;
    const d = document.createElement('div'); d.style.color = c; document.body.appendChild(d);
    const v = cs(d).color; d.remove();
    const m = v.match(/rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?/);
    if (!m) return null;
    const a = m[4] === undefined ? 1 : parseFloat(m[4]);
    if (a === 0) return null;
    return ['#' + [m[1], m[2], m[3]].map(x => (+x | 0).toString(16).padStart(2, '0')).join(''), a];
  }
  const SKIP = el => el.matches('.ctl, .tip, #notes, .dots, script, style, .stepcap .dots');

  // ---------------- SVG ----------------
  function svgPaint(e) {
    const s = cs(e);
    const fill = col(s.fill === 'none' ? null : s.fill), stroke = col(s.stroke === 'none' ? null : s.stroke);
    return { fill, fo: parseFloat(s.fillOpacity || 1), stroke, so: parseFloat(s.strokeOpacity || 1),
             sw: parseFloat(s.strokeWidth || 1), dash: s.strokeDasharray && s.strokeDasharray !== 'none' };
  }
  function ctm(e) { return e.getScreenCTM(); }
  function tp(m, x, y) { return P(m.a * x + m.c * y + m.e, m.b * x + m.d * y + m.f); }
  function svgWalk(e, depth) {
    if (SKIP(e)) return;
    const tag = e.tagName.toLowerCase();
    if (tag === 'foreignobject') { for (const c of e.children) htmlWalk(c); return; }
    if (tag === 'defs' || tag === 'clippath' || tag === 'marker' || tag === 'lineargradient') return;
    const a = alphaOf(e);
    if (a < 0.03) return;
    if (tag === 'g' || tag === 'svg') { for (const c of e.children) svgWalk(c, depth + 1); return; }
    const m = ctm(e), sc = Math.hypot(m.a, m.b) / K, p = svgPaint(e);
    if (tag === 'rect') {
      const x = +e.getAttribute('x') || 0, y = +e.getAttribute('y') || 0, w = e.width.baseVal.value, h = e.height.baseVal.value;
      if (w <= 0 || h <= 0) return;
      const [X, Y] = tp(m, x, y), [X2, Y2] = tp(m, x + w, y + h);
      out.push({ k: 'rect', x: Math.min(X, X2), y: Math.min(Y, Y2), w: Math.abs(X2 - X), h: Math.abs(Y2 - Y),
                 r: (+e.getAttribute('rx') || 0) * sc, ...p, sw: p.sw * sc, a });
    } else if (tag === 'circle' || tag === 'ellipse') {
      const cx = +e.getAttribute('cx') || 0, cy = +e.getAttribute('cy') || 0;
      const rx = tag === 'circle' ? +e.getAttribute('r') : +e.getAttribute('rx'), ry = tag === 'circle' ? rx : +e.getAttribute('ry');
      const [X, Y] = tp(m, cx - rx, cy - ry), [X2, Y2] = tp(m, cx + rx, cy + ry);
      out.push({ k: 'oval', x: X, y: Y, w: X2 - X, h: Y2 - Y, ...p, sw: p.sw * sc, a });
    } else if (tag === 'line') {
      const [X1, Y1] = tp(m, +e.getAttribute('x1'), +e.getAttribute('y1')), [X2, Y2] = tp(m, +e.getAttribute('x2'), +e.getAttribute('y2'));
      out.push({ k: 'poly', pts: [[X1, Y1], [X2, Y2]], closed: false, ...p, fill: null, sw: p.sw * sc, a });
    } else if (tag === 'path' || tag === 'polyline' || tag === 'polygon') {
      const L = e.getTotalLength();
      if (!(L > 0)) return;
      const d = e.getAttribute('d') || '';
      const closed = tag === 'polygon' || /z\s*$/i.test(d.trim());
      // split at move-to commands so separate subpaths stay separate
      const subs = tag === 'path' ? d.split(/(?=[Mm])/).filter(s => s.trim()) : [d];
      if (subs.length > 1 && tag === 'path') {
        for (const sd of subs) {
          const q = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          q.setAttribute('d', sd); e.parentNode.insertBefore(q, e);
          const LL = q.getTotalLength();
          if (LL > 0) {
            const n = Math.max(2, Math.min(160, Math.ceil(LL / 5))), pts = [];
            for (let i = 0; i <= n; i++) { const pt = q.getPointAtLength(LL * i / n); pts.push(tp(m, pt.x, pt.y)); }
            out.push({ k: 'poly', pts, closed: /z\s*$/i.test(sd.trim()), ...p, sw: p.sw * sc, a });
          }
          q.remove();
        }
        return;
      }
      const n = Math.max(2, Math.min(200, Math.ceil(L / 5))), pts = [];
      for (let i = 0; i <= n; i++) { const pt = e.getPointAtLength(L * i / n); pts.push(tp(m, pt.x, pt.y)); }
      out.push({ k: 'poly', pts, closed, ...p, sw: p.sw * sc, a });
    } else if (tag === 'text') {
      const t = e.textContent.trim();
      if (!t) return;
      const b = e.getBBox(), [X, Y] = tp(m, b.x, b.y), [X2, Y2] = tp(m, b.x + b.width, b.y + b.height);
      const s = cs(e);
      out.push({ k: 'text', x: X, y: Y, w: X2 - X, h: Y2 - Y, svg: true,
                 align: { start: 'l', middle: 'c', end: 'r' }[s.textAnchor] || 'l',
                 runs: [{ t, size: parseFloat(s.fontSize) * sc, b: +s.fontWeight >= 600, i: s.fontStyle === 'italic',
                          c: col(s.fill) || ['#18202E', 1], f: s.fontFamily, ls: 0 }], a, lh: 0 });
    } else if (tag === 'image') {
      const b = e.getBBox(), [X, Y] = tp(m, b.x, b.y), [X2, Y2] = tp(m, b.x + b.width, b.y + b.height);
      out.push({ k: 'img', src: e.getAttribute('href'), x: X, y: Y, w: X2 - X, h: Y2 - Y, a });
    }
  }

  // ---------------- HTML ----------------
  const FLOWLESS = d => d === 'flex' || d === 'inline-flex' || d === 'grid' || d === 'inline-grid';
  const inlineLike = c => { const d = cs(c).display, t = c.tagName.toLowerCase();
    return t !== 'svg' && t !== 'img' && (d === 'inline' || (d === 'inline-block' && !c.querySelector('svg,img,div'))); };
  function hasOwnText(e) {
    if (FLOWLESS(cs(e).display)) return false;          // flex/grid: every child is its own item
    for (const c of e.childNodes) {
      if (c.nodeType === 3 && c.textContent.trim()) return true;
      if (c.nodeType === 1 && !SKIP(c) && inlineLike(c) && c.textContent.trim()) return true;
    }
    return false;
  }
  let chips = [], lead = null, textNodes = [];
  function runsOf(e, out_runs, top) {
    for (const c of e.childNodes) {
      if (c.nodeType === 3) {
        let t = c.textContent.replace(/\s+/g, ' ');
        if (!t) continue;
        textNodes.push(c);
        const s = cs(e);
        if (s.textTransform === 'uppercase') t = t.toUpperCase();
        out_runs.push({ t, size: parseFloat(s.fontSize), b: +s.fontWeight >= 600, i: s.fontStyle === 'italic', c: col(s.color),
                        f: s.fontFamily, ls: parseFloat(s.letterSpacing) || 0, u: s.textDecorationLine.includes('underline') });
      } else if (c.nodeType === 1 && !SKIP(c)) {
        const tag = c.tagName.toLowerCase();
        if (tag === 'br') { out_runs.push({ br: true }); continue; }
        if (!inlineLike(c)) continue;
        const d = cs(c).display;
        // a label chip that opens the paragraph is drawn on its own; the text starts after it
        if (top && d === 'inline-block' && !out_runs.some(r => r.t && r.t.trim()) && col(cs(c).backgroundColor)) { lead = c; continue; }
        if (d === 'inline-block' || col(cs(c).backgroundColor)) chips.push(c);
        runsOf(c, out_runs, false);
      }
    }
  }
  function boxOf(e, a) {
    const s = cs(e), r = e.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return;
    const bg = col(s.backgroundColor);
    const bw = ['Top', 'Right', 'Bottom', 'Left'].map(k => parseFloat(s['border' + k + 'Width']) || 0);
    const bc = ['Top', 'Right', 'Bottom', 'Left'].map(k => col(s['border' + k + 'Color']));
    const [X, Y] = P(r.left, r.top);
    const rad = parseFloat(s.borderTopLeftRadius) || 0;
    if (!bg && !bw.some((w, i) => w > 0 && bc[i])) return;
    const uni = bw.every(w => w === bw[0]) && bc.every(c => c && bc[0] && c[0] === bc[0][0]);
    out.push({ k: 'rect', x: X, y: Y, w: r.width / K, h: r.height / K, r: Math.min(rad, r.height / 2 / K, r.width / 2 / K),
               fill: bg, fo: 1, stroke: uni && bw[0] > 0 ? bc[0] : null, so: 1, sw: uni ? bw[0] : 0, dash: s.borderTopStyle === 'dashed', a });
    if (!uni) {
      const sides = [[X, Y, r.width / K, bw[0]], [X + r.width / K - bw[1], Y, bw[1], r.height / K],
                     [X, Y + r.height / K - bw[2], r.width / K, bw[2]], [X, Y, bw[3], r.height / K]];
      sides.forEach((q, i) => { if (bw[i] > 0 && bc[i]) out.push({ k: 'rect', x: q[0], y: q[1], w: q[2], h: q[3], r: 0, fill: bc[i], fo: 1, stroke: null, sw: 0, a }); });
    }
  }
  function textRects(nodes) {
    const rs = [];
    for (const n of nodes) { const rg = document.createRange(); rg.selectNodeContents(n);
      for (const q of rg.getClientRects()) if (q.width > 0 && q.height > 0) rs.push(q); }
    return rs;
  }
  function emitText(e, a, runs, nodes, indent) {
    const s = cs(e), r = e.getBoundingClientRect();
    const pl = parseFloat(s.paddingLeft) + parseFloat(s.borderLeftWidth), pr = parseFloat(s.paddingRight) + parseFloat(s.borderRightWidth);
    const rects = textRects(nodes);
    if (!rects.length) return;
    const lines = new Set(rects.map(q => Math.round((q.top + q.bottom) / 2 / 6))).size;
    let x0 = r.left + pl, x1 = r.right - pr;
    if (lines === 1) { x0 = Math.min(...rects.map(q => q.left)); x1 = Math.max(...rects.map(q => q.right)); indent = 0; }
    const y0 = Math.min(...rects.map(q => q.top)), y1 = Math.max(...rects.map(q => q.bottom));
    const [X, Y] = P(x0, y0);
    const al = s.textAlign;
    const lh = s.lineHeight === 'normal' ? 0 : parseFloat(s.lineHeight);
    out.push({ k: 'text', x: X, y: Y, w: (x1 - x0) / K, h: (y1 - y0) / K,
               align: al === 'center' ? 'c' : (al === 'right' || al === 'end') ? 'r' : 'l',
               runs, a, lh, lines, indent: indent || 0 });
  }
  function htmlWalk(e) {
    if (e.nodeType !== 1 || SKIP(e)) return;
    const a = alphaOf(e);
    if (a < 0.03) return;
    const tag = e.tagName.toLowerCase();
    if (tag === 'svg') {
      const r = e.getBoundingClientRect();
      if (e.classList.contains('ic') || (r.width / K <= 90 && r.height / K <= 90 && !e.closest('.fig'))) {
        const [X, Y] = P(r.left, r.top), c = cs(e).color;
        out.push({ k: 'svgimg', svg: e.outerHTML.replace(/currentColor/g, c), x: X, y: Y, w: r.width / K, h: r.height / K, a });
      } else { for (const c of e.children) svgWalk(c, 0); }
      return;
    }
    if (tag === 'img') {
      const r = e.getBoundingClientRect(), [X, Y] = P(r.left, r.top);
      out.push({ k: 'img', src: e.currentSrc || e.src, x: X, y: Y, w: r.width / K, h: r.height / K, a });
      return;
    }
    boxOf(e, a);
    const own = hasOwnText(e);
    if (own) {
      chips = []; lead = null; textNodes = [];
      const runs = []; runsOf(e, runs, true);
      const myChips = chips, myLead = lead, nodes = textNodes;
      myChips.forEach(c => boxOf(c, a));
      let indent = 0;
      if (myLead) {
        const er = e.getBoundingClientRect(), es = cs(e), pl = parseFloat(es.paddingLeft) + parseFloat(es.borderLeftWidth);
        const lr = myLead.getBoundingClientRect(), ms = parseFloat(cs(myLead).marginRight) || 0;
        indent = (lr.right + ms - (er.left + pl)) / K;
        htmlWalk(myLead);
      }
      emitText(e, a, runs, nodes, indent);
    } else if (FLOWLESS(cs(e).display)) {
      for (const c of e.childNodes) if (c.nodeType === 3 && c.textContent.trim()) {   // anonymous flex item
        const s = cs(e);
        let t = c.textContent.trim(); if (s.textTransform === 'uppercase') t = t.toUpperCase();
        emitText(e, a, [{ t, size: parseFloat(s.fontSize), b: +s.fontWeight >= 600, i: s.fontStyle === 'italic', c: col(s.color), f: s.fontFamily, ls: parseFloat(s.letterSpacing) || 0 }], [c], 0);
      }
    }
    for (const c of e.children) {
      if (own && inlineLike(c)) continue;
      htmlWalk(c);
    }
  }
  // slide background
  const sb = col(cs(slide).backgroundColor);
  out.push({ k: 'bg', fill: sb });
  for (const c of slide.children) htmlWalk(c);
  return { notes: slide.dataset.notes || '', items: out };
})()

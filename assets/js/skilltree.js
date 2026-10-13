// ── Skill trees: hex view, list/tree toggle, and progress ──────
// Progress lives in this browser's localStorage only, one key per tree.
(function () {
  'use strict';

  const root = document.querySelector('[data-tree]');
  if (!root) return;
  const treeName = root.dataset.tree;
  const storeKey = 'lt-skilltree:' + treeName;

  // ── Storage (may be unavailable: private windows, blocked storage) ──
  function loadDone() {
    try { return new Set(JSON.parse(localStorage.getItem(storeKey)) || []); }
    catch (e) { return new Set(); }
  }
  function saveDone(done) {
    try { localStorage.setItem(storeKey, JSON.stringify(Array.from(done))); }
    catch (e) { /* progress just won't persist */ }
  }
  function loadPref(key) {
    try { return localStorage.getItem(key); } catch (e) { return null; }
  }
  function savePref(key, value) {
    try { localStorage.setItem(key, value); } catch (e) { /* ignore */ }
  }

  let done = loadDone();
  let onProgress = null;   // set below on tree pages

  // ── Checkboxes (skill page and list view) ──────────────────
  const boxes = Array.from(document.querySelectorAll('input[type="checkbox"][data-skill]'));
  boxes.forEach(function (box) {
    box.closest('label').hidden = false;
    box.checked = done.has(box.dataset.skill);
    box.addEventListener('change', function () { setDone(box.dataset.skill, box.checked); });
  });

  function setDone(slug, isDone) {
    done = loadDone();   // another tab may have changed it
    if (isDone) done.add(slug); else done.delete(slug);
    saveDone(done);
    boxes.forEach(function (b) { b.checked = done.has(b.dataset.skill); });
    if (onProgress) onProgress();
  }

  // ── [[id]] links to skills that don't have a page yet ──────
  // (the layout already turned the ones that do into real links)
  document.querySelectorAll('.skill-page .post-content').forEach(function (body) {
    const walker = document.createTreeWalker(body, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        return n.parentElement.closest('code, pre') ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
      }
    });
    const nodes = [];
    while (walker.nextNode()) if (/\[\[[\w-]+\]\]/.test(walker.currentNode.nodeValue)) nodes.push(walker.currentNode);
    nodes.forEach(function (node) {
      const frag = document.createDocumentFragment();
      node.nodeValue.split(/(\[\[[\w-]+\]\])/).forEach(function (part) {
        const m = /^\[\[([\w-]+)\]\]$/.exec(part);
        if (!m) { frag.append(part); return; }
        const em = document.createElement('em');
        em.textContent = m[1].replace(/-/g, ' ');
        frag.append(em, ' (coming soon)');
      });
      node.replaceWith(frag);
    });
  });

  const dataEl = document.getElementById('skilltree-data');
  if (!dataEl) return;   // a skill page: nothing else to do
  const data = JSON.parse(dataEl.textContent);

  // ── Hex geometry (pointy-top) ──────────────────────────────
  const R = 62;                      // center to corner
  const W = Math.sqrt(3) * R;        // flat side to flat side
  const GAP = 5;
  const DX = W + GAP;
  const DY = 1.5 * R + GAP * Math.sqrt(3) / 2;
  const MARGIN = 10;
  const SVG_NS = 'http://www.w3.org/2000/svg';

  // Grid text: rows of slot numbers ("." = empty); indented rows sit half a hex right.
  function parseGrid(text) {
    const cells = [];
    (text || '').split('\n').filter(function (l) { return l.trim(); }).forEach(function (line, row) {
      const shift = /^\s/.test(line) ? 0.5 : 0;
      line.trim().split(/\s+/).forEach(function (tok, col) {
        if (tok !== '.') cells.push({ slot: tok, row: row, col: col + shift });
      });
    });
    return cells;
  }

  function el(name, attrs, parent) {
    const node = document.createElementNS(SVG_NS, name);
    Object.keys(attrs || {}).forEach(function (k) { node.setAttribute(k, attrs[k]); });
    if (parent) parent.appendChild(node);
    return node;
  }

  function hexPoints(cx, cy) {
    const pts = [];
    for (let i = 0; i < 6; i++) {
      const a = Math.PI / 180 * (60 * i - 90);
      pts.push((cx + R * Math.cos(a)).toFixed(1) + ',' + (cy + R * Math.sin(a)).toFixed(1));
    }
    return pts.join(' ');
  }

  function wrap(text, maxChars) {
    const lines = [];
    let line = '';
    text.split(/\s+/).forEach(function (word) {
      if (line && (line + ' ' + word).length > maxChars) { lines.push(line); line = word; }
      else line = line ? line + ' ' + word : word;
    });
    if (line) lines.push(line);
    return lines;
  }

  function isDark(hex) {
    const m = /^#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i.exec(hex || '');
    if (!m) return false;
    const [r, g, b] = m.slice(1).map(function (h) { return parseInt(h, 16) / 255; });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.5;
  }

  const tiles = [];   // { slug, group, toggle } for refreshing done state

  function drawTree(container) {
    const cells = parseGrid(data.grid).filter(function (c) { return data.tiles[c.slot]; });
    if (!cells.length) return false;

    const minCol = Math.min.apply(null, cells.map(function (c) { return c.col; }));
    const minRow = Math.min.apply(null, cells.map(function (c) { return c.row; }));
    const maxCol = Math.max.apply(null, cells.map(function (c) { return c.col; }));
    const maxRow = Math.max.apply(null, cells.map(function (c) { return c.row; }));
    const width = (maxCol - minCol) * DX + W + 2 * MARGIN;
    const height = (maxRow - minRow) * DY + 2 * R + 2 * MARGIN;

    const svg = el('svg', {
      viewBox: '0 0 ' + width.toFixed(0) + ' ' + height.toFixed(0),
      role: 'group',
      'aria-label': 'Skill tree',
      class: 'skilltree-svg'
    }, container);
    svg.style.maxWidth = width.toFixed(0) + 'px';

    cells.forEach(function (c) {
      const slug = data.tiles[c.slot];
      const skill = data.skills[slug];
      const cx = MARGIN + W / 2 + (c.col - minCol) * DX;
      const cy = MARGIN + R + (c.row - minRow) * DY;
      const fill = skill ? (data.palette[skill.tier] || '#ffffff') : 'none';
      const ink = isDark(fill) ? '#ffffff' : '#111111';

      // A tile whose page doesn't exist yet is drawn as an unlinked outline.
      const group = el('g', { class: 'skilltree-tile' + (skill ? '' : ' skilltree-tile-pending') }, svg);
      const link = skill ? el('a', { href: skill.url }, group) : el('g', {}, group);
      el('title', {}, link).textContent = skill ? skill.title : slug + ' (coming soon)';
      el('polygon', { points: hexPoints(cx, cy), fill: fill }, link);

      const lines = wrap(skill ? skill.label : slug, 12);
      const lineH = 16;
      const text = el('text', { x: cx, 'text-anchor': 'middle', fill: skill ? ink : 'currentColor' }, link);
      lines.forEach(function (line, i) {
        const t = el('tspan', { x: cx, y: (cy - 3 + (i - (lines.length - 1) / 2) * lineH).toFixed(1) }, text);
        t.textContent = line;
      });
      if (!skill) return;

      // Done checkbox near the bottom of the hex; outside the link so it doesn't navigate.
      const toggle = el('g', {
        class: 'skilltree-toggle',
        role: 'checkbox',
        tabindex: '0',
        'aria-label': 'Done: ' + skill.title
      }, group);
      const by = cy + R - 22;
      el('circle', { cx: cx, cy: by.toFixed(1), r: 11, stroke: ink }, toggle);
      const tick = el('text', { x: cx, y: (by + 5).toFixed(1), 'text-anchor': 'middle', fill: ink }, toggle);
      tick.textContent = '✓';
      el('title', {}, toggle).textContent = 'Mark as done';
      function flip() { setDone(slug, !done.has(slug)); }
      toggle.addEventListener('click', flip);
      toggle.addEventListener('keydown', function (e) {
        if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); flip(); }
      });

      tiles.push({ slug: slug, group: group, toggle: toggle });
    });
    return true;
  }

  // ── Progress display ───────────────────────────────────────
  const slugs = Object.keys(data.skills);
  const progressEl = document.getElementById('skilltree-progress');

  function refresh() {
    tiles.forEach(function (t) {
      t.group.classList.toggle('done', done.has(t.slug));
      t.toggle.setAttribute('aria-checked', done.has(t.slug));
    });
    boxes.forEach(function (box) { box.checked = done.has(box.dataset.skill); });
    if (!progressEl) return;
    const n = slugs.filter(function (s) { return done.has(s); }).length;
    progressEl.textContent = n + ' of ' + slugs.length + ' done';
    if (n) {
      const reset = document.createElement('button');
      reset.className = 'skilltree-reset';
      reset.textContent = 'reset';
      reset.addEventListener('click', function () {
        if (!confirm('Clear your progress on this tree?')) return;
        done = new Set();
        saveDone(done);
        refresh();
      });
      progressEl.append(' · ', reset);
    }
  }

  // ── Tree / list toggle ─────────────────────────────────────
  const treeView = document.getElementById('skilltree-tree');
  const listView = document.getElementById('skilltree-list');
  const viewButtons = Array.from(document.querySelectorAll('[data-view]'));
  const viewKey = 'lt-skilltree-view';

  function setView(view) {
    treeView.hidden = view !== 'tree';
    listView.hidden = view !== 'list';
    viewButtons.forEach(function (b) { b.classList.toggle('active', b.dataset.view === view); });
  }

  if (drawTree(treeView)) {
    viewButtons.forEach(function (b) {
      b.hidden = false;
      b.addEventListener('click', function () { savePref(viewKey, b.dataset.view); setView(b.dataset.view); });
    });
    // Phones get the list by default; the hexes are too small to read there.
    setView(loadPref(viewKey) || (window.innerWidth < 640 ? 'list' : 'tree'));
  }
  onProgress = refresh;
  refresh();

})();

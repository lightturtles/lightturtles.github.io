// ── Skill pages: the "done" checkbox and [[id]] links ──────────
// Progress lives in this browser's localStorage only, one key per tree
// (the same key metro.js uses on the tree's map).
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

  let done = loadDone();

  // ── Checkboxes ─────────────────────────────────────────
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

})();

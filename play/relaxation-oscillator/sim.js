// Relaxation oscillator page: controls, plots and export. The simulation
// itself is simulate() in simulate.js, which the page also shows as its code.
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const css = getComputedStyle(document.documentElement);
  const token = (name) => css.getPropertyValue(name).trim();

  function download(blob, filename) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }

  // ── Controls: each slider is paired with a number box ─────────
  const ids = ["ra", "rb", "c", "v", "dt", "tend"];
  const values = {};

  for (const id of ids) {
    const slider = $(id);
    const box = document.querySelector(`input[type="number"][data-for="${id}"]`);
    values[id] = +slider.value;
    box.value = slider.value;

    slider.addEventListener("input", () => {
      values[id] = +slider.value;
      box.value = slider.value;
      box.classList.remove("bad");
      run();
    });
    // Typed values can fall between slider steps; the slider just shows the nearest.
    box.addEventListener("input", () => {
      const x = box.valueAsNumber;
      const ok = Number.isFinite(x) && x >= +box.min && x <= +box.max;
      box.classList.toggle("bad", !ok);
      if (!ok) return;
      values[id] = x;
      slider.value = x;
      run();
    });
    box.addEventListener("change", () => {
      box.value = values[id];
      box.classList.remove("bad");
    });
  }

  // ── Plots ─────────────────────────────────────────────────────
  const Q1_COLOR = token("--teal");
  const Q2_COLOR = token("--orange");
  const AXIS = { stroke: token("--text-muted"), grid: { stroke: token("--bg-card") }, ticks: { stroke: token("--border") } };
  const fmtV = (u, v) => (v == null ? "–" : v.toFixed(2) + " V");

  // Keep both plots on the same time window when either one zooms.
  const plots = [];
  let syncing = false;
  function syncZoom(src) {
    if (syncing) return;
    syncing = true;
    const { min, max } = src.scales.x;
    for (const p of plots) if (p !== src) p.setScale("x", { min, max });
    syncing = false;
  }

  function makePlot(el, labels) {
    const opts = {
      width: el.clientWidth,
      height: 240,
      scales: { x: { time: false } },
      cursor: { sync: { key: "osc" }, drag: { x: true, y: false } },
      axes: [{ label: "Time (ms)", ...AXIS }, { label: "Volts", ...AXIS }],
      series: [
        { label: "t", value: (u, v) => (v == null ? "–" : v.toFixed(3) + " ms") },
        { label: labels[0], stroke: Q1_COLOR, width: 2, value: fmtV },
        { label: labels[1], stroke: Q2_COLOR, width: 2, value: fmtV },
      ],
      hooks: { setScale: [(u, key) => key === "x" && syncZoom(u)] },
    };
    return new uPlot(opts, [[], [], []], el);
  }

  const collectors = makePlot($("plot-collectors"), ["V_CE1", "V_CE2"]);
  const bases = makePlot($("plot-bases"), ["V_BE1", "V_BE2"]);
  plots.push(collectors, bases);

  new ResizeObserver(() => {
    for (const p of plots) p.setSize({ width: p.root.parentElement.clientWidth, height: 240 });
  }).observe($("plot-collectors"));

  // ── Run ───────────────────────────────────────────────────────
  let sim = null;

  function run() {
    const RA = values.ra * 1e3;
    const RB = values.rb * 1e3;
    const C = values.c * 1e-9;
    const V = values.v;
    const dt = values.dt * 1e-6;
    sim = simulate(RA, RB, C, V, dt, values.tend * 1e-3);

    const tMs = sim.t.map((s) => s * 1e3);
    collectors.setData([tMs, sim.vce1, sim.vce2]);
    bases.setData([tMs, sim.vbe1, sim.vbe2]);

    $("warn-tau").textContent = (RA * C * 1e6).toFixed(0);
    $("warn").hidden = !(dt > 0.2 * RA * C);
  }

  // ── Export ────────────────────────────────────────────────────
  // CSV of the whole run, matching the notebook's columns and %.6g format.
  $("dl-csv").addEventListener("click", () => {
    const cols = ["t", "q1", "q2", "vc1", "vc2", "vce1", "vbe1", "vce2", "vbe2"];
    const g6 = (x) => String(Number(x.toPrecision(6)));
    const rows = [cols.join(",")];
    for (let k = 0; k < sim.t.length; k++) rows.push(cols.map((c) => g6(sim[c][k])).join(","));
    download(new Blob([rows.join("\n") + "\n"], { type: "text/csv" }), "relaxation_oscillator.csv");
  });

  // PNG of a graph as currently shown: title, legend of visible traces, then
  // uPlot's own canvas (which already holds the axes and lines).
  function savePng(u, title, filename) {
    const src = u.ctx.canvas;
    const s = src.width / src.getBoundingClientRect().width; // device pixel ratio
    const pad = 16 * s, titleH = 28 * s, legendH = 24 * s;
    const out = document.createElement("canvas");
    out.width = src.width + 2 * pad;
    out.height = src.height + titleH + legendH + 2 * pad;
    const ctx = out.getContext("2d");

    ctx.fillStyle = token("--bg");
    ctx.fillRect(0, 0, out.width, out.height);
    ctx.textBaseline = "middle";
    ctx.fillStyle = token("--primary");
    ctx.font = `600 ${16 * s}px ${token("--font-mono")}`;
    ctx.fillText(title, pad, pad + titleH / 2);

    let x = pad;
    const y = pad + titleH + legendH / 2;
    ctx.font = `${13 * s}px ${token("--font-mono")}`;
    u.series.forEach((series, i) => {
      if (i === 0 || !series.show) return;
      ctx.strokeStyle = typeof series.stroke === "function" ? series.stroke(u, i) : series.stroke;
      ctx.lineWidth = 2 * s;
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x + 20 * s, y);
      ctx.stroke();
      ctx.fillStyle = token("--text");
      ctx.fillText(series.label, x + 26 * s, y);
      x += 26 * s + ctx.measureText(series.label).width + 20 * s;
    });

    ctx.drawImage(src, pad, pad + titleH + legendH);
    out.toBlob((blob) => download(blob, filename), "image/png");
  }

  $("dl-png-collectors").addEventListener("click", () => savePng(collectors, "Collector voltages", "collector_voltages.png"));
  $("dl-png-bases").addEventListener("click", () => savePng(bases, "Base voltages", "base_voltages.png"));

  run();
})();

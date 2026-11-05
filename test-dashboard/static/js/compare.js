/* ── ATE Dashboard — Compare (A vs B) page ── */
"use strict";

let META   = null;
let charts = {};
const CMP_A_COLOR = "#3b82f6";
const CMP_B_COLOR = "#f59e0b";
// palette for N-way (manual) comparison
const CMP_PALETTE = ["#3b82f6","#f59e0b","#10b981","#ec4899","#8b5cf6",
                     "#06b6d4","#ef4444","#a3e635","#f97316","#14b8a6"];

// ── Helpers ──────────────────────────────────────────────────────────
function qs(id) { return document.getElementById(id); }
function fmt(n, d=1) { return (n==null) ? "—" : Number(n).toFixed(d); }
function destroyChart(id) { if (charts[id]) { charts[id].destroy(); delete charts[id]; } }

const CAT_CLASS = {
  "DC":"cat-DC", "IDDQ":"cat-IDDQ", "AC":"cat-AC", "Timing":"cat-TIME",
  "Memory":"cat-MEM", "Scan":"cat-SCAN", "Functional":"cat-FUNC",
  "Data Eye":"cat-EYE", "Assembly":"cat-ASM", "Open/Short":"cat-OPEN",
  "Contact":"cat-OPEN",
  "HBM-TSV":"cat-HBM", "HBM-PHY":"cat-HBM", "HBM-Eye":"cat-HBM",
  "HBM-MBiST":"cat-HBM", "HBM-ECC":"cat-HBM",
};
function catBadge(cat) {
  return `<span class="cat ${CAT_CLASS[cat] || "cat-DC"}">${cat}</span>`;
}

// Each returns an array of {value, label}
const DIM_VALUES = {
  run:            () => META.runs.map(r => ({
                          value: r.run_id,
                          label: `${r.run_id} · ${r.run_label} · ${r.product} · ${r.test_date}` })),
  lot:            () => META.lots.map(l => ({
                          value: l.lot_id,
                          label: `${l.lot_id} · ${l.product} · ${l.first_date} · ${l.run_count} run(s)` })),
  tp_rev:         () => META.tp_revs.map(v => ({value:v, label:v})),
  tester:         () => META.testers.map(v => ({value:v, label:v})),
  socket:         () => META.sockets.map(v => ({value:v, label:v})),
  product:        () => META.products.map(v => ({value:v, label:v})),
  product_family: () => META.families.map(v => ({value:v, label:v})),
  proc_node:      () => META.proc_nodes.map(v => ({value:v, label:v})),
  test_step:      () => META.test_steps.map(v => ({value:v, label:v})),
};

// ── Init ─────────────────────────────────────────────────────────────
async function init() {
  META = await fetch("/api/meta").then(r => r.json());
  // Test Step scope filter
  const stepSel = qs("cmp-step");
  META.test_steps.forEach(v =>
    stepSel.appendChild(Object.assign(document.createElement("option"), {value:v, textContent:v})));
  setQuick("30d", false);
  onCmpDimChange();
}

// Re-run whichever comparison mode is active (after a scope change)
function refreshCompare() {
  const dim = qs("cmp-dim").value;
  if (dim === "runlist")       runManualCompare();
  else if (dim === "runmulti") runMultiCompare();
  else                         loadCompare();
}

// Apply the global scope filters (currently Test Step) to a params object.
// Skipped when the comparison dimension IS test_step (would contradict).
function applyScope(p) {
  const step = qs("cmp-step") ? qs("cmp-step").value : "ALL";
  if (step && step !== "ALL" && qs("cmp-dim").value !== "test_step")
    p.set("test_step", step);
}

// ── Date quick-select ─────────────────────────────────────────────────
function setQuick(mode, doRefresh=true) {
  document.querySelectorAll(".date-btn").forEach(b => b.classList.remove("active"));
  event?.target?.classList.add("active");

  const today = META ? META.date_max : new Date().toISOString().slice(0,10);
  const from  = qs("f-date-from");
  const to    = qs("f-date-to");
  to.value = today;

  if (mode === "today")   from.value = today;
  else if (mode === "7d") from.value = offsetDate(today, -7);
  else if (mode === "30d") from.value = offsetDate(today, -30);
  else if (mode === "90d") from.value = META ? META.date_min : offsetDate(today, -90);
  else { from.value = META ? META.date_min : ""; to.value = META ? META.date_max : ""; }

  if (doRefresh) refreshCompare();
}
function offsetDate(dateStr, days) {
  const d = new Date(dateStr); d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}
function onDateChange() {
  document.querySelectorAll(".date-btn").forEach(b => b.classList.remove("active"));
  refreshCompare();
}

// ── Dimension + A/B selectors ─────────────────────────────────────────
function onCmpDimChange() {
  const dim        = qs("cmp-dim").value;
  const isLot      = (dim === "lot");
  const isRunList  = (dim === "runlist");    // two boxes, each combined -> A vs B
  const isRunMulti = (dim === "runmulti");   // one box, each run separate -> N-way
  const isManual   = isRunList || isRunMulti;

  // Populate A/B dropdowns only for dimensions that have a value list
  if (DIM_VALUES[dim]) {
    const vals = DIM_VALUES[dim]();
    const aSel = qs("cmp-a"), bSel = qs("cmp-b");
    aSel.innerHTML = ""; bSel.innerHTML = "";
    vals.forEach(v => {
      aSel.appendChild(Object.assign(document.createElement("option"), {value:v.value, textContent:v.label}));
      bSel.appendChild(Object.assign(document.createElement("option"), {value:v.value, textContent:v.label}));
    });
    if (vals.length > 1) bSel.selectedIndex = 1;
  }

  // A/B dropdown groups show for the dropdown dimensions only
  qs("grp-a").style.display       = isManual ? "none" : "";
  qs("grp-b").style.display       = isManual ? "none" : "";
  qs("cmp-main-vs").style.display = isManual ? "none" : "";

  // For the Lot dimension, reveal a per-side Run picker so the user chooses
  // exactly which run of each lot to compare (runs are never combined).
  qs("grp-a-run").style.display = isLot ? "" : "none";
  qs("grp-b-run").style.display = isLot ? "" : "none";
  if (isLot) { fillRunPicker("a"); fillRunPicker("b"); }

  // Manual text-input modes
  qs("grp-runlist").style.display  = isRunList  ? "" : "none";
  qs("grp-runmulti").style.display = isRunMulti ? "" : "none";

  if (isRunList)       runManualCompare();   // A vs B combined
  else if (isRunMulti) runMultiCompare();    // multiple runs separate
  else                 loadCompare();
}

// Populate the Run (A|B) dropdown with the runs belonging to the chosen lot.
function fillRunPicker(side) {
  const lotId = qs(`cmp-${side}`).value;
  const sel   = qs(`cmp-${side}-run`);
  const runs  = META.runs.filter(r => r.lot_id === lotId)
                         .sort((x, y) => x.run_num - y.run_num);
  sel.innerHTML = "";
  runs.forEach(r => sel.appendChild(Object.assign(document.createElement("option"),
    { value: r.run_id, textContent: `${r.run_label} (${r.run_id.split("-").pop()}) · ${r.test_date}` })));
  // default to the latest run
  if (runs.length) sel.selectedIndex = runs.length - 1;
}

// A/B lot selector changed → refresh that side's run picker (lot dim only)
function onSideChange(side) {
  if (qs("cmp-dim").value === "lot") fillRunPicker(side);
  loadCompare();
}

// Params = date range + chosen dimension override + global scope (step)
function cmpParams(dim, value, extra={}) {
  const p = new URLSearchParams();
  const df = qs("f-date-from")?.value;
  const dt = qs("f-date-to")?.value;
  if (df) p.set("date_from", df);
  if (dt) p.set("date_to", dt);
  p.set(dim, value);
  Object.entries(extra).forEach(([k,v]) => p.set(k, String(v)));
  applyScope(p);
  return p;
}
async function cmpFetch(path, dim, value, extra={}) {
  return fetch(`${path}?${cmpParams(dim, value, extra)}`).then(r => r.json());
}

// Restore the two-way (A vs B) table header + KPI grid after manual mode
function restoreTwoWayLayout() {
  qs("cmp-kpis").style.gridTemplateColumns = "";   // fall back to CSS (4 cols)
  qs("cmp-table").querySelector("thead").innerHTML =
    `<tr><th>Test Name</th><th>Category</th>` +
    `<th class="num" id="cmp-th-a" style="color:${CMP_A_COLOR}">A</th>` +
    `<th class="num" id="cmp-th-b" style="color:${CMP_B_COLOR}">B</th>` +
    `<th class="num">Δ (A−B)</th><th style="min-width:140px">Delta</th></tr>`;
}

// ── Load + render ─────────────────────────────────────────────────────
async function loadCompare() {
  restoreTwoWayLayout();
  let dim = qs("cmp-dim").value;
  let a   = qs("cmp-a").value;
  let b   = qs("cmp-b").value;

  // Lot dimension: resolve to the specific run chosen on each side (no combining)
  if (dim === "lot") {
    dim = "run";
    a = qs("cmp-a-run").value;
    b = qs("cmp-b-run").value;
  }
  if (!a || !b) return;

  qs("cmp-th-a").textContent = a;
  qs("cmp-th-b").textContent = b;

  // For lot/run comparison, trend by wafer (each tests on one day); else by date
  const perWafer   = (dim === "run");
  const trendGroup = perWafer ? "wafer" : "date";
  const trendTitle = perWafer ? "Per-Wafer Yield — A vs B" : "Yield Trend — A vs B";
  const titleEl = document.querySelector("#chartCmpYield")
    ?.closest(".chart-card")?.querySelector(".chart-title");
  if (titleEl) titleEl.textContent = trendTitle;

  const [sumA, sumB, trendA, trendB, failA, failB] = await Promise.all([
    cmpFetch("/api/summary", dim, a),
    cmpFetch("/api/summary", dim, b),
    cmpFetch("/api/yield_trend", dim, a, {group_by: trendGroup}),
    cmpFetch("/api/yield_trend", dim, b, {group_by: trendGroup}),
    cmpFetch("/api/top_fail_tests", dim, a, {n:90}),
    cmpFetch("/api/top_fail_tests", dim, b, {n:90}),
  ]);

  renderCmpKPIs(sumA, sumB);
  renderCmpYield(trendA, trendB, a, b, dim);
  renderCmpFails(failA, failB, a, b);
}

function renderCmpKPIs(a, b) {
  const cards = [
    { label:"Yield %",       va:a.yield_pct, vb:b.yield_pct, d:1, better:"high", suffix:"%" },
    { label:"Fail Rate %",   va:+(100-a.yield_pct).toFixed(2), vb:+(100-b.yield_pct).toFixed(2), d:2, better:"low", suffix:"%" },
    { label:"Avg Test Time", va:a.avg_test_time_s, vb:b.avg_test_time_s, d:0, better:"low", suffix:"s" },
    { label:"Wafers",        va:a.wafers, vb:b.wafers, d:0, better:"none", suffix:"" },
  ];
  qs("cmp-kpis").innerHTML = cards.map(c => {
    const delta = c.va - c.vb;
    let cls = "cmp-delta-neutral", arrow = "";
    if (c.better !== "none" && Math.abs(delta) > 1e-9) {
      const aBetter = (c.better === "high") ? delta > 0 : delta < 0;
      cls = aBetter ? "cmp-delta-good" : "cmp-delta-bad";
      arrow = delta > 0 ? "▲" : "▼";
    }
    const deltaTxt = (delta>0?"+":"") + fmt(delta, c.d) + c.suffix;
    return `<div class="cmp-kpi-card">
      <div class="cmp-kpi-label">${c.label}</div>
      <div class="cmp-kpi-pair">
        <span class="cmp-kpi-a">${fmt(c.va, c.d)}${c.suffix}</span>
        <span style="color:var(--dim);font-size:11px">vs</span>
        <span class="cmp-kpi-b">${fmt(c.vb, c.d)}${c.suffix}</span>
      </div>
      <div class="cmp-kpi-delta ${cls}">Δ ${arrow} ${deltaTxt}</div>
    </div>`;
  }).join("");
}

function renderCmpYield(trendA, trendB, labelA, labelB, dim) {
  const allDates = [...new Set([...trendA.map(d=>d.label), ...trendB.map(d=>d.label)])].sort();
  const mapA = Object.fromEntries(trendA.map(d=>[d.label, d.yield_pct]));
  const mapB = Object.fromEntries(trendB.map(d=>[d.label, d.yield_pct]));

  destroyChart("chartCmpYield");
  charts.chartCmpYield = new Chart(qs("chartCmpYield").getContext("2d"), {
    type: "line",
    data: {
      labels: allDates,
      datasets: [
        { label:`A · ${labelA}`, data: allDates.map(d=>mapA[d] ?? null),
          borderColor: CMP_A_COLOR, backgroundColor:"transparent", borderWidth:2,
          pointRadius: allDates.length>40?0:2, tension:0.3, spanGaps:true },
        { label:`B · ${labelB}`, data: allDates.map(d=>mapB[d] ?? null),
          borderColor: CMP_B_COLOR, backgroundColor:"transparent", borderWidth:2,
          pointRadius: allDates.length>40?0:2, tension:0.3, spanGaps:true },
      ]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins: { legend:{labels:{color:"#94a3b8",font:{size:11},boxWidth:14}},
        tooltip:{callbacks:{label:c=>` ${c.dataset.label}: ${c.parsed.y?.toFixed(2)}%`}} },
      scales: {
        x:{ticks:{color:"#64748b",maxTicksLimit:18,font:{size:10}},grid:{color:"#1e2d45"}},
        y:{min:80,max:100,ticks:{color:"#64748b",font:{size:10},callback:v=>v+"%"},grid:{color:"#1e2d45"}},
      }
    }
  });
}

function renderCmpFails(failA, failB, labelA, labelB) {
  const mapA = Object.fromEntries(failA.map(d=>[d.name, d]));
  const mapB = Object.fromEntries(failB.map(d=>[d.name, d]));
  const names = [...new Set([...failA.map(d=>d.name), ...failB.map(d=>d.name)])];

  const rows = names.map(n => {
    const ra = mapA[n]?.fail_rate ?? 0;
    const rb = mapB[n]?.fail_rate ?? 0;
    return { name:n, category: mapA[n]?.category || mapB[n]?.category || "-",
             ra, rb, delta: +(ra - rb).toFixed(3) };
  }).sort((x,y) => Math.abs(y.delta) - Math.abs(x.delta));

  const top = rows.slice(0, 20);
  destroyChart("chartCmpFails");
  charts.chartCmpFails = new Chart(qs("chartCmpFails").getContext("2d"), {
    type: "bar",
    data: {
      labels: top.map(r=>r.name),
      datasets: [
        { label:`A · ${labelA}`, data: top.map(r=>r.ra), backgroundColor: CMP_A_COLOR, borderRadius:2 },
        { label:`B · ${labelB}`, data: top.map(r=>r.rb), backgroundColor: CMP_B_COLOR, borderRadius:2 },
      ]
    },
    options: {
      indexAxis:"y", responsive:true, maintainAspectRatio:false,
      plugins: { legend:{labels:{color:"#94a3b8",font:{size:11},boxWidth:14}},
        tooltip:{callbacks:{label:c=>` ${c.dataset.label}: ${c.parsed.x.toFixed(3)}%`}} },
      scales: {
        x:{ticks:{color:"#64748b",font:{size:10},callback:v=>v+"%"},grid:{color:"#1e2d45"}},
        y:{ticks:{color:"#94a3b8",font:{size:10}},grid:{display:false}},
      }
    }
  });

  const maxD = Math.max(...rows.map(r=>Math.abs(r.delta)), 0.001);
  qs("cmp-tbody").innerHTML = rows.map(r => {
    const dCls = r.delta > 0 ? "rate-high" : r.delta < 0 ? "rate-low" : "";
    const barW = (Math.abs(r.delta)/maxD*100).toFixed(1);
    const barColor = r.delta > 0 ? CMP_A_COLOR : CMP_B_COLOR;
    return `<tr>
      <td style="font-family:monospace;font-size:12px;white-space:nowrap">${r.name}</td>
      <td>${catBadge(r.category)}</td>
      <td class="num" style="color:${CMP_A_COLOR}">${fmt(r.ra,3)}%</td>
      <td class="num" style="color:${CMP_B_COLOR}">${fmt(r.rb,3)}%</td>
      <td class="num ${dCls}" style="font-weight:700">${r.delta>0?"+":""}${fmt(r.delta,3)}</td>
      <td><div class="bar-wrap"><div class="bar-track">
        <div class="bar-fill" style="width:${barW}%;background:${barColor}"></div>
      </div></div></td>
    </tr>`;
  }).join("");
}

// ══════════════════════════════════════════════════════════════════════
// ── Manual compare: Box A vs Box B (each box = one combined group) ────
// ══════════════════════════════════════════════════════════════════════

// Expand a box's tokens into a set of run_ids.
// A token can be a run_id (used directly) or a lot_id (all its runs added).
// Every run in a box is combined into that box's single group.
function resolveBox(elId) {
  const tokens = (qs(elId).value || "").split(/[\s,;]+/).map(s => s.trim()).filter(Boolean);
  const runSet = new Set(META.runs.map(r => r.run_id));
  const byLot  = {};
  META.runs.forEach(r => { (byLot[r.lot_id] = byLot[r.lot_id] || []).push(r.run_id); });

  const runIds = [], unknown = [];
  tokens.forEach(tok => {
    if (runSet.has(tok))      runIds.push(tok);                 // a run id
    else if (byLot[tok])      byLot[tok].forEach(r => runIds.push(r)); // a lot id -> its runs
    else                      unknown.push(tok);
  });
  return { runIds: [...new Set(runIds)], unknown, tokens };
}

// Fetch helper that sends a combined set of run_ids (runs=a,b,c) + date range
async function cmpFetchRuns(path, runIds, extra={}) {
  const p = new URLSearchParams();
  const df = qs("f-date-from")?.value, dt = qs("f-date-to")?.value;
  if (df) p.set("date_from", df);
  if (dt) p.set("date_to", dt);
  p.set("runs", runIds.join(","));
  Object.entries(extra).forEach(([k,v]) => p.set(k, String(v)));
  applyScope(p);
  return fetch(`${path}?${p}`).then(r => r.json());
}

async function runManualCompare() {
  const msg = qs("cmp-runlist-msg");
  const A   = resolveBox("cmp-runlist-a");
  const B   = resolveBox("cmp-runlist-b");

  if (!A.tokens.length && !B.tokens.length) { msg.textContent = ""; return; }

  if (!A.runIds.length || !B.runIds.length) {
    msg.innerHTML = `<span style="color:var(--red)">Enter at least one valid Run ID (or Lot ID) in each box.</span>`;
    return;
  }

  const unknown = [...new Set([...A.unknown, ...B.unknown])];
  const labelA  = A.runIds.length === 1 ? A.runIds[0] : `Box A (${A.runIds.length} runs combined)`;
  const labelB  = B.runIds.length === 1 ? B.runIds[0] : `Box B (${B.runIds.length} runs combined)`;
  msg.innerHTML = `A = ${A.runIds.length} run(s) combined · B = ${B.runIds.length} run(s) combined.` +
    (unknown.length ? ` <span style="color:var(--amber)">Skipped unknown: ${unknown.join(", ")}</span>` : "");

  // Each box is ONE combined group -> standard A vs B view
  restoreTwoWayLayout();
  qs("cmp-th-a").textContent = labelA;
  qs("cmp-th-b").textContent = labelB;

  const titleEl = document.querySelector("#chartCmpYield")
    ?.closest(".chart-card")?.querySelector(".chart-title");
  if (titleEl) titleEl.textContent = "Per-Wafer Yield — A vs B (combined)";

  const [sumA, sumB, trendA, trendB, failA, failB] = await Promise.all([
    cmpFetchRuns("/api/summary",        A.runIds),
    cmpFetchRuns("/api/summary",        B.runIds),
    cmpFetchRuns("/api/yield_trend",    A.runIds, {group_by:"wafer"}),
    cmpFetchRuns("/api/yield_trend",    B.runIds, {group_by:"wafer"}),
    cmpFetchRuns("/api/top_fail_tests", A.runIds, {n:90}),
    cmpFetchRuns("/api/top_fail_tests", B.runIds, {n:90}),
  ]);

  renderCmpKPIs(sumA, sumB);
  renderCmpYield(trendA, trendB, labelA, labelB, "run");
  renderCmpFails(failA, failB, labelA, labelB);
}

// ══════════════════════════════════════════════════════════════════════
// ── Multiple runs: one box, each run its own series (N-way) ───────────
// ══════════════════════════════════════════════════════════════════════
function tokenToRunIds(tok) {
  const runSet = new Set(META.runs.map(r => r.run_id));
  if (runSet.has(tok)) return [tok];                                   // a run id
  return META.runs.filter(r => r.lot_id === tok).map(r => r.run_id);  // a lot id -> its runs (else [])
}

async function runMultiCompare() {
  const msg    = qs("cmp-runmulti-msg");
  const tokens = (qs("cmp-runmulti").value || "").split(/[\s,;]+/).map(s => s.trim()).filter(Boolean);
  if (!tokens.length) { msg.textContent = ""; return; }

  const series = [], unknown = [], seen = new Set();
  tokens.forEach(tok => {
    if (seen.has(tok)) return;
    seen.add(tok);
    const runIds = tokenToRunIds(tok);
    if (runIds.length) series.push({ id: tok, runIds });
    else unknown.push(tok);
  });

  if (series.length < 2) {
    msg.innerHTML = `<span style="color:var(--red)">Enter at least 2 valid Run IDs.</span>` +
      (unknown.length ? ` Unknown: ${unknown.join(", ")}` : "");
    return;
  }
  series.forEach((s, i) => s.color = CMP_PALETTE[i % CMP_PALETTE.length]);
  msg.innerHTML = `Comparing ${series.length} runs.` +
    (unknown.length ? ` <span style="color:var(--amber)">Skipped unknown: ${unknown.join(", ")}</span>` : "");

  await Promise.all(series.map(async s => {
    const [summary, trend, fails] = await Promise.all([
      cmpFetchRuns("/api/summary",        s.runIds),
      cmpFetchRuns("/api/yield_trend",    s.runIds, {group_by:"wafer"}),
      cmpFetchRuns("/api/top_fail_tests", s.runIds, {n:90}),
    ]);
    s.summary = summary; s.trend = trend; s.fails = fails;
  }));

  const titleEl = document.querySelector("#chartCmpYield")
    ?.closest(".chart-card")?.querySelector(".chart-title");
  if (titleEl) titleEl.textContent = "Per-Wafer Yield — All Runs";

  renderMultiKPIs(series);
  renderMultiYield(series);
  renderMultiFails(series);
}

function renderMultiKPIs(series) {
  qs("cmp-kpis").style.gridTemplateColumns = `repeat(${Math.min(series.length, 4)}, 1fr)`;
  qs("cmp-kpis").innerHTML = series.map(s => {
    const d  = s.summary;
    const yc = d.yield_pct >= 95 ? "kpi-green" : d.yield_pct >= 90 ? "kpi-amber" : "kpi-red";
    return `<div class="cmp-kpi-card" style="border-top:3px solid ${s.color}">
      <div class="cmp-kpi-label" style="color:${s.color}">${s.id}</div>
      <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px">
        <span style="color:var(--sub)">Yield</span>
        <span class="${yc}" style="font-weight:800">${fmt(d.yield_pct)}%</span></div>
      <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px">
        <span style="color:var(--sub)">Fail rate</span>
        <span style="font-weight:700">${fmt(100 - d.yield_pct, 2)}%</span></div>
      <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px">
        <span style="color:var(--sub)">Avg time</span>
        <span style="font-weight:700">${fmt(d.avg_test_time_s,0)}s</span></div>
      <div style="display:flex;justify-content:space-between;font-size:12px">
        <span style="color:var(--sub)">Wafers</span>
        <span style="font-weight:700">${d.wafers}</span></div>
    </div>`;
  }).join("");
}

function renderMultiYield(series) {
  const allX = [...new Set(series.flatMap(s => s.trend.map(d => d.label)))].sort();
  destroyChart("chartCmpYield");
  charts.chartCmpYield = new Chart(qs("chartCmpYield").getContext("2d"), {
    type: "line",
    data: {
      labels: allX,
      datasets: series.map(s => {
        const m = Object.fromEntries(s.trend.map(d => [d.label, d.yield_pct]));
        return { label: s.id, data: allX.map(x => m[x] ?? null),
                 borderColor: s.color, backgroundColor:"transparent",
                 borderWidth:2, pointRadius: allX.length>40?0:2, tension:0.3, spanGaps:true };
      })
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins: { legend:{labels:{color:"#94a3b8",font:{size:11},boxWidth:14}},
        tooltip:{callbacks:{label:c=>` ${c.dataset.label}: ${c.parsed.y?.toFixed(2)}%`}} },
      scales: {
        x:{ticks:{color:"#64748b",maxTicksLimit:18,font:{size:10}},grid:{color:"#1e2d45"}},
        y:{min:80,max:100,ticks:{color:"#64748b",font:{size:10},callback:v=>v+"%"},grid:{color:"#1e2d45"}},
      }
    }
  });
}

function renderMultiFails(series) {
  const names = [...new Set(series.flatMap(s => s.fails.map(f => f.name)))];
  const maps  = series.map(s => Object.fromEntries(s.fails.map(f => [f.name, f])));
  const rows  = names.map(n => {
    const rates = maps.map(m => m[n]?.fail_rate ?? 0);
    const cat   = maps.map(m => m[n]?.category).find(Boolean) || "-";
    return { name:n, category:cat, rates, spread:+(Math.max(...rates) - Math.min(...rates)).toFixed(3) };
  }).sort((a,b) => b.spread - a.spread);

  const top = rows.slice(0, 15);
  destroyChart("chartCmpFails");
  charts.chartCmpFails = new Chart(qs("chartCmpFails").getContext("2d"), {
    type: "bar",
    data: {
      labels: top.map(r => r.name),
      datasets: series.map((s, i) => ({
        label: s.id, data: top.map(r => r.rates[i]),
        backgroundColor: s.color, borderRadius:2 }))
    },
    options: {
      indexAxis:"y", responsive:true, maintainAspectRatio:false,
      plugins: { legend:{labels:{color:"#94a3b8",font:{size:11},boxWidth:14}},
        tooltip:{callbacks:{label:c=>` ${c.dataset.label}: ${c.parsed.x.toFixed(3)}%`}} },
      scales: {
        x:{ticks:{color:"#64748b",font:{size:10},callback:v=>v+"%"},grid:{color:"#1e2d45"}},
        y:{ticks:{color:"#94a3b8",font:{size:10}},grid:{display:false}},
      }
    }
  });

  // Matrix table: test | run1 | run2 | ... | spread; highlight worst per row
  qs("cmp-table").querySelector("thead").innerHTML =
    `<tr><th>Test Name</th><th>Category</th>` +
    series.map(s => `<th class="num" style="color:${s.color}">${s.id.split("-").pop()}</th>`).join("") +
    `<th class="num">Spread</th></tr>`;

  qs("cmp-tbody").innerHTML = rows.map(r => {
    const worst = Math.max(...r.rates);
    const cells = r.rates.map(v => {
      const hot = (v === worst && r.spread > 0) ? "font-weight:800;color:var(--red)" : "";
      return `<td class="num" style="${hot}">${fmt(v,3)}%</td>`;
    }).join("");
    return `<tr>
      <td style="font-family:monospace;font-size:12px;white-space:nowrap">${r.name}</td>
      <td>${catBadge(r.category)}</td>
      ${cells}
      <td class="num" style="font-weight:700">${fmt(r.spread,3)}</td>
    </tr>`;
  }).join("");
}

// ── Kick off ──────────────────────────────────────────────────────────
init();

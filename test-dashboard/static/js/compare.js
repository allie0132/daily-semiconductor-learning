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
  setQuick("30d", false);
  onCmpDimChange();
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

  if (doRefresh) loadCompare();
}
function offsetDate(dateStr, days) {
  const d = new Date(dateStr); d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}
function onDateChange() {
  document.querySelectorAll(".date-btn").forEach(b => b.classList.remove("active"));
  loadCompare();
}

// ── Dimension + A/B selectors ─────────────────────────────────────────
function onCmpDimChange() {
  const dim  = qs("cmp-dim").value;
  const vals = DIM_VALUES[dim]();
  const aSel = qs("cmp-a"), bSel = qs("cmp-b");
  aSel.innerHTML = ""; bSel.innerHTML = "";
  vals.forEach(v => {
    aSel.appendChild(Object.assign(document.createElement("option"), {value:v.value, textContent:v.label}));
    bSel.appendChild(Object.assign(document.createElement("option"), {value:v.value, textContent:v.label}));
  });
  if (vals.length > 1) bSel.selectedIndex = 1;

  // For the Lot dimension, reveal a per-side Run picker so the user chooses
  // exactly which run of each lot to compare (runs are never combined).
  const isLot      = (dim === "lot");
  const isRunList  = (dim === "runlist");
  qs("grp-a-run").style.display = isLot ? "" : "none";
  qs("grp-b-run").style.display = isLot ? "" : "none";
  if (isLot) { fillRunPicker("a"); fillRunPicker("b"); }

  // Manual multi-run mode: hide the A/B selectors, show the text input
  qs("grp-runlist").style.display = isRunList ? "" : "none";
  qs("cmp-a").closest(".filter-group").style.display = isRunList ? "none" : "";
  qs("cmp-b").closest(".filter-group").style.display = isRunList ? "none" : "";
  document.querySelector(".cmp-vs").style.display    = isRunList ? "none" : "";

  if (isRunList) runManualCompare();   // render with whatever is already typed
  else           loadCompare();
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

// Params = date range + chosen dimension override
function cmpParams(dim, value, extra={}) {
  const p = new URLSearchParams();
  const df = qs("f-date-from")?.value;
  const dt = qs("f-date-to")?.value;
  if (df) p.set("date_from", df);
  if (dt) p.set("date_to", dt);
  p.set(dim, value);
  Object.entries(extra).forEach(([k,v]) => p.set(k, String(v)));
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
// ── Manual N-way comparison (paste multiple Run IDs) ──────────────────
// ══════════════════════════════════════════════════════════════════════
async function runManualCompare() {
  const raw  = qs("cmp-runlist").value || "";
  const ids  = raw.split(/[\s,;]+/).map(s => s.trim()).filter(Boolean);
  const msg  = qs("cmp-runlist-msg");

  if (!ids.length) { msg.textContent = "Enter at least two Run IDs to compare."; return; }

  const known   = new Set(META.runs.map(r => r.run_id));
  const valid   = ids.filter(id => known.has(id));
  const unknown = ids.filter(id => !known.has(id));
  const uniq    = [...new Set(valid)];

  if (uniq.length < 2) {
    msg.innerHTML = `<span style="color:var(--red)">Need at least 2 valid Run IDs.</span>` +
      (unknown.length ? ` Unknown: ${unknown.join(", ")}` : "");
    return;
  }
  msg.innerHTML = `Comparing ${uniq.length} runs.` +
    (unknown.length ? ` <span style="color:var(--amber)">Skipped unknown: ${unknown.join(", ")}</span>` : "");

  const series = uniq.map((id, i) => ({ id, color: CMP_PALETTE[i % CMP_PALETTE.length] }));

  // fetch summary, per-wafer trend, and fail tests for each run in parallel
  await Promise.all(series.map(async s => {
    const [summary, trend, fails] = await Promise.all([
      cmpFetch("/api/summary",         "run", s.id),
      cmpFetch("/api/yield_trend",     "run", s.id, {group_by:"wafer"}),
      cmpFetch("/api/top_fail_tests",  "run", s.id, {n:90}),
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
  // one card per run: yield / fail% / avg time / wafers
  qs("cmp-kpis").style.gridTemplateColumns =
    `repeat(${Math.min(series.length, 4)}, 1fr)`;
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
  // union of test names, ranked by spread (max-min fail rate across runs)
  const names = [...new Set(series.flatMap(s => s.fails.map(f => f.name)))];
  const maps  = series.map(s => Object.fromEntries(s.fails.map(f => [f.name, f])));
  const rows  = names.map(n => {
    const rates = maps.map(m => m[n]?.fail_rate ?? 0);
    const cat   = maps.map(m => m[n]?.category).find(Boolean) || "-";
    return { name:n, category:cat, rates, spread:+(Math.max(...rates) - Math.min(...rates)).toFixed(3) };
  }).sort((a,b) => b.spread - a.spread);

  // Chart: top 15 by spread, grouped bars
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
  const thead = `<tr><th>Test Name</th><th>Category</th>` +
    series.map(s => `<th class="num" style="color:${s.color}">${s.id.split("-").pop()}</th>`).join("") +
    `<th class="num">Spread</th></tr>`;
  qs("cmp-table").querySelector("thead").innerHTML = thead;

  qs("cmp-tbody").innerHTML = rows.map(r => {
    const worst = Math.max(...r.rates);
    const cells = r.rates.map((v,i) => {
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

/* ── ATE Dashboard — Compare (A vs B) page ── */
"use strict";

let META   = null;
let charts = {};
const CMP_A_COLOR = "#3b82f6";
const CMP_B_COLOR = "#f59e0b";

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

const DIM_VALUES = {
  tp_rev:         () => META.tp_revs,
  tester:         () => META.testers,
  socket:         () => META.sockets,
  product:        () => META.products,
  product_family: () => META.families,
  proc_node:      () => META.proc_nodes,
  test_step:      () => META.test_steps,
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
    aSel.appendChild(Object.assign(document.createElement("option"), {value:v, textContent:v}));
    bSel.appendChild(Object.assign(document.createElement("option"), {value:v, textContent:v}));
  });
  if (vals.length > 1) bSel.selectedIndex = 1;
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

// ── Load + render ─────────────────────────────────────────────────────
async function loadCompare() {
  const dim = qs("cmp-dim").value;
  const a   = qs("cmp-a").value;
  const b   = qs("cmp-b").value;
  if (!a || !b) return;

  qs("cmp-th-a").textContent = a;
  qs("cmp-th-b").textContent = b;

  const [sumA, sumB, trendA, trendB, failA, failB] = await Promise.all([
    cmpFetch("/api/summary", dim, a),
    cmpFetch("/api/summary", dim, b),
    cmpFetch("/api/yield_trend", dim, a, {group_by:"date"}),
    cmpFetch("/api/yield_trend", dim, b, {group_by:"date"}),
    cmpFetch("/api/top_fail_tests", dim, a, {n:90}),
    cmpFetch("/api/top_fail_tests", dim, b, {n:90}),
  ]);

  renderCmpKPIs(sumA, sumB);
  renderCmpYield(trendA, trendB, a, b);
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

function renderCmpYield(trendA, trendB, labelA, labelB) {
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

// ── Kick off ──────────────────────────────────────────────────────────
init();

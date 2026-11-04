/* ── ATE Production Test Dashboard ── */
"use strict";

// ── State ────────────────────────────────────────────────────────────
let META       = null;
let charts     = {};
let activeTab  = "overview";

// ── Helpers ──────────────────────────────────────────────────────────
function qs(id) { return document.getElementById(id); }

function filterParams() {
  const p = new URLSearchParams();
  ["product","tp_rev","test_step","proc_node","tester","socket"].forEach(k => {
    const v = qs(`f-${k}`)?.value;
    if (v && v !== "ALL") p.set(k, v);
  });
  const df = qs("f-date-from")?.value;
  const dt = qs("f-date-to")?.value;
  if (df) p.set("date_from", df);
  if (dt) p.set("date_to",   dt);
  return p;
}

async function api(path, extra={}) {
  const p = filterParams();
  Object.entries(extra).forEach(([k, v]) => p.set(k, String(v)));
  const res = await fetch(`${path}?${p}`);
  return res.json();
}

function fmt(n, d=1) { return (n==null) ? "—" : Number(n).toFixed(d); }
function fmtK(n) {
  if (n >= 1e6) return (n/1e6).toFixed(1)+"M";
  if (n >= 1e3) return (n/1e3).toFixed(1)+"K";
  return String(n);
}

const CAT_CLASS = {
  "DC": "cat-DC", "IDDQ": "cat-IDDQ", "AC": "cat-AC", "Timing": "cat-TIME",
  "Memory": "cat-MEM", "Scan": "cat-SCAN", "Functional": "cat-FUNC",
  "Data Eye": "cat-EYE", "Assembly": "cat-ASM", "Open/Short": "cat-OPEN",
  "Contact": "cat-OPEN",
  "HBM-TSV": "cat-HBM", "HBM-PHY": "cat-HBM", "HBM-Eye": "cat-HBM",
  "HBM-MBiST": "cat-HBM", "HBM-ECC": "cat-HBM",
};
function catBadge(cat) {
  const cls = CAT_CLASS[cat] || "cat-DC";
  return `<span class="cat ${cls}">${cat}</span>`;
}

function binColor(bin) {
  const map = {
    BIN1:"#10b981", BIN1B:"#06b6d4", BIN1C:"#f59e0b",
    BIN2:"#f97316", BIN3:"#eab308", BIN4:"#ef4444",
    BIN5:"#dc2626", BIN6:"#ec4899", BIN7:"#8b5cf6",
    BIN8:"#6366f1", BIN9:"#a16207", BIN10:"#67e8f9",
    BIN11:"#7f1d1d", EDGE:"#1e2d45",
  };
  return map[bin] || "#64748b";
}

function rateClass(r) {
  if (r >= 5) return "rate-high";
  if (r >= 2) return "rate-med";
  return "rate-low";
}

function destroyChart(id) {
  if (charts[id]) { charts[id].destroy(); delete charts[id]; }
}

// ── Init ─────────────────────────────────────────────────────────────
async function init() {
  META = await fetch("/api/meta").then(r => r.json());
  populateSelects();
  setQuick("30d", false);
  await refresh();
}

function populateSelects() {
  const fill = (id, arr) => {
    const sel = qs(id);
    arr.forEach(v => sel.appendChild(Object.assign(document.createElement("option"), {value:v, textContent:v})));
  };
  fill("f-product",   META.products);
  fill("f-tp_rev",    META.tp_revs);
  fill("f-test_step", META.test_steps);
  fill("f-proc_node", META.proc_nodes);
  fill("f-tester",    META.testers);
  fill("f-socket",    META.sockets);

  // Wafer map lot selector
  const lotSel = qs("wmap-lot");
  META.lots.forEach(l => {
    const opt = document.createElement("option");
    opt.value = l.lot_id;
    opt.textContent = `${l.lot_id} · ${l.product} · ${l.start_date}`;
    lotSel.appendChild(opt);
  });
}

// ── Date quick-select ─────────────────────────────────────────────────
function setQuick(mode, doRefresh=true) {
  document.querySelectorAll(".date-btn").forEach(b => b.classList.remove("active"));
  event?.target?.classList.add("active");

  const today = META ? META.date_max : new Date().toISOString().slice(0,10);
  const from  = qs("f-date-from");
  const to    = qs("f-date-to");
  to.value   = today;

  if (mode === "today") {
    from.value = today;
  } else if (mode === "7d") {
    from.value = offsetDate(today, -7);
  } else if (mode === "30d") {
    from.value = offsetDate(today, -30);
  } else if (mode === "90d") {
    from.value = META ? META.date_min : offsetDate(today, -90);
  } else {  // all
    from.value = META ? META.date_min : "";
    to.value   = META ? META.date_max : "";
  }
  if (doRefresh) refresh();
}

function offsetDate(dateStr, days) {
  const d = new Date(dateStr);
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

function onDateChange() {
  document.querySelectorAll(".date-btn").forEach(b => b.classList.remove("active"));
  refresh();
}

function applyFilters() { refresh(); }

// ── Refresh all data ──────────────────────────────────────────────────
async function refresh() {
  loadKPIs();
  if (activeTab === "overview")  { loadYieldTrend(); loadBinDist(); loadLotTable(); }
  if (activeTab === "fails")     loadFailTests();
  if (activeTab === "time")      loadTimeTests();
  if (activeTab === "wafer")     { /* lot selector driven */ }
}

// ── Tab switching ─────────────────────────────────────────────────────
function switchTab(tab) {
  activeTab = tab;
  document.querySelectorAll(".tab").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".pane").forEach(el => el.classList.remove("active"));
  qs(`tab-${tab}`).classList.add("active");
  qs(`pane-${tab}`).classList.add("active");

  if (tab === "overview")  { loadYieldTrend(); loadBinDist(); loadLotTable(); }
  if (tab === "fails")     loadFailTests();
  if (tab === "time")      loadTimeTests();
  if (tab === "wafer")     initWaferTab();
}

// ── KPI Cards ────────────────────────────────────────────────────────
async function loadKPIs() {
  const d = await api("/api/summary");
  qs("kpi-yield").textContent    = fmt(d.yield_pct) + "%";
  qs("kpi-yield-sub").textContent = `pass rate`;
  qs("kpi-lots").textContent     = d.lots;
  qs("kpi-lots-sub").textContent = `${d.wafers} wafers`;
  qs("kpi-dies").textContent     = fmtK(d.total_dies);
  qs("kpi-dies-sub").textContent = `${fmtK(d.pass_dies)} pass`;
  qs("kpi-fails").textContent    = fmtK(d.fail_dies);
  qs("kpi-fails-sub").textContent = fmt(100 - d.yield_pct) + "% fail rate";
  qs("kpi-time").textContent     = fmt(d.avg_test_time_s, 0);

  // Color yield by health
  const el = qs("kpi-yield");
  el.className = "kpi-value " + (d.yield_pct >= 95 ? "kpi-green" : d.yield_pct >= 90 ? "kpi-amber" : "kpi-red");
}

// ── Yield Trend ───────────────────────────────────────────────────────
async function loadYieldTrend() {
  const group = qs("trend-group").value;
  const data  = await api("/api/yield_trend", {group_by: group});
  const labels = data.map(d => d.label);
  const vals   = data.map(d => d.yield_pct);

  destroyChart("chartYield");
  const ctx = qs("chartYield").getContext("2d");
  charts.chartYield = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: "Yield %",
        data: vals,
        borderColor: "#3b82f6",
        backgroundColor: "rgba(59,130,246,0.08)",
        borderWidth: 2,
        pointRadius: labels.length > 50 ? 0 : 3,
        pointHoverRadius: 5,
        tension: 0.3,
        fill: true,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.y.toFixed(2)}%` } } },
      scales: {
        x: { ticks: { color: "#64748b", maxTicksLimit: 20, maxRotation: 45,
                       font: { size: 10 } }, grid: { color: "#1e2d45" } },
        y: { min: 80, max: 100, ticks: { color: "#64748b", font: { size: 10 },
              callback: v => v + "%" }, grid: { color: "#1e2d45" } },
      }
    }
  });
}

// ── Bin Distribution ──────────────────────────────────────────────────
async function loadBinDist() {
  const data = await api("/api/bin_summary");
  const BIN_ORDER = ["BIN1","BIN1B","BIN1C","BIN2","BIN3","BIN4","BIN5",
                     "BIN6","BIN7","BIN8","BIN9","BIN10","BIN11"];
  const entries = BIN_ORDER.filter(b => data[b] && data[b].count > 0)
                            .map(b => ({ bin: b, ...data[b] }));
  const total   = entries.reduce((s, e) => s + e.count, 0);

  destroyChart("chartBins");
  const ctx = qs("chartBins").getContext("2d");
  charts.chartBins = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: entries.map(e => e.label),
      datasets: [{ data: entries.map(e => e.count),
                   backgroundColor: entries.map(e => e.color),
                   borderWidth: 1, borderColor: "#0a0e1a" }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: "65%",
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: {
          label: ctx => ` ${ctx.label}: ${fmtK(ctx.raw)} (${(ctx.raw/total*100).toFixed(1)}%)`
        }}
      }
    }
  });

  // Legend
  const legend = qs("bin-legend");
  legend.innerHTML = entries.map(e => `
    <div class="bin-dist-row">
      <div class="bin-swatch" style="background:${e.color}"></div>
      <span class="bin-label">${e.label}</span>
      <span class="bin-count">${fmtK(e.count)}</span>
      <span class="bin-pct">${(e.count/total*100).toFixed(1)}%</span>
    </div>`).join("");
}

// ── Lot Table ────────────────────────────────────────────────────────
async function loadLotTable() {
  const lots = await api("/api/lots");
  qs("lot-count").textContent = `${lots.length} lots`;
  const tbody = qs("lot-tbody");
  tbody.innerHTML = lots.map(l => {
    const yc = l.yield_pct >= 95 ? "kpi-green" : l.yield_pct >= 90 ? "kpi-amber" : "kpi-red";
    return `<tr>
      <td style="font-family:monospace;font-size:12px">${l.lot_id}</td>
      <td>${l.product}</td>
      <td>${l.tp_rev}</td>
      <td>${l.test_step}</td>
      <td>${l.proc_node}</td>
      <td class="num ${yc}" style="font-weight:700">${fmt(l.yield_pct)}%</td>
      <td style="color:var(--dim)">${l.start_date}</td>
    </tr>`;
  }).join("");
}

// ── Fail Tests ───────────────────────────────────────────────────────
async function loadFailTests() {
  const data  = await api("/api/top_fail_tests", {n: 30});
  const maxFc = data[0]?.fail_count || 1;
  renderBarChart("chartFails", data,
    d => d.fail_count,
    d => binColor(d.bin),
    "Fail Count");
  qs("fail-tbody").innerHTML = data.map((d, i) => `
    <tr>
      <td class="rank">${i+1}</td>
      <td style="font-family:monospace;font-size:12px;white-space:nowrap">${d.name}</td>
      <td>${catBadge(d.category)}</td>
      <td><span style="display:inline-block;width:10px;height:10px;border-radius:2px;
                       background:${binColor(d.bin)};vertical-align:middle;margin-right:4px"></span>${d.bin}</td>
      <td class="num" style="font-weight:700">${fmtK(d.fail_count)}</td>
      <td class="num ${rateClass(d.fail_rate)}">${fmt(d.fail_rate, 3)}%</td>
      <td class="num">${fmt(d.avg_time_ms, 1)}</td>
      <td>
        <div class="bar-wrap">
          <div class="bar-track">
            <div class="bar-fill" style="width:${(d.fail_count/maxFc*100).toFixed(1)}%;
                 background:${binColor(d.bin)}"></div>
          </div>
        </div>
      </td>
    </tr>`).join("");
}

// ── Test Time ─────────────────────────────────────────────────────────
async function loadTimeTests() {
  const data   = await api("/api/top_time_tests", {n: 30});
  const maxTm  = data[0]?.avg_time_ms || 1;
  renderBarChart("chartTime", data,
    d => d.avg_time_ms,
    d => binColor(d.bin),
    "Avg Time (ms)");
  qs("time-tbody").innerHTML = data.map((d, i) => `
    <tr>
      <td class="rank">${i+1}</td>
      <td style="font-family:monospace;font-size:12px;white-space:nowrap">${d.name}</td>
      <td>${catBadge(d.category)}</td>
      <td><span style="display:inline-block;width:10px;height:10px;border-radius:2px;
                       background:${binColor(d.bin)};vertical-align:middle;margin-right:4px"></span>${d.bin}</td>
      <td class="num" style="font-weight:700">${fmt(d.avg_time_ms, 1)}</td>
      <td class="num ${rateClass(d.fail_rate)}">${fmt(d.fail_rate, 3)}%</td>
      <td>
        <div class="bar-wrap">
          <div class="bar-track">
            <div class="bar-fill" style="width:${(d.avg_time_ms/maxTm*100).toFixed(1)}%;
                 background:${binColor(d.bin)}"></div>
          </div>
        </div>
      </td>
    </tr>`).join("");
}

// ── Generic Horizontal Bar Chart ──────────────────────────────────────
function renderBarChart(canvasId, data, valFn, colorFn, label) {
  destroyChart(canvasId);
  const ctx = qs(canvasId).getContext("2d");
  charts[canvasId] = new Chart(ctx, {
    type: "bar",
    data: {
      labels: data.map(d => d.name),
      datasets: [{
        label,
        data: data.map(valFn),
        backgroundColor: data.map(colorFn),
        borderWidth: 0,
        borderRadius: 3,
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.x.toFixed(1)}` }}
      },
      scales: {
        x: { ticks: { color: "#64748b", font:{size:10} }, grid: { color: "#1e2d45" } },
        y: { ticks: { color: "#94a3b8", font:{size:10.5} }, grid: { display: false } },
      }
    }
  });
}

// ── Wafer Map ─────────────────────────────────────────────────────────
function initWaferTab() {
  if (qs("wmap-lot").options.length > 0) loadWaferList();
}

async function loadWaferList() {
  const lot  = qs("wmap-lot").value;
  const data = await fetch(`/api/wafers_in_lot?lot=${lot}`).then(r=>r.json());
  const sel  = qs("wmap-wafer");
  sel.innerHTML = "";
  data.forEach(w => {
    sel.appendChild(Object.assign(document.createElement("option"), {value:w, textContent:w}));
  });
  loadWaferMap();
}

async function loadWaferMap() {
  const lot   = qs("wmap-lot").value;
  const wafer = qs("wmap-wafer").value;
  if (!lot || !wafer) return;

  const d = await fetch(`/api/wafer_map?lot=${lot}&wafer=${wafer}`).then(r=>r.json());
  if (d.error) return;

  drawWafer(d);
  updateWaferStats(d);
}

function drawWafer(data) {
  const canvas = qs("waferCanvas");
  const ctx    = canvas.getContext("2d");
  const size   = canvas.width;
  const GRID   = data.grid_size;
  const cell   = size / GRID;
  const GAP    = 1;
  ctx.clearRect(0, 0, size, size);

  // Background
  ctx.fillStyle = "#0a0e1a";
  ctx.fillRect(0, 0, size, size);

  // Die outline color map
  const BIN_COLOR = {
    BIN1:"#10b981", BIN1B:"#06b6d4", BIN1C:"#f59e0b",
    BIN2:"#f97316", BIN3:"#eab308", BIN4:"#ef4444",
    BIN5:"#dc2626", BIN6:"#ec4899", BIN7:"#8b5cf6",
    BIN8:"#6366f1", BIN9:"#a16207", BIN10:"#67e8f9",
    BIN11:"#450a0a", EDGE:"#111827",
  };
  const BIN_FILL = {
    ...BIN_COLOR,
    BIN11: "#7f1d1d", EDGE: "#0d1627",
  };

  data.dies.forEach(die => {
    const x = die.x * cell + GAP/2;
    const y = die.y * cell + GAP/2;
    const w = cell - GAP;
    ctx.fillStyle   = BIN_FILL[die.bin] || "#1e2d45";
    ctx.strokeStyle = "rgba(0,0,0,0.3)";
    ctx.lineWidth   = 0.5;
    ctx.beginPath();
    ctx.rect(x, y, w, w);
    ctx.fill();
    ctx.stroke();
  });

  // Wafer outline circle
  const cx = size / 2, cy = size / 2, r = size / 2 - 2;
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, Math.PI*2);
  ctx.strokeStyle = "#2d3f5c";
  ctx.lineWidth   = 2;
  ctx.stroke();

  // Store for tooltip
  canvas._mapData  = data;
  canvas._cellSize = cell;
}

// ── Wafer tooltip ─────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  const canvas  = qs("waferCanvas");
  const tooltip = qs("tooltip");

  canvas.addEventListener("mousemove", e => {
    if (!canvas._mapData) return;
    const rect = canvas.getBoundingClientRect();
    const cell = canvas._cellSize;
    const mx   = e.clientX - rect.left;
    const my   = e.clientY - rect.top;
    const gx   = Math.floor(mx / cell);
    const gy   = Math.floor(my / cell);

    const die  = canvas._mapData.dies.find(d => d.x === gx && d.y === gy);
    if (!die) { tooltip.style.display = "none"; return; }

    const BIN_LABELS = {
      BIN1:"Grade A Pass", BIN1B:"Grade B Downgrade", BIN1C:"Grade C Downgrade",
      BIN2:"Open/Short",   BIN3:"Contact", BIN4:"DC Parametric",
      BIN5:"IDDQ/Leakage", BIN6:"AC/Timing Fail", BIN7:"Memory",
      BIN8:"Scan/ATPG",    BIN9:"Functional", BIN10:"Data Eye/SI",
      BIN11:"Assembly/Crack", EDGE:"Not Tested",
    };

    let html = `<div class="tt-tick">Die (${die.x}, ${die.y})</div>`;
    html += `<div>Bin: ${die.bin} — ${BIN_LABELS[die.bin] || die.bin}</div>`;
    if (die.status === "FAIL") {
      html += `<div class="tt-fail">Fail: ${die.fail_test || "?"}</div>`;
    } else if (die.status === "DOWNGRADE") {
      html += `<div style="color:#06b6d4">Downgrade via: ${die.fail_test || "?"}</div>`;
      html += `<div style="color:#64748b;font-size:10px">Passed at lower speed</div>`;
    } else if (die.status === "PASS") {
      html += `<div class="tt-pass">Pass (Grade A)</div>`;
    }

    tooltip.innerHTML = html;
    tooltip.style.display = "block";
    tooltip.style.left = (e.clientX + 12) + "px";
    tooltip.style.top  = (e.clientY + 12) + "px";
  });
  canvas.addEventListener("mouseleave", () => { qs("tooltip").style.display = "none"; });
});

function updateWaferStats(d) {
  qs("wm-yield").textContent = fmt(d.grade_a_pct) + "%";
  qs("wm-grb").textContent   = fmt(d.grade_b_pct) + "%";
  qs("wm-grc").textContent   = fmt(d.grade_c_pct) + "%";
  const failPct = d.fail_count / (d.pass_count + d.downgrade_count + d.fail_count + d.edge_count) * 100;
  qs("wm-fail").textContent  = fmt(failPct) + "%";

  // Top fail tests
  const failDiv = qs("wm-top-fails");
  if (d.top_fail_tests.length) {
    failDiv.innerHTML = d.top_fail_tests.map(t =>
      `<div class="top-fail-row">
         <span class="top-fail-name">${t.name}</span>
         <span class="top-fail-cnt">${t.count}</span>
       </div>`
    ).join("");
  } else {
    failDiv.innerHTML = '<span class="empty-msg">No fail dies</span>';
  }

  // Top downgrade tests
  const downDiv = qs("wm-top-down");
  if (d.top_downgrade_tests?.length) {
    downDiv.innerHTML = d.top_downgrade_tests.map(t =>
      `<div class="top-fail-row">
         <span class="top-fail-name">${t.name}</span>
         <span style="color:#06b6d4;font-weight:700;min-width:30px;text-align:right">${t.count}</span>
       </div>`
    ).join("");
  } else {
    downDiv.innerHTML = '<span class="empty-msg">No downgrades</span>';
  }

  // Bin counts
  const binsDiv = qs("wm-bins");
  const BIN_ORDER = ["BIN1","BIN1B","BIN1C","BIN2","BIN3","BIN4","BIN5",
                     "BIN6","BIN7","BIN8","BIN9","BIN10","BIN11"];
  const BIN_LABELS = {
    BIN1:"Grade A",    BIN1B:"Grade B ↓", BIN1C:"Grade C ↓",
    BIN2:"Open/Short", BIN3:"Contact",    BIN4:"DC Para",
    BIN5:"IDDQ",       BIN6:"AC/Timing",  BIN7:"Memory",
    BIN8:"Scan",       BIN9:"Functional", BIN10:"Data Eye",
    BIN11:"Assembly",
  };
  binsDiv.innerHTML = BIN_ORDER.filter(b => d.bin_counts[b])
    .map(b => `
      <div class="bin-dist-row">
        <div class="bin-swatch" style="background:${binColor(b)}"></div>
        <span class="bin-label">${BIN_LABELS[b] || b}</span>
        <span class="bin-count">${d.bin_counts[b]}</span>
      </div>`).join("");

  // Legend
  const legend = qs("wmap-legend");
  legend.innerHTML = BIN_ORDER.filter(b => d.bin_counts[b]).map(b => `
    <div class="legend-item">
      <div class="legend-dot" style="background:${binColor(b)}"></div>
      ${BIN_LABELS[b] || b}
    </div>`).join("");
}

// ── Kick off ──────────────────────────────────────────────────────────
init();

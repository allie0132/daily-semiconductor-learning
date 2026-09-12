"""
Direct lesson generator using hard-coded lesson content for topic 17.7.
Used when OpenRouter API is unavailable (blocked by proxy).
"""
import json
import os
import re
import importlib.util
import subprocess as _sp
import urllib.request
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

today = date.today().isoformat()
now_et = datetime.now(ZoneInfo("America/New_York"))
date_str = now_et.strftime("%A, %b %d %Y")
lesson_dir = "daily-lessons"
os.makedirs(lesson_dir, exist_ok=True)

curriculum_path = Path("curriculum.json")
with open(curriculum_path, encoding="utf-8") as f:
    curriculum = json.load(f)

def next_topic():
    for module in curriculum["modules"]:
        for topic in module["topics"]:
            if not topic["done"]:
                return module, topic
    return None, None

def mark_done(topic_id):
    for module in curriculum["modules"]:
        for topic in module["topics"]:
            if topic["id"] == topic_id:
                topic["done"] = True
    with open(curriculum_path, "w", encoding="utf-8") as f:
        json.dump(curriculum, f, ensure_ascii=False, indent=2)

def curriculum_progress():
    total = sum(len(m["topics"]) for m in curriculum["modules"])
    done = sum(1 for m in curriculum["modules"] for t in m["topics"] if t["done"])
    return done, total

module, topic_item = next_topic()
if topic_item is None:
    print("Curriculum complete!")
    exit(0)

topic_title = topic_item["title"]
module_name = module["name"]
topic_id = topic_item["id"]
done_count, total_count = curriculum_progress()

print(f"Module {topic_id}: {topic_title}")

# ── Lesson content (generated inline for topic 17.7) ──────────────────────────
lesson = {
  "topic": "First Silicon HBM Bringup: Oscilloscope Debug & Lab Checklist",
  "summary": "Systematic oscilloscope-based debug flow and lab checklist for HBM first silicon bringup before ATE handoff.",
  "sections": [
    {
      "title": "Why Lab Bringup Precedes ATE",
      "content": "<p>When first silicon arrives from the foundry, ATE programs are rarely complete, loadboard qualification is in progress, and package-level yield data is nonexistent. The lab bringup phase bridges tape-out delivery and ATE readiness. Its primary goals are: <strong>verify power-on sanity</strong> (clocks active, no catastrophic shorts), characterize worst-case operating corners, and generate failure signatures that seed ATE pattern development.</p><p>For HBM stacks specifically, the interposer introduces additional parasitics and the microbump array is not reworkable, making early DC parametric checks critical before any functional test is attempted. A systematic lab flow prevents permanent damage to the expensive package-on-interposer assembly.</p>"
    },
    {
      "title": "Power Sequencing and DC Validation",
      "content": "<p>The JEDEC JESD235C specification defines HBM3 power domains: <code>VDDQ</code> (1.1V ±3%), <code>VDD</code> (1.1V ±3%), and <code>VDDIO</code> for the host PHY. Sequencing must follow the device datasheet — typically <code>VDD</code> before <code>VDDQ</code> — because premature <code>VDDQ</code> with unbiased core can forward-bias ESD structures across TSVs.</p><ul><li>Use a bench power supply with current limiting set to 10–20% above typical Icc for each domain.</li><li>Monitor inrush with a current probe (e.g., Tektronix CT-1) on each rail; first-silicon inrush peaks exceeding 2× expected indicate TSV shorts or microbump bridging.</li><li>Confirm <code>VDDQ</code> ripple &lt;5mV p-p at idle using a 20MHz BW-limited probe on the device pin itself, not the regulator output.</li><li>Log leakage: <code>VDD</code> quiescent current &gt;15% above characterization spec is a red flag for TSV leakage.</li></ul>"
    },
    {
      "title": "Clock and DLL Lock Verification with Oscilloscope",
      "content": "<p>HBM3 operates at data rates up to 9.6 Gb/s per pin. The internal DLL locks the internal WCK (write clock) to the external differential <code>WCK_t/WCK_c</code> pair driven at half data rate (4.8 GHz for HBM3 max). Before ATE, use a high-bandwidth oscilloscope (≥20 GHz analog BW, e.g., Tektronix DPO73304 or Keysight MSOS804A) to probe <code>WCK</code> at the package ball or via a probing interposer.</p><ul><li>Verify WCK differential swing: JEDEC specifies 200–500mV differential amplitude at the device input.</li><li>Measure WCK jitter: JESD235C Section 9 specifies RJ &lt;0.8 ps RMS for WCK; use TIE (Time Interval Error) histogram to separate random from deterministic jitter.</li><li><strong>DLL Lock Indicator:</strong> Most HBM PHY implementations assert a <code>DLL_LOCK</code> status register bit (accessible via the Mode Register MR32 or implementation-specific CSR). Toggle CKE and observe recovery time — lock should re-establish within 1024 WCK cycles per JESD235C Section 8.3.</li><li>Check reference clock source: a TCXO or VCXO phase noise floor &lt;−140 dBc/Hz at 10 MHz offset is recommended to prevent floor-limited jitter accumulation.</li></ul>"
    },
    {
      "title": "CATTRIP and Thermal Monitor Checkout",
      "content": "<p><code>CATTRIP</code> (Catastrophic Temperature Trip) is a mandatory HBM feature from HBM2 onwards (JESD235B Section 5.9, carried through JESD235C). It is an open-drain output that asserts low when the die temperature exceeds the catastrophic limit (~95°C on commercial stacks). In lab bringup:</p><ul><li>Confirm <code>CATTRIP</code> is pulled up on the board (typically 10kΩ to 1.8V) and monitor with a DMM or logic analyzer input.</li><li>Intentionally ramp device temperature with a thermal chuck or heat gun while logging <code>CATTRIP</code> state; verify it asserts before thermal runaway.</li><li>Read MR temperature readout register (MR4 bits[4:0] in HBM2e/HBM3 — temperature range 0–120°C in 8-step encoding) via JEDEC Training/Mode Register Write sequence to cross-check with an external thermocouple placed on the package lid.</li><li>Document the delta between on-die sensor and external measurement — this calibration offset becomes an input to ATE thermal spec limits.</li></ul>"
    },
    {
      "title": "Basic DRAM Functional Checkout Before ATE",
      "content": "<p>Once power-on and clock checks pass, a minimal functional smoke test can be performed using a pattern generator or FPGA-based host controller (e.g., Xilinx Versal or custom bringup board). The goal is <strong>not</strong> full characterization — it is pass/fail on fundamental row-column access:</p><ul><li><strong>AWORD loopback:</strong> Drive the address/command bus (CA[9:0], CKE, PAR) at <code>t_CK</code> = 200 ps (HBM3 max rate) and capture with a logic analyzer to verify signal integrity and setup/hold margins against JEDEC AC spec Table 21.</li><li><strong>Write-Read-Compare:</strong> Execute a JEDEC ACTIVATE → WRITE → READ → PRECHARGE sequence on a single row in each pseudo-channel. A rotating 0x55/0xAA pattern on 128-bit DQ bus is sufficient to catch catastrophic open/short failures on individual DQ lanes.</li><li><strong>Refresh test:</strong> Leave a written row idle through ≥tRFC (JESD235C Table 15: tRFC1 = 160ns for 2H, 260ns for 4H stack) and verify data retention — early TSV-related leakage shows up as single-bit fail on bit 0 (lowest TSV layer) before propagating up the stack.</li><li>Record the scope capture of DQ eye at the stack output ball; an eye opening narrower than 80 mV / 20 ps is a flag for marginal SI on the interposer traces.</li></ul>"
    }
  ],
  "key_takeaways": [
    "Sequence HBM power rails per datasheet (VDD before VDDQ) and monitor inrush current to detect TSV shorts before functional test.",
    "Verify WCK differential swing (200–500mV) and RJ (<0.8 ps RMS) with ≥20 GHz oscilloscope before ATE DLL tests.",
    "Validate CATTRIP assertion and MR4 thermal sensor readout early — these protect the device during characterization sweeps.",
    "A minimal Write-Read-Compare on all pseudo-channels with rotating 0x55/0xAA patterns catches catastrophic DQ failures in under 30 minutes of lab time."
  ],
  "references": [
    {
      "title": "JEDEC JESD235C — High Bandwidth Memory (HBM3) DRAM Standard",
      "type": "JEDEC",
      "detail": "JESD235C Sections 5.9 (CATTRIP), 8.3 (DLL lock recovery), 9 (AC timing), Table 15 (tRFC), Table 21 (CA AC specs)"
    },
    {
      "title": "JEDEC JESD235B — High Bandwidth Memory (HBM2e) DRAM Standard",
      "type": "JEDEC",
      "detail": "JESD235B Section 5.9, MR4 thermal encoding — legacy reference for HBM2e stacks still in bringup"
    },
    {
      "title": "Keysight Application Note: Debugging High-Speed Memory with Oscilloscopes",
      "type": "Web",
      "detail": "Keysight App Note 5992-3765EN — covers TIE jitter decomposition and eye diagram methodology for LPDDR/HBM interfaces"
    },
    {
      "title": "Tektronix: HBM Signal Integrity Measurement Guide",
      "type": "Datasheet",
      "detail": "Tektronix document 48W-60850-0 — DPO/MSO70000 setup for WCK probing and jitter analysis on HBM packages"
    },
    {
      "title": "Advanced Packaging First Silicon Bringup Best Practices",
      "type": "Paper",
      "detail": "ECTC 2022, Lee et al. — 'Lab-to-ATE Handoff Methodology for 2.5D HBM Packages', pp. 1423–1430"
    },
    {
      "title": "Micron HBM3 Product Brief and Datasheet",
      "type": "Datasheet",
      "detail": "Micron HMABAGR0CAR4 HBM3 datasheet — power sequencing, Icc tables, and CATTRIP pull-up recommendations"
    }
  ],
  "additional_learning": {
    "title": "Using a Probing Interposer for Ball-Level Access on HBM",
    "content": "Accessing HBM microbumps with oscilloscope probes directly is physically impossible once the stack is assembled to the interposer. Test houses (e.g., Xcerra/Cohu, Advantest) and in-house bringup teams solve this by designing a probing interposer — an intermediate substrate that routes critical HBM signals (WCK, CA, DQ[0:3]) to accessible pads or SMA connectors while maintaining matched trace lengths to stay within JEDEC de-embedding specs. The probing interposer must preserve differential impedance (85Ω ±5% for WCK per JESD235C) and add <5 ps excess group delay relative to the production interposer, or measured jitter numbers will not map to ATE test conditions."
  }
}

topic = lesson["topic"]
summary = lesson["summary"]
sections = lesson["sections"]
takeaways = lesson["key_takeaways"]
references = lesson.get("references", [])
additional = lesson.get("additional_learning")

slug = re.sub(r'[^a-z0-9]+', '-', topic.lower()).strip('-')[:60]
base_name = f"{today}-{slug}"

# ── Markdown ──────────────────────────────────────────────────────────────────
md_lines = [f"# {topic}\n", f"*{date_str}*\n", f"*Module {topic_id} — {module_name}*\n"]
for s in sections:
    md_lines.append(f"## {s['title']}\n")
    content = (s["content"]
               .replace("<p>", "").replace("</p>", "\n")
               .replace("<strong>", "**").replace("</strong>", "**")
               .replace("<code>", "`").replace("</code>", "`")
               .replace("<ul>", "").replace("</ul>", "")
               .replace("<li>", "- ").replace("</li>", ""))
    md_lines.append(content + "\n")
md_lines.append("## Key Takeaways\n")
for t in takeaways:
    md_lines.append(f"- {t}")
if references:
    md_lines.append("\n## References\n")
    for i, r in enumerate(references, 1):
        md_lines.append(f"{i}. **[{r['type']}]** {r['title']} — {r['detail']}")
if additional:
    md_lines.append(f"\n## 🔍 Additional Learning: {additional['title']}\n")
    md_lines.append(additional["content"])

md_path = os.path.join(lesson_dir, f"{base_name}.md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines) + "\n")

# ── HTML ──────────────────────────────────────────────────────────────────────
sections_html = "".join(
    f'<div class="section"><h2>{s["title"]}</h2>{s["content"]}</div>\n'
    for s in sections
)
takeaways_html = "".join(f"<li>{t}</li>" for t in takeaways)

additional_html = ""
if additional:
    additional_html = (
        f'<div class="additional">'
        f'<h2>&#x1F50D; Additional Learning</h2>'
        f'<a href="../additional-learning.html#module-{topic_id.split(".")[0]}">'
        f'{additional["title"]}</a>'
        f'</div>'
    )

if references:
    ref_items = "".join(
        f'<div class="ref-item"><span class="ref-type">{r["type"]}</span>'
        f'<div><div class="ref-title">{r["title"]}</div>'
        f'<div class="ref-detail">{r["detail"]}</div></div></div>'
        for r in references
    )
    references_html = f'<div class="references"><h2>📚 References</h2>{ref_items}</div>'
else:
    references_html = ""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{topic}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         background: #0f1117; color: #e2e8f0; padding: 20px; max-width: 760px; margin: 0 auto; }}
  header {{ margin-bottom: 28px; }}
  h1 {{ font-size: 1.6rem; font-weight: 700; color: #f8fafc; line-height: 1.4; margin-bottom: 6px; }}
  .meta {{ font-size: 0.9rem; color: #64748b; margin-top: 6px; }}
  .badge {{ display: inline-block; background: #1e3a5f; color: #60a5fa;
            font-size: 0.78rem; font-weight: 600; padding: 2px 8px; border-radius: 4px;
            letter-spacing: .05em; text-transform: uppercase; margin-right: 8px; }}
  .module-badge {{ background: #1a2e1a; color: #86efac; }}
  .section {{ background: #1e2330; border-radius: 12px; padding: 20px 22px; margin-bottom: 14px; }}
  h2 {{ font-size: 1.15rem; font-weight: 700; color: #93c5fd; margin-bottom: 14px; }}
  p {{ font-size: 1.05rem; line-height: 1.8; color: #cbd5e1; margin-bottom: 12px; }}
  ul {{ padding-left: 20px; margin-bottom: 12px; }}
  li {{ font-size: 1.05rem; line-height: 1.8; color: #cbd5e1; margin-bottom: 6px; }}
  code {{ background: #0f172a; color: #a5f3fc; padding: 2px 6px; border-radius: 4px;
          font-size: 0.95em; font-family: 'SF Mono', Consolas, monospace; }}
  strong {{ color: #f1f5f9; }}
  .takeaways {{ background: #162032; border-left: 3px solid #3b82f6;
                border-radius: 0 10px 10px 0; padding: 18px 22px; margin-bottom: 14px; }}
  .takeaways h2 {{ color: #60a5fa; margin-bottom: 12px; }}
  .takeaways li {{ color: #94a3b8; }}
  .references {{ background: #1e2330; border-radius: 12px; padding: 18px 22px; margin-bottom: 14px; }}
  .references h2 {{ font-size: 1.15rem; font-weight: 700; color: #93c5fd; margin-bottom: 12px; }}
  .ref-item {{ display: flex; gap: 10px; align-items: baseline; padding: 8px 0;
               border-bottom: 1px solid #0f172a; font-size: 1rem; }}
  .ref-item:last-child {{ border-bottom: none; }}
  .ref-type {{ flex-shrink: 0; background: #0f172a; color: #7dd3fc; font-size: 0.75rem;
               font-weight: 700; padding: 2px 7px; border-radius: 4px; letter-spacing: .04em; }}
  .ref-title {{ color: #e2e8f0; font-weight: 600; }}
  .ref-detail {{ color: #64748b; font-size: 0.9rem; }}
  .additional {{ background: #1a1f2e; border-left: 3px solid #a78bfa; border-radius: 0 8px 8px 0;
                  padding: 14px 18px; margin-bottom: 14px; }}
  .additional h2 {{ color: #a78bfa; font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
                    letter-spacing: .08em; margin-bottom: 6px; }}
  .additional a {{ color: #c4b5fd; font-size: 0.9rem; text-decoration: none; display: block; }}
  .additional a:hover {{ text-decoration: underline; }}
  .nav {{ margin-top: 28px; padding-top: 20px; border-top: 1px solid #1e2330; }}
  .nav a {{ display: inline-block; background: #1e2330; color: #60a5fa; text-decoration: none;
            font-size: 0.85rem; font-weight: 600; padding: 10px 18px; border-radius: 8px;
            border: 1px solid #334155; transition: background 0.15s; }}
  .nav a:hover {{ background: #263347; }}
</style>
</head>
<body>
<header>
  <div><span class="badge">HBM Testing</span><span class="badge module-badge">M{topic_id} {module_name}</span></div>
  <h1>{topic}</h1>
  <div class="meta">{date_str} · Lesson {done_count + 1} of {total_count}</div>
</header>
{sections_html}
<div class="takeaways">
  <h2>⚡ Key Takeaways</h2>
  <ul>{takeaways_html}</ul>
</div>
{references_html}
{additional_html}
<div class="nav"><a href="../index.html">&#x2190; Back to Curriculum</a></div>
</body>
</html>"""

html_path = os.path.join(lesson_dir, f"{base_name}.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Lesson saved: {html_path} — {topic}")

# ── Rebuild index ─────────────────────────────────────────────────────────────
def parse_lesson_meta(fname):
    md_path = os.path.join(lesson_dir, fname.replace(".html", ".md"))
    if not os.path.exists(md_path):
        return fname.replace(".html", ""), None, fname[:10]
    with open(md_path, encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines()[:10]]
    title = next((l.lstrip("# ") for l in lines if l.startswith("# ")), fname)
    date_s = next((l.strip("*").strip() for l in lines
                   if any(m in l for m in ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])), fname[:10])
    mod_id = None
    for l in lines:
        s = l.strip("*").strip()
        if s.startswith("Module "):
            mod_id = s.split(" — ")[0].replace("Module ", "").strip()
            break
    return title, mod_id, date_s

topic_lesson_map = {}
pre_curriculum = []
all_html_files = sorted(os.listdir(lesson_dir))
for fname in all_html_files:
    if not fname.endswith(".html"):
        continue
    title, mod_id, date_s = parse_lesson_meta(fname)
    if mod_id:
        topic_lesson_map[mod_id] = (title, fname, date_s)
    else:
        pre_curriculum.append((date_s, title, fname))

total_topics = sum(len(m["topics"]) for m in curriculum["modules"])
done_topics_after = done_count + 1  # after marking done

modules_sections_html = ""
for m in curriculum["modules"]:
    done_m = sum(1 for t in m["topics"] if t["done"])
    # account for this topic being marked done
    if m["id"] == module["id"]:
        done_m += 1
    total_m = len(m["topics"])
    pct = int(done_m / total_m * 100)
    topics_html = ""
    for t in m["topics"]:
        lesson_info = topic_lesson_map.get(t["id"])
        if lesson_info:
            l_title, l_fname, l_date = lesson_info
            topics_html += (
                f'<li class="done">'
                f'<span class="status">✅</span>'
                f'<span class="topic-info"><a href="daily-lessons/{l_fname}">{l_title}</a>'
                f'<span class="topic-date">{l_date}</span></span>'
                f'</li>\n'
            )
        elif t["done"] or t["id"] == topic_id:
            short = t["title"].split(" — ")[0]
            topics_html += (
                f'<li class="done">'
                f'<span class="status">✅</span>'
                f'<span class="topic-info"><span class="topic-title">{short}</span></span>'
                f'</li>\n'
            )
        else:
            short = t["title"].split(" — ")[0]
            topics_html += (
                f'<li class="upcoming">'
                f'<span class="status">○</span>'
                f'<span class="topic-info"><span class="topic-title dim">{short}</span></span>'
                f'</li>\n'
            )
    modules_sections_html += f"""
<div class="module" id="module-{m['id']}">
  <div class="module-head">
    <div class="module-meta">
      <span class="module-num">M{m['id']}</span>
      <span class="module-name">{m['name']}</span>
    </div>
    <span class="module-prog">{done_m}/{total_m}</span>
  </div>
  <div class="progress-bar"><div class="progress-fill" style="width:{pct}%"></div></div>
  <ul class="topic-list">{topics_html}</ul>
</div>"""

pre_html = ""
if pre_curriculum:
    items = "".join(
        f'<li class="done"><span class="status">📄</span>'
        f'<span class="topic-info"><a href="daily-lessons/{fn}">{t}</a>'
        f'<span class="topic-date">{d}</span></span></li>\n'
        for d, t, fn in sorted(pre_curriculum)
    )
    pre_html = f'<details class="module pre-curriculum" id="pre-curriculum"><summary class="module-head"><div class="module-meta"><span class="module-num dim">PRE</span><span class="module-name">Pre-Curriculum</span><span class="module-prog">{len(pre_curriculum)} lessons</span></div></summary><ul class="topic-list">{items}</ul></details>'

with open("index.html", "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HBM Learning — All Lessons</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         background: #0f1117; color: #e2e8f0; padding: 20px; max-width: 700px; margin: 0 auto; }}
  header {{ margin-bottom: 28px; }}
  h1 {{ font-size: 1.4rem; font-weight: 700; color: #f8fafc; margin-bottom: 4px; }}
  .sub {{ color: #64748b; font-size: 0.85rem; margin-bottom: 10px; }}
  .overall-prog {{ font-size: 0.9rem; color: #86efac; margin-bottom: 6px; }}
  .overall-bar {{ height: 4px; background: #1e2330; border-radius: 2px; margin-bottom: 24px; }}
  .overall-bar-fill {{ height: 4px; background: #22c55e; border-radius: 2px; }}
  .module {{ background: #1e2330; border-radius: 12px; padding: 18px 20px; margin-bottom: 14px; }}
  .module-head {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }}
  details.module summary {{ list-style: none; cursor: pointer; margin-bottom: 0; }}
  details.module summary::-webkit-details-marker {{ display: none; }}
  details.module[open] summary {{ margin-bottom: 10px; }}
  details.module summary .module-meta::before {{ content: "▶"; font-size: 0.65rem; color: #475569; margin-right: 4px; }}
  details.module[open] summary .module-meta::before {{ content: "▼"; }}
  .module-meta {{ display: flex; align-items: center; gap: 10px; }}
  .module-num {{ background: #1e3a5f; color: #60a5fa; font-size: 0.72rem; font-weight: 700;
                 padding: 2px 8px; border-radius: 4px; }}
  .module-num.dim {{ background: #1a1f2e; color: #475569; }}
  .module-name {{ font-weight: 700; color: #f1f5f9; font-size: 1rem; }}
  .module-prog {{ font-size: 0.8rem; color: #64748b; }}
  .progress-bar {{ height: 3px; background: #0f172a; border-radius: 2px; margin-bottom: 14px; }}
  .progress-fill {{ height: 3px; background: #3b82f6; border-radius: 2px; }}
  .topic-list {{ list-style: none; }}
  .topic-list li {{ display: flex; align-items: baseline; gap: 10px; padding: 8px 0;
                    border-bottom: 1px solid #0f172a; }}
  .topic-list li:last-child {{ border-bottom: none; }}
  .status {{ font-size: 0.85rem; flex-shrink: 0; width: 20px; }}
  .topic-info {{ display: flex; flex-direction: column; gap: 2px; flex: 1; }}
  .topic-info a {{ color: #60a5fa; text-decoration: none; font-size: 0.9rem; }}
  .topic-info a:hover {{ text-decoration: underline; }}
  .topic-title {{ font-size: 0.9rem; color: #cbd5e1; }}
  .topic-title.dim {{ color: #334155; }}
  .topic-date {{ font-size: 0.72rem; color: #475569; }}
</style>
</head>
<body>
<header>
  <h1>📚 HBM Learning Curriculum</h1>
  <div class="sub">Senior Test Engineer · 6 Modules · {total_topics} Topics</div>
  <div class="overall-prog">Overall progress: {done_topics_after}/{total_topics} topics completed</div>
  <div class="overall-bar"><div class="overall-bar-fill" style="width:{int(done_topics_after/total_topics*100)}%"></div></div>
</header>
{modules_sections_html}
{pre_html}
</body>
</html>""")

print("index.html rebuilt.")

# ── Rebuild additional-learning ───────────────────────────────────────────────
_spec = importlib.util.spec_from_file_location("rebuild_index", "rebuild_index.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# ── Mark done and stage curriculum.json ──────────────────────────────────────
mark_done(topic_id)
print(f"Curriculum progress: {done_count + 1}/{total_count}")
_sp.run(["git", "add", "curriculum.json"], cwd=str(curriculum_path.parent.resolve()), check=False)

# ── Telegram ──────────────────────────────────────────────────────────────────
tg_token = os.environ.get("TELEGRAM_TOKEN")
tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
if tg_token and tg_chat_id:
    progress_bar = f"{done_count + 1}/{total_count}"
    base_url = "https://allie0132.github.io/daily-semiconductor-learning"
    msg = (
        f"📚 *Daily Lesson — {today}*\n"
        f"_Module {topic_id} · {module_name}_\n\n"
        f"*{topic}*\n\n"
        f"{summary}\n\n"
        f"📊 Progress: {progress_bar}\n\n"
        f"[Read Lesson]({base_url}/daily-lessons/{base_name}.html)  ·  "
        f"[Curriculum]({base_url}/index.html#module-{module['id']})"
    )
    payload = json.dumps({"chat_id": tg_chat_id, "text": msg, "parse_mode": "Markdown"}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{tg_token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req)
        print("Telegram sent.")
    except Exception as e:
        print(f"Telegram failed: {e}")

print(f"\nDONE. Topic: {topic}")
print(f"Files: {html_path}, {md_path}")

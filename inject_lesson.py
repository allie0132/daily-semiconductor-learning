"""
Generates today's lesson for topic 3.6 using inline content (no external API),
then runs the rest of the generate_lesson.py pipeline.
"""
import json, os, re, subprocess
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import importlib.util, sys

today = date.today().isoformat()
now_et = datetime.now(ZoneInfo("America/New_York"))
date_str = now_et.strftime("%A, %b %d %Y")
lesson_dir = "daily-lessons"
os.makedirs(lesson_dir, exist_ok=True)

# ── Curriculum ────────────────────────────────────────────────────────────────
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
    done  = sum(1 for m in curriculum["modules"] for t in m["topics"] if t["done"])
    return done, total

module, topic_item = next_topic()
if topic_item is None:
    print("Curriculum complete!")
    sys.exit(0)

topic_title  = topic_item["title"]
module_name  = module["name"]
topic_id     = topic_item["id"]
done_count, total_count = curriculum_progress()
print(f"Module {topic_id}: {topic_title}")

# ── Inline lesson content ─────────────────────────────────────────────────────
lesson = {
  "topic": "HBM Mode Registers & Configuration Testing: MR0-MR15",
  "summary": "Systematic testing of HBM MR0-MR15 via MRS write and MRR readback, covering boundary values, reserved bits, and JESD235C compliance verification.",
  "sections": [
    {
      "title": "Mode Register Architecture and Access Protocol",
      "content": "<p>HBM mode registers (MRs) are accessed via the <strong>Mode Register Set (MRS)</strong> command on the command/address (CA) bus. In HBM3 (JESD235C), the MRS command drives a 3-bit register address on CA[2:0] and an 8-bit data payload on CA[10:3], targeting a specific pseudo-channel. The <strong>Mode Register Read (MRR)</strong> command returns the current register value on the DQ bus during the subsequent read latency window.</p><p>Registers MR0-MR15 are individually addressable. HBM3 uses <strong>per-channel</strong> mode registers - each of the 8 channels (16 pseudo-channels) maintains an independent MR state, requiring full coverage testing across all pseudo-channels. The MRS command must comply with <strong>tMRD</strong> (minimum 4 nCK between successive MRS commands) to prevent register metastability.</p><ul><li>MRS command takes effect after tMRD (4 nCK in HBM3)</li><li>MRR data appears on DQ after tMRR read latency offset</li><li>All MRS/MRR must occur with <strong>CKE HIGH</strong> and device in idle state</li></ul>"
    },
    {
      "title": "MR0-MR5: Core Timing, Latency, and Data Path Configuration",
      "content": "<p><strong>MR0</strong> is the most critical register, controlling <strong>Burst Length (BL)</strong> and <strong>CAS Latency (CL)</strong>. In HBM3, BL is fixed at 4 (MR0[1:0]=00), and CL is encoded in MR0[5:2] with valid values from CL=6 to CL=17 depending on operating frequency. An incorrect CL setting causes systematic read failures - commonly seen as a fixed-offset alignment error in captured eye diagrams.</p><p><strong>MR1</strong> configures <strong>Write Latency (WL)</strong> and <strong>Additive Latency (AL)</strong>. WL must match the PHY write-path delay; mismatches appear as DQS-to-DQ alignment errors in ATE timing closure reports. <strong>MR2</strong> and <strong>MR3</strong> control read/write preamble and postamble lengths - critical for eye margin at data rates above 3.2 Gbps/pin.</p><ul><li><strong>MR4</strong>: DBI-WR enable (bit 3) and DBI-RD enable (bit 2) - Data Bus Inversion reduces simultaneous switching noise</li><li><strong>MR5</strong>: ODT impedance settings - affects signal integrity margin testing</li></ul>"
    },
    {
      "title": "MR6-MR10: ECC, Temperature Sensor, and RAS Feature Control",
      "content": "<p><strong>MR8</strong> is the ECC control register in HBM3. Bit 0 enables/disables SECDED ECC; bit 1 enables the <strong>ECC error log</strong>, which accumulates correctable error counts accessible via MRR. Test strategy: write MR8[0]=1, inject single-bit errors via deliberate data inversion during write, then verify ECC correction via MRR readback of error log registers MR14 and MR15.</p><p><strong>MR6</strong> holds the temperature sensor output in read-only mode - MRR of MR6 returns the on-die thermal sensor reading with 1 degree C LSB resolution. Cross-correlate against chuck temperature at ATE: a deviation greater than 5 degrees C flags a sensor calibration failure. <strong>MR7</strong> controls CATTRIP threshold programming in applicable HBM implementations - writing above the thermal limit triggers CATTRIP pin assertion, which ATE must capture as a forced test interrupt.</p><ul><li><strong>MR9</strong>: Refresh rate control (1x, 2x, 4x) - test at all three settings to verify tREFI compliance</li><li><strong>MR10</strong>: CRC enable - enables per-burst CRC on the read data path per JESD235C Section 6.3</li></ul>"
    },
    {
      "title": "MR11-MR15: HBM3 Extensions, Error Logs, and Reserved Fields",
      "content": "<p><strong>MR14 and MR15</strong> are read-only <strong>ECC error log registers</strong> in HBM3. MR14[7:0] reports correctable (single-bit) error counts; MR15[7:0] reports uncorrectable (double-bit) detection events. After each DRAM stress pattern, MRR of MR14/MR15 validates error injection and ECC hardware function. Error log counters are <strong>sticky</strong> - they persist across refresh cycles until explicitly cleared via MR8[3]=1.</p><p><strong>Reserved bit testing</strong> is a JEDEC compliance requirement: JESD235C mandates that RFU-labeled bits must return 0 on MRR regardless of what was written via MRS. ATE patterns must write 0xFF to registers containing reserved fields, then perform MRR and mask-compare against the defined bit pattern. Any non-zero return on an RFU bit is a compliance failure.</p><ul><li>MR11-MR13: Vendor-specific or HBM3e-extended features (PHY training status, vendor ID)</li><li>Boundary-value testing: write 0x00 and 0xFF to each MR; verify defined bits behave per spec</li></ul>"
    },
    {
      "title": "ATE Mode Register Test Implementation and Coverage Strategy",
      "content": "<p>A complete MR test suite on Advantest V93000 or Teradyne UltraFLEX requires three layers: <strong>(1) Walk test</strong> - write each valid value to each MR and verify via MRR, covering all defined bits. <strong>(2) Interaction test</strong> - stress timing interactions with CL+WL combinations near min/max valid pairs. <strong>(3) Retention test</strong> - verify MR values survive a self-refresh entry/exit cycle (tPD hold) unchanged.</p><p>MRR data is captured as a <strong>functional read</strong> on ATE - the DQ return is compared against expected bit patterns using per-bit expect (PBE) masks. A critical pitfall: MRR data appears on DQ at the CAS Latency offset from the MRR command, so ATE strobe timing must align to the CL programmed in MR0. Misaligned strobe captures are the #1 debug failure mode during first-silicon MR test bring-up.</p><ul><li>Test all 16 pseudo-channels independently - channel-to-channel MR isolation is a common RTL bug</li><li>Verify <strong>reset-state</strong>: after power-on-reset or ZQCal init, all MRs must match JEDEC-defined reset values</li><li>Automate MR sweep via parametric loops in the ATE test program; avoid hardcoded single-value tests</li></ul>"
    }
  ],
  "key_takeaways": [
    "MR0 (CAS Latency, Burst Length) and MR1 (Write Latency) are the highest-impact registers - incorrect values cause systematic functional failures that mimic electrical defects",
    "Reserved/RFU bits must return 0 on MRR regardless of MRS write value; any non-zero RFU readback is a JEDEC JESD235C compliance failure",
    "ECC control (MR8) and error log (MR14/MR15) testing requires deliberate error injection to validate end-to-end SECDED hardware function",
    "All 16 pseudo-channels must be tested independently for MR state isolation - shared register state bugs are common in first-silicon HBM controller integration",
    "ATE MRR capture requires strobe alignment to the CL programmed in MR0; strobe timing mismatch is the #1 bring-up failure mode for mode register testing"
  ],
  "references": [
    {
      "title": "High Bandwidth Memory (HBM) DRAM - JESD235C",
      "type": "JEDEC",
      "detail": "JEDEC Standard JESD235C, Section 4 (Mode Registers), Table 4-1 through Table 4-15; Section 6.3 (CRC)"
    },
    {
      "title": "HBM2 Standard - JESD235A Mode Register Definitions",
      "type": "JEDEC",
      "detail": "JEDEC JESD235A, Section 4.4 - MR0-MR8 definitions and power-on reset values"
    },
    {
      "title": "SK Hynix HBM3 HBMC Series Datasheet",
      "type": "Datasheet",
      "detail": "Mode Register Map section; MRS/MRR timing diagrams; tMRD specification (Rev 1.0)"
    },
    {
      "title": "Micron HBM2e Mode Register Programming Technical Note TN-HBM-01",
      "type": "Datasheet",
      "detail": "Programming sequences, boundary conditions, and ATE implementation guidance for MR0-MR10"
    },
    {
      "title": "Advantest V93000 HBM Test Library Application Note AN-V93K-HBM-003",
      "type": "Web",
      "detail": "MRR capture alignment, PBE mask programming, and pseudo-channel parallel MR sweep patterns"
    },
    {
      "title": "JEDEC JESD79-4B DDR4 Specification",
      "type": "JEDEC",
      "detail": "Section 3.5 - MRS/MRR protocol heritage shared with HBM command bus; cross-reference for tMRD timing"
    }
  ],
  "additional_learning": {
    "title": "HBM3e MR Extensions: New Registers in JESD235D",
    "content": "HBM3e (JESD235D) adds new mode register definitions extending coverage beyond JESD235C, including enhanced refresh management registers and per-channel RFM (Refresh Management) control bits. HBM3e also expands PHY training status readback registers (MR11-MR13) to expose per-pseudo-channel read/write DQ training results, enabling ATE to diagnose marginal PHY calibration without oscilloscope captures. Test engineers targeting HBM3e must update MR test suites to include these extended registers and validate that HBM3 legacy mode correctly masks or ignores HBM3e-exclusive MR fields."
  }
}

# ── Everything below mirrors generate_lesson.py ───────────────────────────────
topic     = lesson["topic"]
summary   = lesson["summary"]
sections  = lesson["sections"]
takeaways = lesson["key_takeaways"]
references= lesson.get("references", [])
additional= lesson.get("additional_learning")

slug      = re.sub(r'[^a-z0-9]+', '-', topic.lower()).strip('-')[:60]
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
    md_lines.append(f"\n## \U0001f50d Additional Learning: {additional['title']}\n")
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

print(f"Lesson saved: {html_path}")

# ── Rebuild index ─────────────────────────────────────────────────────────────
def parse_lesson_meta(fname):
    md_path = os.path.join(lesson_dir, fname.replace(".html", ".md"))
    if not os.path.exists(md_path):
        return fname.replace(".html", ""), None, fname[:10]
    with open(md_path, encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines()[:10]]
    title  = next((l.lstrip("# ") for l in lines if l.startswith("# ")), fname)
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
pre_curriculum   = []
for fname in sorted(os.listdir(lesson_dir)):
    if not fname.endswith(".html"):
        continue
    title, mod_id, date_s = parse_lesson_meta(fname)
    if mod_id:
        topic_lesson_map[mod_id] = (title, fname, date_s)
    else:
        pre_curriculum.append((date_s, title, fname))

total_topics = sum(len(m["topics"]) for m in curriculum["modules"])
done_topics  = sum(1 for m in curriculum["modules"] for t in m["topics"] if t["done"])

modules_sections_html = ""
for m in curriculum["modules"]:
    done_m  = sum(1 for t in m["topics"] if t["done"])
    total_m = len(m["topics"])
    pct     = int(done_m / total_m * 100)
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
        elif t["done"]:
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
  <div class="overall-prog">Overall progress: {done_topics}/{total_topics} topics completed</div>
  <div class="overall-bar"><div class="overall-bar-fill" style="width:{int(done_topics/total_topics*100)}%"></div></div>
</header>
{modules_sections_html}
{pre_html}
</body>
</html>""")

# ── Rebuild full index via rebuild_index.py ───────────────────────────────────
_spec = importlib.util.spec_from_file_location("rebuild_index", "rebuild_index.py")
_mod  = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

print(f"Index rebuilt.")

# ── Mark curriculum done ──────────────────────────────────────────────────────
mark_done(topic_id)
done_count_new, _ = curriculum_progress()
print(f"Curriculum progress: {done_count_new}/{total_count}")
import subprocess as _sp
_sp.run(["git", "add", "curriculum.json"], cwd=str(curriculum_path.parent.resolve()), check=False)

# ── Telegram ──────────────────────────────────────────────────────────────────
import urllib.request
tg_token   = os.environ.get("TELEGRAM_TOKEN")
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

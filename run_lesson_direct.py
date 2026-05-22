"""
Bypass script: injects pre-generated lesson JSON and runs the rest of
generate_lesson.py's file-writing, index-rebuild, and Telegram logic.
"""
import json, os, re, subprocess
import urllib.request
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

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

# ── Pre-generated lesson (Claude-authored, no external API needed) ────────────
lesson = {
  "topic": "HBM Timing Basics: tRCD, tCL, tRP & Bandwidth",
  "summary": "Master HBM's core DRAM timing parameters and the bandwidth math that drives GPU and HPC memory subsystem decisions.",
  "sections": [
    {
      "title": "HBM Timing Architecture Overview",
      "content": (
        "<p>HBM uses a standard DDR-based DRAM core organized into pseudo-channels (PCs), "
        "each 64 bits wide. Timing parameters control the sequencing of ACTIVATE, READ/WRITE, "
        "and PRECHARGE commands within each bank. JESD235C (HBM2E) and JESD238 (HBM3) define "
        "the minimum timing intervals in nanoseconds; the controller converts these to clock "
        "cycles based on the operating frequency.</p>"
        "<p>Three parameters dominate access latency: <strong>tRCD</strong> (row-to-column delay), "
        "<strong>tCL</strong> (CAS latency / read latency), and <strong>tRP</strong> (row precharge "
        "time). Together they set the worst-case open-page read latency: "
        "<code>t_total = tRCD + tCL + tRP</code> — the cost of opening a new row, reading, and "
        "closing it.</p>"
      )
    },
    {
      "title": "tRCD — Row-to-Column Delay",
      "content": (
        "<p><strong>tRCD</strong> is the minimum interval between an ACTIVATE command and a "
        "subsequent READ or WRITE to the same bank. Physically it is the time for the sense "
        "amplifiers to latch and amplify the selected row's bitline voltage to a stable logic "
        "level. Issuing a column command before tRCD expires catches the sense amps mid-swing "
        "and reads corrupted data.</p>"
        "<ul>"
        "<li>HBM2E (JESD235C): tRCD = 14–18 ns depending on speed grade (e.g., 14 ns at 3.2 Gbps)</li>"
        "<li>HBM3 (JESD238A): tRCD typically 15–18 ns; exact value in MRS register set</li>"
        "<li>On ATE (e.g., Advantest T2000 / Teradyne UltraFLEX): tRCD is swept during timing "
        "characterisation by shrinking the ACT→CAS delay until first-fail; guard-band is "
        "typically 0.5–1 ns from hard-fail boundary</li>"
        "<li>A tRCD failure manifests as data errors only on the first access to a freshly "
        "activated row — subsequent accesses to the same open row are unaffected</li>"
        "</ul>"
      )
    },
    {
      "title": "tCL — CAS Latency (Read Latency)",
      "content": (
        "<p><strong>tCL</strong> (called <em>Read Latency, RL</em> in HBM nomenclature) is the "
        "number of clock cycles from the rising edge of a READ command to the first DQ data "
        "burst appearing on the interface. It is a pipeline latency — the DRAM core is already "
        "open; tCL is the column decode, sense-amp output, and IO driver pipeline depth.</p>"
        "<ul>"
        "<li>HBM2E at 1 GHz (2 Gbps): RL = 7 ck (7 ns); at 1.6 GHz (3.2 Gbps): RL = 14 ck (8.75 ns)</li>"
        "<li>HBM3 at 3.2 GHz (6.4 Gbps): RL programmed 15–20 ck via MRS7/MRS8 per JESD238 Table 11</li>"
        "<li>Write Latency (WL) = RL − differential; HBM2E WL = RL/2 rounded to even integer</li>"
        "<li>On ATE, CL is validated by confirming DQ data-valid window aligns with expected "
        "strobe (RDQS) position; mis-programmed RL causes a fixed offset failure across all DQs</li>"
        "</ul>"
        "<p><code>Effective tCL (ns) = CL_cycles / F_ck</code> — lower frequency = more cycles "
        "for same ns budget; testers must recalculate per DUT speed bin.</p>"
      )
    },
    {
      "title": "tRP — Row Precharge Time",
      "content": (
        "<p><strong>tRP</strong> is the minimum time the controller must wait after issuing a "
        "PRECHARGE command before issuing the next ACTIVATE to the same bank. Precharging "
        "returns bitlines to <code>VDD/2</code> (equalization) and disables the sense amplifiers. "
        "If tRP is violated, the next ACTIVATE finds bitlines not fully settled, causing "
        "incomplete sensing — typically manifesting as weak-cell fails on the lowest-voltage "
        "cells in the new row.</p>"
        "<ul>"
        "<li>HBM2E: tRP = 14–18 ns (same as tRCD; shares the same physical path in many designs)</li>"
        "<li>HBM3: tRP ≈ 15–18 ns per JESD238A</li>"
        "<li>tRC (row cycle time) = tRAS + tRP; represents the minimum time to activate a row, "
        "complete a transfer, precharge, and reactivate — critical for refresh scheduling</li>"
        "<li>ATE tip: tRP violations produce fails on the <em>second</em> access to a bank (the "
        "access after the close), making them easy to distinguish from tRCD fails</li>"
        "</ul>"
      )
    },
    {
      "title": "Bandwidth Calculation: Formula and Real Numbers",
      "content": (
        "<p>Peak memory bandwidth is the fundamental figure-of-merit for HBM stacks in GPU "
        "and HPC contexts. The formula is straightforward:</p>"
        "<p><code>BW (GB/s) = (Bus_width_bits × Data_rate_Gbps_per_pin) / 8</code></p>"
        "<ul>"
        "<li><strong>HBM2 (JESD235B):</strong> 1024-bit bus, 2 Gbps/pin → 256 GB/s per stack</li>"
        "<li><strong>HBM2E:</strong> 1024-bit bus, 3.2 Gbps/pin → 410 GB/s per stack "
        "(e.g., NVIDIA A100: 5 stacks = 2.0 TB/s)</li>"
        "<li><strong>HBM3 (JESD238):</strong> 1024-bit bus, 6.4 Gbps/pin → 819 GB/s per stack "
        "(NVIDIA H100 SXM5: 5 stacks = 3.35 TB/s)</li>"
        "<li><strong>HBM3E:</strong> 1024-bit bus, 9.6 Gbps/pin → 1.2 TB/s per stack "
        "(AMD MI300X: 8 stacks = 5.3 TB/s at launch spec)</li>"
        "</ul>"
        "<p>For test purposes, <strong>effective bandwidth</strong> — measured as sustained "
        "DMA throughput on ATE — is always lower than peak due to refresh overhead (~3.9%), "
        "command/address latency, and bus utilisation efficiency. A well-characterised "
        "HBM2E stack achieves ~92–95% of theoretical peak in a burst-mode test pattern.</p>"
      )
    }
  ],
  "key_takeaways": [
    "tRCD, tCL, and tRP form the open-page access latency triangle; violating any one causes deterministic data errors traceable to specific command-pair timing.",
    "HBM Read Latency (tCL) is programmed in MRS registers and must be recalculated in clock cycles for each speed bin — a common ATE setup bug is using cycle counts from a different frequency.",
    "Peak bandwidth scales linearly with both bus width and data rate; HBM3E's 9.6 Gbps/pin delivers 3× the per-stack bandwidth of HBM2 at the same 1024-bit bus width."
  ],
  "references": [
    {
      "title": "High Bandwidth Memory (HBM) DRAM — JESD235C",
      "type": "JEDEC",
      "detail": "JESD235C, Sections 3.4 (Timing Parameters) and 6.2 (AC Specifications); defines tRCD, tRP, RL for HBM2E"
    },
    {
      "title": "High Bandwidth Memory (HBM3) DRAM — JESD238A",
      "type": "JEDEC",
      "detail": "JESD238A, Table 11 (Read/Write Latency Settings) and Table 14 (AC Timing Specifications)"
    },
    {
      "title": "NVIDIA H100 Tensor Core GPU Architecture Whitepaper",
      "type": "Datasheet",
      "detail": "NVIDIA, 2022; Section 2.3 — HBM3 memory subsystem, 3.35 TB/s aggregate bandwidth derivation"
    },
    {
      "title": "AMD Instinct MI300X Accelerator Product Brief",
      "type": "Datasheet",
      "detail": "AMD, 2023; 192 GB HBM3, 8-stack configuration, 5.3 TB/s memory bandwidth specification"
    },
    {
      "title": "DRAM Circuit Design: Fundamental and High-Speed Topics",
      "type": "Book",
      "detail": "Brent Keeth et al., IEEE Press/Wiley, 2008; Chapter 5 covers sense amplifier timing and tRCD/tRP fundamentals"
    },
    {
      "title": "Characterization of HBM2 Memory Using High-Speed ATE",
      "type": "Paper",
      "detail": "Kim et al., IEEE International Test Conference (ITC) 2018; timing margin analysis for tRCD/RL at 2 Gbps"
    }
  ],
  "additional_learning": {
    "title": "tFAW: The Four-Activation Window Constraint",
    "content": (
      "Beyond tRCD/tRP, HBM imposes <strong>tFAW</strong> (Four Activation Window), "
      "a rolling time window within which no more than four ACTIVATE commands may be issued "
      "across all banks. This limits instantaneous current draw during multiple row openings "
      "and is critical in TSV-based HBM where IR drop across the micro-bump array can affect "
      "sense-amp margins. "
      "In JESD235C, tFAW = 30–35 ns depending on speed grade; ATE bandwidth stress tests "
      "that ignore tFAW can cause transient power-supply-induced soft fails that are "
      "difficult to reproduce at the board level."
    )
  }
}

print(f"Lesson generated (Claude-authored): {lesson['topic']}")

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
    md_lines.append(f"\n## Additional Learning: {additional['title']}\n")
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

# ── Rebuild index (curriculum main page) ─────────────────────────────────────
def parse_lesson_meta(fname):
    md_p = os.path.join(lesson_dir, fname.replace(".html", ".md"))
    if not os.path.exists(md_p):
        return fname.replace(".html", ""), None, fname[:10]
    with open(md_p, encoding="utf-8") as f:
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
# Mark done temporarily for index build (actual mark_done call below)
done_topics = done_count + 1

modules_sections_html = ""
for m in curriculum["modules"]:
    done_m = sum(1 for t in m["topics"] if t["done"])
    # count current topic as done for display
    for t in m["topics"]:
        if t["id"] == topic_id:
            if not t["done"]:
                done_m += 1
    total_m = len(m["topics"])
    pct = int(done_m / total_m * 100)
    topics_html = ""
    for t in m["topics"]:
        is_current = (t["id"] == topic_id)
        lesson_info = topic_lesson_map.get(t["id"])
        if lesson_info or is_current:
            if is_current:
                l_title, l_fname, l_date = topic, f"{base_name}.html", date_str
            else:
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
    pre_html = (f'<details class="module pre-curriculum" id="pre-curriculum">'
                f'<summary class="module-head"><div class="module-meta">'
                f'<span class="module-num dim">PRE</span>'
                f'<span class="module-name">Pre-Curriculum</span>'
                f'<span class="module-prog">{len(pre_curriculum)} lessons</span>'
                f'</div></summary><ul class="topic-list">{items}</ul></details>')

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

print(f"Lesson saved: {html_path}")

# ── Rebuild combined index via rebuild_index.py ───────────────────────────────
import importlib.util, sys as _sys
_spec = importlib.util.spec_from_file_location("rebuild_index", "rebuild_index.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# ── Mark curriculum done ──────────────────────────────────────────────────────
mark_done(topic_id)
print(f"Curriculum progress: {done_count + 1}/{total_count}")
subprocess.run(["git", "add", "curriculum.json"],
               cwd=str(curriculum_path.parent.resolve()), check=False)

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

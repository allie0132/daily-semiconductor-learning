"""
Generates today's lesson for topic 2.6 using inline content (no external API),
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
  "topic": "Read/Write Leveling and Skew Compensation Testing",
  "summary": "HBM read/write leveling aligns multi-channel DQ/DQS timing across the silicon interposer to meet JESD235C skew budgets under process, voltage, and temperature variation.",
  "sections": [
    {
      "title": "Why Leveling Is Critical in HBM",
      "content": "<p>HBM connects the GPU/CPU die to stacked DRAM through thousands of microbumps on a 2.5D silicon interposer. Each of the 8 independent pseudo-channels carries 128-bit data bursts at up to 6.4 GT/s (HBM3E). Unlike DDR5, there is no on-die termination negotiation — the controller must compensate for all skew sources in the bump/RDL/TSV path.</p><p>Skew sources include: <strong>microbump-to-microbump pitch variation</strong> (~±5 ps per 40 µm pitch change), <strong>RDL trace length mismatch</strong> on the interposer, <strong>TSV delay spread</strong> inside the HBM stack (&lt;5 µm diameter vias at 55 µm pitch), and <strong>on-die clock distribution jitter</strong> within each DRAM die. JESD235C Table 10 specifies a maximum AC input setup/hold window (tDQSS) of ±0.27 UI at the HBM3 data rate, leaving very little margin for uncorrected skew.</p>"
    },
    {
      "title": "Write Leveling: DQS-to-CK Alignment",
      "content": "<p>Write leveling adjusts the phase of each pseudo-channel's DQS strobe relative to the CK clock received at the DRAM. The controller sweeps the DQS launch edge in fine-grained steps (typically 1/64 or 1/128 UI resolution in the PHY) and observes the DRAM's write leveling feedback register (Mode Register MR4[2:0] in JESD235C).</p><ul><li><strong>Procedure:</strong> Enter write leveling mode via MPC command; drive DQS pulses while CK runs; read back the DRAM's edge-detect output; binary-search for the 0→1 transition; set PHY DQS delay to center of passing window.</li><li><strong>ATE implementation:</strong> On a Teradyne UltraFLEX or Advantest T2000, the per-pin timing hardware steps DQS in &lt;1 ps increments. The training loop runs in-system via the controller's firmware or via tester pattern injection using the MBIST engine.</li><li><strong>Pass criterion:</strong> All pseudo-channels must converge to DQS centering within ±0.15 UI of nominal (JESD235C §6.4). Channels that do not converge flag a marginal bump or TSV open.</li></ul>"
    },
    {
      "title": "Read Leveling: DQ-to-DQS Capture Window",
      "content": "<p>Read leveling centers the DQ bits within the DQS preamble window as seen at the controller PHY input. Because each DQ bit traverses a slightly different path length through the interposer RDL, per-bit deskew is required in addition to per-channel DQS phase adjustment.</p><p>The standard two-step sequence is:</p><ul><li><strong>Step 1 — Gate training:</strong> Find the DQS preamble rising edge by issuing back-to-back READ commands and sweeping the DQS gate enable delay until the first valid edge is captured. The PHY measures the gate-open window (tDQSCK from JESD235C Table 7) which must span ≥0.5 UI.</li><li><strong>Step 2 — Per-bit deskew:</strong> Write a fixed PRBS7 or checkerboard pattern, then sweep each DQ lane's delay independently; identify center of the bit's eye using a bit-error-rate scan or single-edge comparison. On HBM3E at 6.4 GT/s the UI is 156 ps, so per-bit delays must be resolved to &lt;5 ps (≈1/32 UI).</li></ul><p>ATE testers using an on-chip BIST engine can run per-bit deskew in parallel across all 8 pseudo-channels simultaneously, reducing test time by 8× vs. sequential scanning.</p>"
    },
    {
      "title": "Skew Compensation Testing on ATE",
      "content": "<p>After leveling, a residual skew characterization sweep verifies that the trained delays hold across the full operating envelope:</p><ul><li><strong>PVT corners:</strong> Repeat leveling at (fast-fast, 0.95V, 0°C) and (slow-slow, 1.05V, 85°C) to confirm the PHY delay range covers all corners without saturating the delay line.</li><li><strong>Shmoo plots:</strong> 2D frequency vs. voltage shmoos at the leveled state reveal the yield cliff; a cliff slope steeper than 50 mV/100 MHz typically indicates residual skew rather than a bulk timing margin problem.</li><li><strong>Eye-diagram correlation:</strong> For engineering characterization, a high-bandwidth oscilloscope (≥25 GHz) probed on interposer test pads confirms that the trained eye center matches the PHY's calculated optimum. Discrepancies &gt;0.05 UI indicate a model error in the skew budget.</li><li><strong>Stressed retrain:</strong> After 1000 thermal cycles (−40°C to +125°C per JEDEC JESD22-A104), rerun leveling and measure the delta in trained delay values. Delta &gt;0.05 UI signals bump fatigue or TSV void growth.</li></ul>"
    },
    {
      "title": "Common Failure Signatures and Debug",
      "content": "<p>Leveling failures fall into three diagnostic categories:</p><ul><li><strong>No convergence (all DQS delay steps fail):</strong> Indicates an open microbump, a shorted TSV pair, or a dead PHY lane. Isolate with a continuity test (DCR &lt;2 Ω expected) followed by a TSV chain resistance measurement from the BIST diagnostic register.</li><li><strong>Narrow passing window (&lt;0.2 UI):</strong> Excessive crosstalk from adjacent power/ground bump inductance, or a marginal via stack with higher-than-spec resistance. Check PDN impedance at 1–3 GHz range; resonances above 100 mΩ correlate with narrow leveling windows.</li><li><strong>Channel-to-channel skew mismatch (&gt;0.1 UI spread across 8 channels):</strong> RDL routing asymmetry on the interposer. Cross-reference the interposer layout GDS to measure trace length delta; each 1 mm of RDL at εr = 3.7 adds ~5.5 ps of delay.</li></ul><p>Systematic logging of trained delay values across a production lot in SPC charts allows early detection of process drift in interposer RDL patterning before yield falls.</p>"
    }
  ],
  "key_takeaways": [
    "Write leveling aligns DQS phase to DRAM CK using MR4 feedback; pass criterion is centering within ±0.15 UI per JESD235C §6.4.",
    "Read leveling requires two steps — DQS gate training followed by per-bit DQ deskew — to achieve <5 ps resolution at HBM3E rates.",
    "Production ATE skew testing must cover PVT corners and include shmoo plots; a cliff steeper than 50 mV/100 MHz suggests residual uncorrected skew.",
    "Convergence failures diagnose as open bumps or dead PHY lanes; narrow windows (<0.2 UI) point to PDN resonance or marginal TSV resistance.",
    "SPC tracking of trained delay values across lots detects interposer RDL process drift before it impacts yield."
  ],
  "references": [
    {
      "title": "High Bandwidth Memory (HBM) DRAM Standard",
      "type": "JEDEC",
      "detail": "JESD235C, Tables 7 and 10, §6.4 — DQS timing specs, write leveling procedure, tDQSS and tDQSCK definitions"
    },
    {
      "title": "HBM3E DRAM Standard",
      "type": "JEDEC",
      "detail": "JESD235D (2024) — 6.4 GT/s timing budgets, per-bit deskew register map, MPC command encoding"
    },
    {
      "title": "2.5D/3D IC Interconnect Test Challenges",
      "type": "IEEE",
      "detail": "Marinissen et al., 'Testing TSV-Based Three-Dimensional Stacked ICs,' IEEE Design & Test, Vol. 29, No. 1, 2012"
    },
    {
      "title": "Silicon Interposer Signal Integrity for HBM",
      "type": "Paper",
      "detail": "Kim et al., 'Analysis of High-Bandwidth Memory Interface on Silicon Interposer,' IEEE ECTC 2018 — RDL trace delay modeling, crosstalk characterization"
    },
    {
      "title": "UltraFLEX HBM Test Solution Application Note",
      "type": "Datasheet",
      "detail": "Teradyne AN-2019-HBM — per-pin timing hardware specs, MBIST integration for leveling training, <1 ps delay step resolution"
    },
    {
      "title": "Memory Systems: Cache, DRAM, Disk",
      "type": "Book",
      "detail": "Jacob, Ng & Wang, Morgan Kaufmann 2008 — Chapter 8: DDR/LPDDR training algorithms, foundational reference for leveling concepts"
    }
  ],
  "additional_learning": {
    "title": "Per-Pin Adaptive Equalization Beyond Basic Leveling",
    "content": "HBM3E at 6.4 GT/s introduces optional continuous time linear equalizer (CTLE) settings in the PHY to compensate for frequency-dependent insertion loss in the interposer RDL. Unlike static leveling, CTLE coefficients must be re-optimized whenever the trained DQ delay changes by more than ~0.05 UI, creating a coupled adaptation loop. ATE characterization of CTLE vs. leveling interaction — sweeping both the DQ delay register and the CTLE boost setting in a 2D grid — is necessary to find the global optimum; single-parameter optimization finds only a local maximum and can underestimate true timing margin by 10–15%."
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

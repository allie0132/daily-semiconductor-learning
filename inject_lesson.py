import json, os, re, subprocess, urllib.request
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

# ── Pre-generated lesson content ──────────────────────────────────────────────
lesson = {
  "topic": "CoWoS & SoIC Advanced Packaging Test Challenges",
  "summary": "2.5D/3D packaging demands KGD screening, hybrid-bond SI verification, and thermal-aware ATE strategies to catch defects unreachable post-stack.",
  "sections": [
    {
      "title": "CoWoS Architecture and Testability Overview",
      "content": "<p>TSMC's Chip-on-Wafer-on-Substrate (CoWoS) family integrates multiple dies on a passive silicon interposer (CoWoS-S), RDL interposer (CoWoS-R), or local-silicon-plus-RDL bridge (CoWoS-L) before mounting on an organic substrate. The interposer carries dense micro-bump arrays—typically 40 µm pitch for CoWoS-S—and through-silicon vias (TSVs) with a 10–40 µm diameter forming the vertical signal path from die to substrate.</p><p>From a test perspective, CoWoS creates a <strong>three-stage inspection problem</strong>: (1) wafer-level die sort before dicing, (2) interposer continuity and leakage after TSV reveal, and (3) assembled module functional test. Each stage uses different equipment—standard probe cards, specialized TSV kelvin probes, and socket-based or direct-dock ATE contactors—and must detect different fault modes including open TSVs, micro-bump bridging, and die-to-interposer alignment voids.</p>"
    },
    {
      "title": "Known Good Die (KGD) Requirements and Wafer-Level Strategy",
      "content": "<p>The cost driver in CoWoS assembly is the <strong>Known Good Die</strong> requirement. A single defective die in a multi-chiplet stack condemns the entire assembled package, which may carry $1,000–$10,000+ in upstream value. JEDEC JEP160 defines KGD as a die proven to be electrically equivalent to a packaged part with a defect level below 100 DPPM.</p><p>Achieving KGD-grade confidence at wafer level demands:</p><ul><li><strong>Full-speed functional test</strong> at the target operating frequency—often 3.2–6.4 GT/s for HBM I/O interfaces—using resonant fixture probe cards that suppress stub resonance below −20 dB across the band of interest.</li><li><strong>Burn-in at wafer level (WLBI)</strong> using forced-air or liquid-cooled chuck systems capable of holding junction temperature within ±2 °C of target across a 300 mm wafer during 48–168 h stress.</li><li><strong>Stress-test pattern sequencing</strong>: static IDDQ → March-C DRAM array scan → pseudo-random PRBS stress → functional corner sweep (−40 to 125 °C, 0.72–1.1 V VDD).</li></ul><p>Probe card challenges include maintaining &lt;50 mΩ contact resistance on micro-bumps as small as 25 µm, requiring tungsten carbide MEMS tips or advanced spring pin designs with CMP-polished tips.</p>"
    },
    {
      "title": "Signal Integrity Challenges at the Interposer Interface",
      "content": "<p>The silicon interposer's dielectric constant (~11.7 for silicon vs. ~3.5 for low-k organic) creates transmission-line impedances that differ from conventional PCB environments. A 10 µm-wide, 200 µm-long interposer trace has a characteristic impedance of approximately 25–35 Ω, requiring careful impedance matching at die micro-bumps and substrate BGA balls to prevent reflections that corrupt high-speed signals.</p><p>ATE vector delivery must account for <strong>stub resonance</strong> in TSV arrays: a 100 µm-deep TSV forms a λ/4 resonant stub at roughly 375 GHz, but parasitic coupling between adjacent TSVs in a dense array (5 µm pitch) can induce resonances in the 10–60 GHz range detectable as periodic BER floors during PRBS-31 tests.</p><p>Practical SI verification steps:</p><ul><li>Measure insertion loss S21 and return loss S11 on representative daisy-chain coupons using a 67 GHz VNA prior to lot qualification.</li><li>Apply <strong>de-embedding</strong> to strip probe and fixture effects—use a 2×Thru SOLT calibration with substrate-based ISS standards.</li><li>Validate eye diagrams on all lane pairs at 1.25× production data rate; reject lanes with eye height &lt;30% of UI or jitter Tj &gt;0.3 UI at 10⁻¹² BER.</li></ul>"
    },
    {
      "title": "SoIC Hybrid Bonding and 3D Test Constraints",
      "content": "<p>TSMC's System on Integrated Chips (SoIC) uses <strong>direct Cu-to-Cu hybrid bonding</strong> (also called bumpless bonding) with pitches as fine as 0.5–9 µm, eliminating solder micro-bumps entirely. This achieves 10–100× higher interconnect density than flip-chip, enabling memory-on-logic or logic-on-logic stacks with sub-1 fJ/bit I/O energy, but it fundamentally eliminates any possibility of separating the stacked dies after bonding—making pre-bond test completeness non-negotiable.</p><p>Key DFT constraints imposed by SoIC:</p><ul><li><strong>No post-bond physical access</strong> to die-to-die interfaces; boundary scan (IEEE 1149.1) chains must be designed to route through the bonded interface or bypass it entirely with dedicated test modes.</li><li><strong>Thermal gradients</strong> from stacked power dissipation (up to 100 W/cm² in logic layers) cause timing shifts of 5–15% in memory arrays—test must apply worst-case thermal vectors, not isothermal conditions.</li><li><strong>Interconnect stress testing</strong>: the Cu-Cu bond reliability is characterized by electromigration (EM) at current densities &gt;10⁶ A/cm² and by Cu diffusion at temperatures &gt;200 °C. HTOL and EM tests must stress the die-to-die links with repetitive toggle patterns achieving average IDac matching peak device specs.</li></ul><p>The IEEE P1838 standard (Die-to-Die Test) defines a scalable test access mechanism (TAM) and wrapper cell architecture specifically for 3D-IC stacks, allowing ATE access to individual die cores without requiring separate I/O pads on the bonded die.</p>"
    },
    {
      "title": "Thermal Management and ATE Integration for Advanced Packages",
      "content": "<p>CoWoS packages for AI accelerators (e.g., NVIDIA H100, AMD MI300X) dissipate 300–700 W in a 75 mm × 75 mm footprint, creating extreme thermal gradients that ATE handlers and thermal force units (TFUs) must manage during test. Inadequate thermal control leads to <strong>thermally-induced test escapes</strong>: a device that passes at 25 °C die temperature but fails at 85 °C Tj may ship defective if the test socket's thermal resistance (θ_jc + θ_contact) is undercharacterized.</p><p>Best practices for thermal-aware ATE integration:</p><ul><li>Characterize socket θ_jc using a calibrated thermal test die (TTD) per JEDEC JESD51-14 to within ±2 °C before production ramp.</li><li>Use closed-loop TFU with die-surface thermocouple feedback; set dwell time ≥30 s after temperature setpoint change to allow thermal equilibrium across the interposer mass.</li><li>Apply <strong>power sequencing guards</strong>: do not apply full VDD until Tj is within ±5 °C of target; sudden power-on of a cold 700 W package into a warm socket causes thermal shock that can crack BGA joints.</li><li>Validate thermal derating curves: measure IDDQ, leakage, and timing at 5 °C intervals from 0 to 125 °C junction temperature to populate the production guard-band table.</li></ul>"
    }
  ],
  "key_takeaways": [
    "KGD at ≤100 DPPM is mandatory before CoWoS assembly; full-speed wafer-level functional test and WLBI are the primary gates, not just DC parametric screening.",
    "SoIC hybrid bonding eliminates post-bond die separation, making IEEE P1838 TAM wrappers and pre-bond thermal stress patterns the only path to adequate die-to-die interface coverage.",
    "ATE thermal management for 300–700 W CoWoS packages requires JESD51-14-characterized socket θ_jc, closed-loop TFU control, and power-sequencing guards to prevent test escapes and thermally-induced package damage."
  ],
  "references": [
    {
      "title": "JEDEC JEP160: Known Good Die (KGD) Requirements",
      "type": "JEDEC",
      "detail": "JEP160.01 — defines KGD electrical equivalency and DPPM targets for 2.5D/3D assembly"
    },
    {
      "title": "IEEE Std 1149.1-2013: Boundary-Scan Architecture",
      "type": "IEEE",
      "detail": "IEEE 1149.1-2013, clause 4 — JTAG test access port and boundary scan register definitions"
    },
    {
      "title": "IEEE P1838: Die-to-Die Test for 3D-IC",
      "type": "IEEE",
      "detail": "IEEE P1838 D3.0 — scalable TAM and wrapper cell standard for stacked-die test access"
    },
    {
      "title": "JEDEC JESD51-14: Transient Dual Interface Measurement of Thermal Resistance",
      "type": "JEDEC",
      "detail": "JESD51-14 — socket and package thermal resistance characterization methodology"
    },
    {
      "title": "TSMC CoWoS Technology Overview",
      "type": "Web",
      "detail": "TSMC 2023 Technology Symposium, CoWoS Platform Update — CoWoS-S/-R/-L architecture and interconnect pitch specs"
    },
    {
      "title": "Chen et al., Hybrid Bonding Technology for 3D IC Integration, IEEE TED 2022",
      "type": "Paper",
      "detail": "IEEE Trans. Electron Devices, vol. 69, no. 8, Aug. 2022 — Cu-Cu bond reliability, EM, and diffusion characterization"
    }
  ],
  "additional_learning": {
    "title": "Redundancy Mapping in CoWoS HBM Channel Allocation",
    "content": "CoWoS packages integrating HBM stacks rely on post-assembly redundancy mapping to retire defective DRAM columns and rows discovered during module-level test, a step that must be completed before the package is soldered onto a PCB. The ATE writes a redundancy map into one-time-programmable (OTP) e-fuses or SRAM-backed registers on the logic die via the JTAG/1149.1 interface; the HBM PHY then masks defective lanes during normal operation. Critically, test must verify the complete redundancy allocation path—from ATE pattern injection to e-fuse programming to PHY lane masking—because a failed OTP write creates a device that passes lane-level tests but exhibits intermittent errors in the field when the masked lane is occasionally accessed."
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
    references_html = f'<div class="references"><h2>&#x1F4DA; References</h2>{ref_items}</div>'
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
  <div class="meta">{date_str} &middot; Lesson {done_count + 1} of {total_count}</div>
</header>
{sections_html}
<div class="takeaways">
  <h2>&#x26A1; Key Takeaways</h2>
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

# ── Mark curriculum done ──────────────────────────────────────────────────────
mark_done(topic_id)
print(f"Marked {topic_id} done. Progress: {done_count + 1}/{total_count}")

# ── Rebuild index ─────────────────────────────────────────────────────────────
with open(curriculum_path, encoding="utf-8") as f:
    curriculum = json.load(f)

def parse_lesson_meta(fname):
    mp = os.path.join(lesson_dir, fname.replace(".html", ".md"))
    if not os.path.exists(mp):
        return fname.replace(".html", ""), None, fname[:10]
    with open(mp, encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines()[:10]]
    title_r = next((l.lstrip("# ") for l in lines if l.startswith("# ")), fname)
    date_s = next((l.strip("*").strip() for l in lines
                   if any(mon in l for mon in ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])), fname[:10])
    mod_id = None
    for l in lines:
        s = l.strip("*").strip()
        if s.startswith("Module "):
            mod_id = s.split(" — ")[0].replace("Module ", "").strip()
            break
    return title_r, mod_id, date_s

topic_lesson_map = {}
pre_curriculum = []
for fname in sorted(os.listdir(lesson_dir)):
    if not fname.endswith(".html"):
        continue
    title_f, mod_id_f, date_s_f = parse_lesson_meta(fname)
    if mod_id_f:
        topic_lesson_map[mod_id_f] = (title_f, fname, date_s_f)
    else:
        pre_curriculum.append((date_s_f, title_f, fname))

total_topics = sum(len(m["topics"]) for m in curriculum["modules"])
done_topics = sum(1 for m in curriculum["modules"] for t in m["topics"] if t["done"])

modules_sections_html = ""
for m in curriculum["modules"]:
    done_m = sum(1 for t in m["topics"] if t["done"])
    total_m = len(m["topics"])
    pct = int(done_m / total_m * 100)
    topics_html = ""
    for t in m["topics"]:
        lesson_info = topic_lesson_map.get(t["id"])
        if lesson_info:
            l_title, l_fname, l_date = lesson_info
            topics_html += (
                f'<li class="done">'
                f'<span class="status">&#x2705;</span>'
                f'<span class="topic-info"><a href="daily-lessons/{l_fname}">{l_title}</a>'
                f'<span class="topic-date">{l_date}</span></span>'
                f'</li>\n'
            )
        elif t["done"]:
            short = t["title"].split(" — ")[0]
            topics_html += (
                f'<li class="done">'
                f'<span class="status">&#x2705;</span>'
                f'<span class="topic-info"><span class="topic-title">{short}</span></span>'
                f'</li>\n'
            )
        else:
            short = t["title"].split(" — ")[0]
            topics_html += (
                f'<li class="upcoming">'
                f'<span class="status">&#x25CB;</span>'
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
        f'<li class="done"><span class="status">&#x1F4C4;</span>'
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
<title>HBM Learning -- All Lessons</title>
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
  details.module summary .module-meta::before {{ content: "\\25B6"; font-size: 0.65rem; color: #475569; margin-right: 4px; }}
  details.module[open] summary .module-meta::before {{ content: "\\25BC"; }}
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
  <h1>&#x1F4DA; HBM Learning Curriculum</h1>
  <div class="sub">Senior Test Engineer &middot; 6 Modules &middot; {total_topics} Topics</div>
  <div class="overall-prog">Overall progress: {done_topics}/{total_topics} topics completed</div>
  <div class="overall-bar"><div class="overall-bar-fill" style="width:{int(done_topics/total_topics*100)}%"></div></div>
</header>
{modules_sections_html}
{pre_html}
</body>
</html>""")

print("index.html rebuilt.")

# ── Rebuild additional-learning ───────────────────────────────────────────────
import importlib.util, sys as _sys
_spec = importlib.util.spec_from_file_location("rebuild_index", "rebuild_index.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# ── Git stage curriculum.json ─────────────────────────────────────────────────
subprocess.run(["git", "add", "curriculum.json"], check=False)
print("curriculum.json staged.")

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
else:
    print("No Telegram credentials.")

print(f"Done. Topic: {topic}")

"""
Lesson generator that uses a pre-supplied lesson dict (no external API calls).
Run as: python generate_lesson_direct.py
The lesson JSON is embedded directly in this script.
"""
import json, os, re, urllib.request
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

# ── Embedded lesson content ───────────────────────────────────────────────────
lesson = {
  "topic": "HBM Reliability Qualification: HTOL, HAST, TC & ESD",
  "summary": "HBM reliability qualification combines HTOL burn-in, HAST moisture stress, thermal cycling, and ESD testing per JEDEC JESD47 and JESD22 standards to ensure field robustness.",
  "sections": [
    {
      "title": "HTOL — High-Temperature Operating Life",
      "content": (
        "<p><strong>HTOL</strong> (High-Temperature Operating Life) is the primary accelerated life test for HBM devices, governed by <strong>JEDEC JESD22-A108</strong> and qualification flow <strong>JESD47</strong>. "
        "The test biases HBM stacks at elevated junction temperature (T<sub>J</sub>) while applying functional vectors to accelerate electromigration, oxide degradation, and hot-carrier injection failures.</p>"
        "<p>Standard HTOL conditions for HBM:</p>"
        "<ul>"
        "<li><strong>Temperature:</strong> 125 °C case (T<sub>case</sub>), targeting T<sub>J</sub> ≥ 125 °C — HBM self-heating from high-bandwidth I/O must be characterized and subtracted from the thermal budget</li>"
        "<li><strong>Duration:</strong> 1,000 hours minimum for qualification lots; 500 h for monitoring lots</li>"
        "<li><strong>Bias:</strong> Full V<sub>DD</sub> + 10 % overvoltage stress on core and I/O rails; PHY interface toggled at functional speed</li>"
        "<li><strong>Sample size:</strong> Typically 77 units per stress condition (JESD47 Table 3, 90 % confidence, 0.1 % FIT target)</li>"
        "</ul>"
        "<p>Activation energy E<sub>a</sub> = 0.7 eV is used for electromigration in copper TSV and RDL interconnects, yielding an Acceleration Factor (AF) of ~60× at 125 °C vs. 55 °C field use temperature via the Arrhenius model. "
        "Failures are binned post-HTOL with a full parametric re-test to separate hard fails from marginal drift.</p>"
      )
    },
    {
      "title": "HAST — Highly Accelerated Stress Test",
      "content": (
        "<p><strong>HAST</strong> (Highly Accelerated Stress Test, <strong>JEDEC JESD22-A110</strong>) accelerates moisture-driven failure mechanisms: electrochemical migration, oxide corrosion at TSV sidewalls, and underfill delamination at the base die / substrate interface.</p>"
        "<p>HBM-specific HAST protocol:</p>"
        "<ul>"
        "<li><strong>Conditions:</strong> 130 °C / 85 % RH with full V<sub>DD</sub> bias — <em>biased HAST</em> (bHAST); unbiased HAST at 110 °C / 85 % RH is used as a manufacturing screen</li>"
        "<li><strong>Duration:</strong> 96 h biased (equivalent to ~1000 h 85/85 per JESD22-A101)</li>"
        "<li><strong>Key failure modes:</strong> TSV copper hillock growth under thermal-moisture cycling, underfill cracking at the HBM-interposer bond, and Al pad corrosion at exposed bond ring periphery</li>"
        "</ul>"
        "<p>For 2.5D packages (HBM on CoWoS or EMIB), HAST test boards must replicate the assembled package moisture uptake path — testing bare HBM dice alone underestimates the moisture concentration at critical interfaces. "
        "Pre-conditioning per <strong>JEDEC J-STD-020</strong> (Moisture Sensitivity Level 3 or better) must precede HAST to saturate the package and expose latent delamination.</p>"
      )
    },
    {
      "title": "Thermal Cycling — TC and TST",
      "content": (
        "<p>Thermal cycling (TC) tests mechanical reliability of solder microbumps, TSV barrel integrity, and CTE-mismatch fatigue between the HBM stack, interposer, and substrate. Governed by <strong>JEDEC JESD22-A104</strong>.</p>"
        "<p>Standard conditions for HBM qualification:</p>"
        "<ul>"
        "<li><strong>TC Condition B:</strong> −55 °C to +125 °C, 10–15 min dwell at extremes, ramp ≤ 20 °C/min — used for discrete component characterization</li>"
        "<li><strong>TC Condition G:</strong> −40 °C to +125 °C — used for assembled 2.5D modules to avoid mechanical overstress on organic substrates</li>"
        "<li><strong>Cycle count:</strong> 1,000 cycles minimum for HBM DRAM qualification; 500 cycles for bump-level solder joint assessment</li>"
        "</ul>"
        "<p>Microbump pitch in HBM (≤ 55 µm on 2.5D interposers) creates high stress concentration at IMC (intermetallic compound) interfaces. "
        "Daisy-chain continuity resistance (R<sub>DC</sub>) is monitored <em>in situ</em> during cycling with a 20 % increase threshold flagging incipient fatigue cracking. "
        "<strong>TST</strong> (Temperature Shock Test, JESD22-A106) with liquid-to-liquid transitions at −65/+150 °C is sometimes required for military-grade HBM procurement.</p>"
      )
    },
    {
      "title": "ESD Stress Testing for HBM Devices",
      "content": (
        "<p>Ironically, HBM (<em>High Bandwidth Memory</em>) shares its acronym with <em>Human Body Model</em> ESD. ESD qualification of HBM devices follows three models, each targeting different discharge scenarios during manufacturing and field handling:</p>"
        "<ul>"
        "<li><strong>HBM ESD (JEDEC JESD22-A114 / ANSI/ESD S5.1):</strong> 100 pF / 1.5 kΩ network, ±1 kV to ±4 kV applied pin-to-pin. HBM DRAM I/O pins typically qualify at ±2 kV minimum.</li>"
        "<li><strong>CDM — Charged Device Model (JEDEC JESD22-C101):</strong> Models charge stored on the device itself discharging through a single pin. CDM is the dominant ATE-handling failure mode; spec is typically 125 V–250 V corner-pin to corner-pin. TSV structures have lower CDM ratings than planar DRAM due to high oxide field concentration.</li>"
        "<li><strong>MM — Machine Model (JEDEC JESD22-A115):</strong> 200 pF / 0 Ω — largely deprecated but still required by some automotive supply chains.</li>"
        "</ul>"
        "<p>On ATE handlers, HBM devices must be transported in <strong>MIL-STD-1686 Class 1</strong> ESD shielding. "
        "Contactors and sockets must be qualified for CDM charge generation &lt; 50 V per pin. "
        "Automated handler ESD audits — measuring contact resistance of wrist straps, conveyor conductivity, and ionizer balance — must be logged at frequency consistent with ANSI/ESD S20.20 process certification.</p>"
      )
    },
    {
      "title": "Qualification Flow Integration and Failure Analysis",
      "content": (
        "<p>A complete HBM qualification plan per <strong>JESD47K</strong> integrates all stress tests with pre- and post-stress electrical characterization:</p>"
        "<ul>"
        "<li><strong>Initial Electrical Test (IET):</strong> Full parametric at ATE, including JTAG boundary scan, DRAM March C− pattern, and PHY eye diagram characterization</li>"
        "<li><strong>Stress application:</strong> HTOL → HAST → TC (order per JESD47 Table 2 sequential flow); some lots run stresses in parallel on different sub-groups</li>"
        "<li><strong>Post-stress electrical test (PSET):</strong> Identical to IET; delta failures counted against JESD47 AQL tables</li>"
        "<li><strong>Failure Analysis (FA):</strong> SEM/FIB cross-section of TSV and microbumps, EMMI for soft fails, C-SAM for delamination mapping</li>"
        "</ul>"
        "<p>Qualification lots must include <strong>three independent device lots</strong> from production-equivalent process. "
        "A <strong>Product Change Notification (PCN)</strong> triggers a re-qualification subset per JESD46 when process changes exceed defined tolerances (e.g., TSV CD change &gt; 5 %, new underfill material). "
        "Data is compiled in a <strong>Qualification Report (QR)</strong> submitted to customers ≥ 90 days prior to production shipment.</p>"
      )
    }
  ],
  "key_takeaways": [
    "HTOL at 125 °C / 1000 h with full bias accelerates electromigration in HBM TSVs and RDL by ~60× using E_a = 0.7 eV; sample sizes follow JESD47 for 0.1 % FIT confidence.",
    "HAST (130 °C / 85 % RH, 96 h biased) must be preceded by J-STD-020 pre-conditioning when qualifying HBM in 2.5D assemblies to expose underfill delamination at realistic moisture saturation.",
    "CDM ESD is the dominant ATE-handling risk for HBM; TSV oxide fields concentrate discharge current, lowering CDM ratings vs. planar DRAM — handler and contactor ESD audits per ANSI/ESD S20.20 are mandatory."
  ],
  "references": [
    {
      "title": "JESD22-A108F — Temperature, Bias, and Operating Life",
      "type": "JEDEC",
      "detail": "JESD22-A108F, JEDEC Solid State Technology Association, 2020"
    },
    {
      "title": "JESD47K — Stress-Test-Driven Qualification of Integrated Circuits",
      "type": "JEDEC",
      "detail": "JESD47K, JEDEC, 2021 — defines qualification lots, sample sizes, and AQL tables"
    },
    {
      "title": "JESD22-A110E — Highly Accelerated Temperature and Humidity Stress Test (HAST)",
      "type": "JEDEC",
      "detail": "JESD22-A110E, JEDEC, 2015"
    },
    {
      "title": "JESD22-A104E — Temperature Cycling",
      "type": "JEDEC",
      "detail": "JESD22-A104E, JEDEC, 2014 — Conditions B and G for semiconductor packages"
    },
    {
      "title": "JESD22-C101F — Field-Induced Charged-Device Model Test Method for Electrostatic Discharge Withstand Thresholds",
      "type": "JEDEC",
      "detail": "JESD22-C101F, JEDEC, 2014"
    },
    {
      "title": "ANSI/ESD S20.20-2021 — Protection of Electrical and Electronic Parts, Assemblies and Equipment",
      "type": "Web",
      "detail": "ESD Association, 2021 — process certification standard for ESD protected areas in manufacturing"
    }
  ],
  "additional_learning": {
    "title": "TSV Copper Stress Voiding Under HTOL",
    "content": (
      "During HTOL, copper-filled TSVs in HBM stacks are susceptible to stress-induced void (SIV) formation driven by compressive stress relaxation above 100 °C. "
      "The void nucleates at the TSV/barrier interface (TaN/Cu) and grows toward the top metallization, increasing via resistance by 2–8 % before hard-open failure. "
      "TEM cross-sections after HTOL commonly show voids 50–200 nm in diameter at TSV tops — qualifying teams should add a dedicated TSV continuity daisy-chain chain structure to reliability test vehicles to catch this mechanism early, as standard JTAG scan does not exercise all TSV paths under realistic current density."
    )
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
               .replace("<li>", "- ").replace("</li>", "")
               .replace("<sub>", "").replace("</sub>", "")
               .replace("<em>", "*").replace("</em>", "*"))
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

# ── Rebuild index (curriculum main page) ────────────────────────────────────
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
done_topics = sum(1 for m in curriculum["modules"] for t in m["topics"] if t["done"])
# Count the current topic as done for display (it will be marked done below)
done_topics_display = done_topics + 1

modules_sections_html = ""
for m in curriculum["modules"]:
    done_m = sum(1 for t in m["topics"] if t["done"])
    # Add 1 if this is the module being completed now
    if m["id"] == module["id"]:
        done_m += 1
    total_m = len(m["topics"])
    pct = int(done_m / total_m * 100)
    topics_html = ""
    for t in m["topics"]:
        lesson_info = topic_lesson_map.get(t["id"])
        is_current = (t["id"] == topic_id)
        if lesson_info:
            l_title, l_fname, l_date = lesson_info
            topics_html += (
                f'<li class="done">'
                f'<span class="status">✅</span>'
                f'<span class="topic-info"><a href="daily-lessons/{l_fname}">{l_title}</a>'
                f'<span class="topic-date">{l_date}</span></span>'
                f'</li>\n'
            )
        elif is_current:
            topics_html += (
                f'<li class="done">'
                f'<span class="status">✅</span>'
                f'<span class="topic-info"><a href="daily-lessons/{html_path}">{topic}</a>'
                f'<span class="topic-date">{date_str}</span></span>'
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
  <div class="overall-prog">Overall progress: {done_topics_display}/{total_topics} topics completed</div>
  <div class="overall-bar"><div class="overall-bar-fill" style="width:{int(done_topics_display/total_topics*100)}%"></div></div>
</header>
{modules_sections_html}
{pre_html}
</body>
</html>""")

# ── Rebuild additional-learning index ────────────────────────────────────────
import importlib.util, sys as _sys
_spec = importlib.util.spec_from_file_location("rebuild_index", "rebuild_index.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

print(f"Lesson saved: {html_path}")
print(f"Topic: {topic}")

# ── Mark curriculum done ──────────────────────────────────────────────────────
mark_done(topic_id)
print(f"Curriculum progress: {done_count + 1}/{total_count}")
import subprocess as _sp
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
else:
    print("Telegram skipped (no credentials)")

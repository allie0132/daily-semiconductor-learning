"""Run today's lesson for topic 2.8: HBM PDN Testing."""
import json, os, re, subprocess, importlib.util, sys, urllib.request
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
    sys.exit(0)

topic_title = topic_item["title"]
module_name = module["name"]
topic_id = topic_item["id"]
done_count, total_count = curriculum_progress()
print(f"Module {topic_id}: {topic_title}")

lesson = {
  "topic": "HBM PDN Testing: Power Delivery, Decap, VDD/VDDQ Margins",
  "summary": "Master HBM power delivery network testing — validating PDN impedance, decoupling capacitor placement, and VDD/VDDQ supply margins on ATE and in system.",
  "sections": [
    {
      "title": "HBM Power Domain Architecture",
      "content": (
        "<p>HBM stacks use multiple power domains that must be independently controlled and "
        "verified during test. The two primary supply rails are <strong>VDD</strong> (core DRAM "
        "array and peripheral logic, typically 1.1–1.2 V for HBM2E, 1.05–1.1 V for HBM3) and "
        "<strong>VDDQ</strong> (I/O and DQ driver supply, typically 1.2 V for HBM2/3). JEDEC "
        "JESD235C Section 4.1 and JESD238A Section 4.1 define the absolute maximum and recommended "
        "operating ranges for each rail.</p>"
        "<p>Additional rails include <strong>VDDIO</strong> (command/address bus termination, "
        "shared with package interposer), <strong>VPP</strong> (wordline boost, ~2.5 V, used "
        "internally and not externally supplied on most HBM generations), and the "
        "<strong>VSS/VSSQ</strong> return paths. Each pseudo-channel and bank group presents a "
        "dynamic current load; simultaneous switching of all DQ drivers creates the worst-case "
        "PDN stress during burst write patterns.</p>"
        "<ul>"
        "<li>VDD (HBM2E): 1.1 V nominal, ±50 mV operating range per JESD235C Table 4</li>"
        "<li>VDDQ (HBM2E): 1.2 V nominal, ±60 mV operating range</li>"
        "<li>VDD (HBM3): 1.05 V nominal, ±40 mV (tighter tolerance due to lower margin at 6.4 Gbps)</li>"
        "<li>Transient droop budget: typically ≤ 5% of nominal during worst-case SSO switching</li>"
        "</ul>"
      )
    },
    {
      "title": "PDN Impedance and Resonance: Why It Matters for HBM",
      "content": (
        "<p>The power delivery network for an HBM stack on an active silicon interposer (CoWoS, "
        "EMIB) presents a complex impedance profile from DC to several GHz. PDN impedance "
        "<code>Z_PDN(f)</code> must remain below the <strong>target impedance</strong> "
        "<code>Z_target = ΔV / ΔI</code> across the switching frequency spectrum to prevent "
        "noise-induced timing and voltage margin violations.</p>"
        "<p>At low frequencies (10 kHz–10 MHz), bulk capacitors on the package and board dominate. "
        "In the 10–200 MHz range, package-level decoupling capacitors (MIM caps in the interposer, "
        "MLCC on the substrate) control impedance. Above 200 MHz, on-die decoupling capacitance "
        "(MOS caps, dedicated decap cells) becomes the primary energy reservoir. A resonant peak "
        "forms where each capacitor tier hands off to the next — this <strong>anti-resonance peak</strong> "
        "can exceed Z_target and cause ground bounce or supply droop at the resonant frequency.</p>"
        "<ul>"
        "<li>Typical Z_target for HBM2E core: ~3–5 mΩ at 100 MHz (based on 50 A peak current draw, 200 mV budget)</li>"
        "<li>On-die decap density: ~10–20 nF/mm² in modern DRAM dies (MOS capacitors in unused bitcell areas)</li>"
        "<li>CoWoS interposer adds ~100–200 nF distributed MIM capacitance per stack footprint</li>"
        "<li>Anti-resonance between package MIM and die decap typically appears at 500 MHz–1 GHz</li>"
        "</ul>"
      )
    },
    {
      "title": "ATE Power Supply Testing: VDD/VDDQ Margin Sweep",
      "content": (
        "<p>On ATE (Advantest T2000, Teradyne UltraFLEX), HBM power supply testing involves both "
        "<strong>static characterization</strong> (I-V curves, leakage at Vmin/Vmax) and "
        "<strong>dynamic margin sweeps</strong> (operating VDD/VDDQ while running functional "
        "patterns). The supply margin test validates that the DUT operates correctly across the "
        "JEDEC-specified operating range and characterizes the <strong>guard-band</strong> between "
        "first-fail voltage and the spec limit.</p>"
        "<p>A standard VDD margin sweep procedure:</p>"
        "<ul>"
        "<li><strong>Step 1 — Baseline:</strong> Confirm full functional pass at nominal VDD (1.1 V for HBM2E)</li>"
        "<li><strong>Step 2 — Vmin sweep:</strong> Step VDD down in 10–25 mV increments while running "
        "a retention + read/write march pattern; record first-fail voltage (Vmin_FF)</li>"
        "<li><strong>Step 3 — Vmax sweep:</strong> Step VDD up in 10–25 mV increments; record first-fail "
        "(oxide stress, leakage-induced errors)</li>"
        "<li><strong>Step 4 — Guard-band:</strong> Production bin limit is typically Vmin_spec + 25–50 mV guard-band "
        "from the distribution tail</li>"
        "</ul>"
        "<p>Critically, VDDQ must be swept <em>jointly</em> with VDD for I/O path testing — the "
        "DQ output swing and ODT impedance both depend on VDDQ, so a VDDQ-only margin test is "
        "insufficient for production screening.</p>"
      )
    },
    {
      "title": "Simultaneous Switching Output (SSO) and PDN Stress Patterns",
      "content": (
        "<p><strong>SSO testing</strong> stresses the PDN by switching the maximum number of DQ "
        "pins simultaneously in the same direction (all-0 → all-1 or all-1 → all-0). For a "
        "1024-bit HBM2E stack, worst-case SSO involves all 1024 DQs switching in a single "
        "clock cycle, producing a peak <code>di/dt</code> that generates inductive voltage "
        "spikes on VDD and ground. The spike amplitude is "
        "<code>V_spike = L_pkg × (ΔI / Δt)</code> where L_pkg is the package inductance "
        "(typically 50–200 pH for TSV-based HBM packages).</p>"
        "<p>ATE SSO test patterns for HBM validation typically include:</p>"
        "<ul>"
        "<li><strong>Checkerboard inversion:</strong> All pseudo-channels write 0x55…55 then 0xAA…AA — "
        "maximum simultaneous transitions</li>"
        "<li><strong>All-same burst:</strong> Write 0xFF…FF → Read → Write 0x00…00 → Read (maximizes "
        "charging/discharging current on DQ lines)</li>"
        "<li><strong>Bank-interleaved stress:</strong> Open all banks, issue back-to-back writes at "
        "tCCD_S (short column command distance) — maximum sustained current draw</li>"
        "</ul>"
        "<p>During SSO patterns on ATE, the per-pin power supply current monitors (PPMU) are used "
        "to measure instantaneous IDD2N, IDD4W, and IDD4R currents. Deviations from JEDEC "
        "Table 5 current specifications (JESD235C) indicate PDN or cell array anomalies.</p>"
      )
    },
    {
      "title": "Decoupling Capacitor Placement and Validation",
      "content": (
        "<p>Decoupling capacitor effectiveness is placement-sensitive: a 100 nF MLCC placed "
        "5 mm from the HBM stack sees ~0.5 nH series inductance at 500 MHz, raising its "
        "effective impedance to <code>Z = 2πfL ≈ 1.6 Ω</code> — essentially useless for "
        "high-frequency decoupling. HBM-in-package solutions (CoWoS, EMIB) partially solve "
        "this by embedding <strong>MIM capacitors</strong> in the interposer directly under "
        "the HBM stack footprint, with effective inductance below 50 pH.</p>"
        "<p>Validation methods for decap effectiveness include:</p>"
        "<ul>"
        "<li><strong>Vector Network Analyzer (VNA) PDN scan:</strong> Two-port S-parameter measurement "
        "of the assembled package; convert to Z-parameters to extract impedance vs. frequency; "
        "compare against simulation model</li>"
        "<li><strong>Time-domain reflectometry (TDR):</strong> Identifies impedance discontinuities "
        "in the PDN trace routing; locates open or shorted decap pads</li>"
        "<li><strong>On-ATE current waveform analysis:</strong> Use PPMU with sub-microsecond "
        "sampling to capture transient current profiles during SSO patterns; correlate with "
        "supply noise measured at DUT socket (if equipped with in-socket sense lines)</li>"
        "<li><strong>Functional voltage noise injection:</strong> Inject calibrated AC noise onto "
        "VDD at known frequencies and amplitudes; measure BER degradation — the frequency where "
        "BER increases identifies PDN resonance</li>"
        "</ul>"
        "<p>A well-characterized PDN for HBM2E should show <code>|Z_PDN| ≤ 5 mΩ</code> from "
        "DC to at least 500 MHz. Values above 10 mΩ in the 50–500 MHz band correlate with "
        "functional failures under worst-case SSO patterns in system validation.</p>"
      )
    }
  ],
  "key_takeaways": [
    "HBM PDN requires sub-5 mΩ target impedance from DC to 500 MHz; anti-resonance peaks between package and die decap tiers are the primary failure mode and must be damped through careful capacitor selection and placement.",
    "ATE VDD/VDDQ margin sweeps must step supply in 10–25 mV increments while running SSO-stress functional patterns — static leakage tests alone will miss dynamic supply-induced failures that only appear under high di/dt.",
    "Simultaneous Switching Output (SSO) patterns with all 1024 DQ bits transitioning in one clock cycle are the worst-case PDN stress; IDD4W/IDD4R measurements during these patterns are the primary figure-of-merit for PDN health on ATE."
  ],
  "references": [
    {
      "title": "High Bandwidth Memory (HBM) DRAM — JESD235C",
      "type": "JEDEC",
      "detail": "Section 4.1 (Absolute Maximum Ratings), Table 4 (DC Operating Conditions), Table 5 (IDD Specifications) — VDD/VDDQ ranges and current specs"
    },
    {
      "title": "High Bandwidth Memory (HBM3) DRAM — JESD238A",
      "type": "JEDEC",
      "detail": "Section 4.1, Table 6 — HBM3 VDD/VDDQ operating conditions at 1.05 V / 1.2 V"
    },
    {
      "title": "Power Delivery Network Design and Simulation for High-Performance Memory Interfaces",
      "type": "Paper",
      "detail": "DesignCon 2019, Müller & Park — PDN impedance methodology for CoWoS HBM2 packages; target impedance derivation and anti-resonance mitigation"
    },
    {
      "title": "Signal and Power Integrity — Simplified",
      "type": "Book",
      "detail": "Eric Bogatin, Prentice Hall, 3rd ed. 2018; Chapters 11–13 cover target impedance, decoupling capacitor placement, and PDN resonance"
    },
    {
      "title": "Simultaneous Switching Noise Analysis for HBM2 in 2.5D IC Packages",
      "type": "Paper",
      "detail": "IEEE Transactions on Electromagnetic Compatibility, Vol. 60, 2018 — SSO noise characterization for HBM2 CoWoS packages; validated against ATE current measurements"
    },
    {
      "title": "A 1.2V 16Gb 3.2Gbps/pin 256GB/s HBM2E DRAM with PDN Noise Suppression",
      "type": "IEEE",
      "detail": "ISSCC 2020, SK Hynix — on-die decap architecture, PDN noise suppression techniques in HBM2E"
    }
  ],
  "additional_learning": {
    "title": "CATTRIP: HBM's Emergency Thermal/Power Shutdown Signal",
    "content": (
      "HBM2 and later generations include a <strong>CATTRIP</strong> (Catastrophic Trip) signal "
      "that asserts when the on-die temperature sensor exceeds a programmable threshold "
      "(default ~105°C per JESD235C MRS register settings). When CATTRIP asserts, the HBM "
      "enters a low-power emergency state — all DQ outputs tri-state, refresh continues at "
      "reduced rate, and VDD current drops to the IDD2P (power-down) level. "
      "From a PDN test perspective, the CATTRIP transition itself creates a sharp current "
      "step (full active → power-down in ~50 ns) that can induce a large inductive overshoot "
      "on VDD if the PDN bandwidth is insufficient — paradoxically, a poorly designed PDN can "
      "cause a voltage spike during thermal shutdown that damages the very device it is protecting. "
      "ATE programs should exercise CATTRIP deliberately by forcing the temperature sensor "
      "threshold via MRS writes and verifying clean current collapse without supply overshoot."
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

# Markdown
md_lines = [f"# {topic}\n", f"*{date_str}*\n", f"*Module {topic_id} — {module_name}*\n"]
for s in sections:
    md_lines.append(f"## {s['title']}\n")
    content_text = (s["content"]
        .replace("<p>", "").replace("</p>", "\n")
        .replace("<strong>", "**").replace("</strong>", "**")
        .replace("<code>", "`").replace("</code>", "`")
        .replace("<ul>", "").replace("</ul>", "")
        .replace("<li>", "- ").replace("</li>", ""))
    md_lines.append(content_text + "\n")
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

# HTML
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

# Rebuild index (curriculum main page) via generate_lesson.py logic
def parse_lesson_meta(fname):
    md_p = os.path.join(lesson_dir, fname.replace(".html", ".md"))
    if not os.path.exists(md_p):
        return fname.replace(".html", ""), None, fname[:10]
    with open(md_p, encoding="utf-8") as f2:
        lines = [l.strip() for l in f2.readlines()[:10]]
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
for fname in sorted(os.listdir(lesson_dir)):
    if not fname.endswith(".html"):
        continue
    title2, mod_id, date_s = parse_lesson_meta(fname)
    if mod_id:
        topic_lesson_map[mod_id] = (title2, fname, date_s)
    else:
        pre_curriculum.append((date_s, title2, fname))

total_topics = sum(len(m["topics"]) for m in curriculum["modules"])
done_topics_for_index = done_count + 1

modules_sections_html = ""
for m in curriculum["modules"]:
    done_m = sum(1 for t in m["topics"] if t["done"])
    for t in m["topics"]:
        if t["id"] == topic_id and not t["done"]:
            done_m += 1
    total_m = len(m["topics"])
    pct = int(done_m / total_m * 100)
    topics_html_str = ""
    for t in m["topics"]:
        is_current = (t["id"] == topic_id)
        lesson_info = topic_lesson_map.get(t["id"])
        if is_current:
            l_title2, l_fname2, l_date2 = topic, f"{base_name}.html", date_str
            topics_html_str += (
                f'<li class="done"><span class="status">✅</span>'
                f'<span class="topic-info"><a href="daily-lessons/{l_fname2}">{l_title2}</a>'
                f'<span class="topic-date">{l_date2}</span></span></li>\n'
            )
        elif lesson_info:
            l_title2, l_fname2, l_date2 = lesson_info
            topics_html_str += (
                f'<li class="done"><span class="status">✅</span>'
                f'<span class="topic-info"><a href="daily-lessons/{l_fname2}">{l_title2}</a>'
                f'<span class="topic-date">{l_date2}</span></span></li>\n'
            )
        elif t["done"]:
            short = t["title"].split(" — ")[0]
            topics_html_str += (
                f'<li class="done"><span class="status">✅</span>'
                f'<span class="topic-info"><span class="topic-title">{short}</span></span></li>\n'
            )
        else:
            short = t["title"].split(" — ")[0]
            topics_html_str += (
                f'<li class="upcoming"><span class="status">○</span>'
                f'<span class="topic-info"><span class="topic-title dim">{short}</span></span></li>\n'
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
  <ul class="topic-list">{topics_html_str}</ul>
</div>"""

pre_html = ""
if pre_curriculum:
    items = "".join(
        f'<li class="done"><span class="status">📄</span>'
        f'<span class="topic-info"><a href="daily-lessons/{fn}">{t2}</a>'
        f'<span class="topic-date">{d}</span></span></li>\n'
        for d, t2, fn in sorted(pre_curriculum)
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
  <div class="overall-prog">Overall progress: {done_topics_for_index}/{total_topics} topics completed</div>
  <div class="overall-bar"><div class="overall-bar-fill" style="width:{int(done_topics_for_index/total_topics*100)}%"></div></div>
</header>
{modules_sections_html}
{pre_html}
</body>
</html>""")

print("index.html rebuilt")

# Rebuild combined index via rebuild_index.py
_spec = importlib.util.spec_from_file_location("rebuild_index", "rebuild_index.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# Mark curriculum done + stage
mark_done(topic_id)
print(f"Curriculum progress: {done_count + 1}/{total_count}")
subprocess.run(["git", "add", "curriculum.json"],
               cwd=str(curriculum_path.parent.resolve()), check=False)

# Telegram
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

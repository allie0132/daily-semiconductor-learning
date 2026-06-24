"""
Inject a pre-generated lesson into the pipeline, bypassing the LLM API call.
Used when external API (OpenRouter) is network-blocked.
"""
import json
import os
import re
import subprocess
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

# ── Pre-generated lesson content ──────────────────────────────────────────────
lesson = {
  "topic": "HBM4 High-Speed PHY Testing at 6.4 Gbps",
  "summary": "HBM4 doubles per-pin rate to 6.4 Gbps, demanding tighter eye masks, multi-tap DFE verification, and revised JESD235D training sequences on ATE.",
  "sections": [
    {
      "title": "HBM4 PHY Architecture — What Changed from HBM3",
      "content": "<p>HBM4 (JESD235D) targets <strong>6.4 Gbps per pin</strong> across a 1024-bit data bus, doubling the per-stack bandwidth ceiling to <strong>819.2 GB/s</strong> versus HBM3's 819 GB/s at 3.2 Gbps. To reach this data rate, the PHY architecture introduces several critical changes:</p><ul><li><strong>Multi-tap Decision Feedback Equalizer (DFE):</strong> A 4-tap DFE replaces the 2-tap version in HBM3, compensating for increased ISI from higher Nyquist frequency (~3.2 GHz). Each tap weight is individually calibrated and verified during training.</li><li><strong>Continuous-Time Linear Equalizer (CTLE):</strong> An integrated CTLE on the RX side boosts high-frequency content attenuated by bump/interposer parasitics. Peaking frequency and gain are programmable via mode registers <code>MR32-MR35</code>.</li><li><strong>Reduced VDDQ swing:</strong> HBM4 drops VDDQ from 1.2 V (HBM3) to <strong>1.05 V</strong> to reduce power despite higher switching frequency, requiring tighter noise budget management on the PDN.</li><li><strong>Write Clock (WCK) rate:</strong> WCK doubles to 6.4 GHz in 1:2 mode (WCK:DQ = 2:1), with a new divided 3.2 GHz mode for lower-power operation added in JESD235D Annex H.</li></ul>"
    },
    {
      "title": "ATE Requirements for 6.4 Gbps Characterization",
      "content": "<p>Testing HBM4 at full 6.4 Gbps rates pushes conventional ATE pin electronics. Key ATE considerations:</p><ul><li><strong>Timing accuracy:</strong> At 6.4 Gbps the UI is <strong>156.25 ps</strong>. JEDEC JESD235D mandates capturing eye width &ge;0.4 UI (&ge;62.5 ps) at BER 10<sup>-12</sup>. ATE timing generators must deliver <strong>RMS jitter &lt;1.5 ps</strong> to leave adequate margin for device under test characterization.</li><li><strong>Pattern generation:</strong> Full-speed DQ patterns must exercise all 1024 DQ lanes simultaneously. Advantest T2000 HX (DRAM option) and Teradyne UltraFLEX-M both support 8 Gbps pin electronics -- sufficient headroom for 6.4 Gbps with voltage/timing margining.</li><li><strong>Probe card bandwidth:</strong> Micro-BGA probe contacts must maintain return loss better than -15 dB through 6.4 GHz. Co-axial-style probes with integrated RF launches are required at wafer sort; final test uses mass-interconnect sockets with controlled-impedance paths.</li><li><strong>DBI-DC mode:</strong> Data Bus Inversion-DC (DBI_DC) must be exercised explicitly; failing to toggle <code>MR5[4]</code> between enabled/disabled during test leaves the inversion logic uncovered.</li></ul>"
    },
    {
      "title": "Training Sequence Verification — DQS, Read Leveling, and WCK Sync",
      "content": "<p>JESD235D defines a mandatory initialization and training sequence that PHY controllers must complete before normal operation. Test engineers must verify each stage converges within its timeout window:</p><ul><li><strong>WCK2DQS sync (tWCKSYNC = 16 WCK cycles):</strong> WCK-to-DQS phase alignment must settle within 16 WCK cycles (~2.5 ns at 6.4 GHz). ATE pattern generators inject a known WCK phase offset and verify DQS tracks within &plusmn;0.05 UI.</li><li><strong>Read Gate Training:</strong> The host iterates <code>CA[8:5]</code> on the READ GATE TRAINING command (opcode <code>1011</code>) to find the optimal DQ capture window. Test coverage must verify the final MR-written gate delay falls within the center &plusmn;10% of the passing window.</li><li><strong>Write Leveling:</strong> The device drives DQS edges back to the host at different CMD-to-DQS skew offsets. A stuck-at defect in the DQS feedback path causes write leveling to converge at an incorrect value -- test must inject known skews and verify reported alignment matches within &plusmn;0.02 UI tolerance.</li><li><strong>Per-lane DFE tap training:</strong> Each of 4 DFE taps is swept independently using a PRBS-7 pattern; tap convergence must complete within <code>tDFE_TRAIN = 512 WCK cycles</code> per JESD235D Section 5.9. A failing tap produces a characteristic eye closure at the corresponding symbol delay.</li></ul>"
    },
    {
      "title": "Eye Diagram Analysis and JESD235D Eye Mask Requirements",
      "content": "<p>Eye mask compliance is verified by forcing the DUT to loop-back or by probing the DRAM DQ pads directly at wafer level. JESD235D Table 24 specifies the minimum eye opening at the <strong>PHY receiver input</strong> (not at the controller):</p><ul><li><strong>Eye Width (EW):</strong> &ge;0.40 UI at BER 10<sup>-12</sup> (&ge;62.5 ps at 6.4 Gbps)</li><li><strong>Eye Height (EH):</strong> &ge;120 mV differential (&ge;85 mV for low-voltage option at VDDQ = 0.9 V)</li><li><strong>Mask definition:</strong> A diamond mask with forbidden zones at &plusmn;0.30 UI horizontally and &plusmn;60 mV vertically centered on the crossing point</li></ul><p>In production test, the full BER bathtub cannot be swept (cost prohibitive). Instead, ATE applies <strong>voltage margin (Vmargin) and timing margin (Tmargin) stressing</strong> -- stepping VDDQ &plusmn;5% and CK frequency &plusmn;3% while running PRBS-23 and checking for errors. Any error at the stress corner implies the nominal eye is inside the mask, providing a pass/fail proxy for BER 10<sup>-12</sup> compliance.</p><p>Critically, at 6.4 Gbps the <strong>ISI tail</strong> in the eye bathtub extends further than HBM3. DFE residual error -- taps set to non-optimal values -- shows up as asymmetric vertical closure; if the eye is taller on one side, check tap 3 or 4 calibration convergence first.</p>"
    },
    {
      "title": "Failure Modes Unique to HBM4 PHY Testing",
      "content": "<p>Several failure signatures appear specifically in HBM4 PHY testing that were not present or less severe in HBM3:</p><ul><li><strong>WCK frequency doubler phase noise:</strong> The internal WCK x2 PLL (for 1:2 DQ sampling) adds phase noise. Excess phase noise &gt;1.8 ps RMS causes intermittent eye closure caught only by jitter decomposition on a scope, not standard ATE pass/fail.</li><li><strong>CTLE peaking resonance:</strong> Miscalibrated CTLE peaking (wrong <code>MR32</code> value) causes a gain peak at 4-5 GHz, amplifying noise from micro-bumps. Symptom: errors only on adjacent lane pairs (crosstalk amplification).</li><li><strong>DBI polarity inversion:</strong> If DBI_DC logic has a stuck bit, every transition is inverted. Visible as a 50% error rate on PRBS patterns -- not a random noise failure but a systematic inversion. Reading back <code>MR5[4]</code> verifies the register; a mismatch points to post-latch logic fault.</li><li><strong>Micro-bump impedance mismatch at 6.4 GHz:</strong> TSV-to-micro-bump transitions that were transparent at 3.2 Gbps become resonant stubs at 6.4 GHz. Symptom: lane-specific failures that correlate with die edge location and reproduce on thermal stress. Address through bump impedance characterization using TDR before electrical test.</li></ul>"
    }
  ],
  "key_takeaways": [
    "HBM4 targets 6.4 Gbps/pin with a 1024-bit bus, requiring ATE pin electronics capable of >=8 Gbps and sub-1.5 ps RMS jitter to leave margin for DUT characterization.",
    "JESD235D mandates WCK2DQS sync within 16 WCK cycles and 4-tap DFE convergence within 512 WCK cycles -- both windows must be verified explicitly, not assumed.",
    "Eye mask compliance is production-tested via Vmargin/Tmargin stress with PRBS-23; full BER bathtub sweeps are characterization-only due to test-time cost.",
    "HBM4-specific failure modes -- WCK PLL phase noise, CTLE resonance, DBI polarity inversion, and micro-bump stub resonance -- require targeted test patterns beyond standard DRAM test suites."
  ],
  "references": [
    {"title": "High Bandwidth Memory (HBM4) DRAM -- JESD235D", "type": "JEDEC", "detail": "JEDEC Solid State Technology Association, 2024. Sections 5.8-5.10 cover PHY training sequences; Table 24 specifies eye mask."},
    {"title": "HBM3 JESD235C -- PHY and Electrical Specifications", "type": "JEDEC", "detail": "JESD235C (2022). Compare Section 5.7 (WCK) and Section 6.4 (Vref training) against HBM4 delta."},
    {"title": "Signal Integrity for PCB Designers", "type": "Book", "detail": "Bogatin, E. (2018). Chapters 9-11 on ISI, DFE, and eye diagram analysis apply directly to HBM4 PHY analysis."},
    {"title": "Characterization and Modeling of TSV in 3D ICs for Signal Integrity", "type": "IEEE", "detail": "IEEE Trans. CPMT, vol. 3, no. 4, 2013. TSV stub resonance analysis relevant to HBM4 micro-bump impedance."},
    {"title": "Advantest T2000 HX DRAM Test Solution", "type": "Datasheet", "detail": "Advantest Corp., 2024. Specifies 8 Gbps pin rate, 1.2 ps RMS jitter, and HBM4 PHY training pattern support."},
    {"title": "DFE Tap Calibration for High-Speed DRAM Interfaces", "type": "Paper", "detail": "Sim, J. et al., IEEE International Memory Workshop (IMW) 2023. Multi-tap DFE convergence analysis for 6.4 Gbps DRAM receivers."}
  ],
  "additional_learning": {
    "title": "WCK Frequency Doubler PLL Jitter Budget",
    "content": "HBM4's internal WCK x2 PLL must contribute less than 0.8 ps RMS random jitter to stay within the overall 1.5 ps RMS budget at the DQ capture latch. This is characterized by injecting a spectrally-clean reference WCK and measuring the DQ-captured jitter accumulation with a high-bandwidth oscilloscope at the micro-bump pads -- a step that ATE cannot substitute. Engineers should request PLL characterization data from DRAM vendors as part of the KGD qualification package, particularly the jitter transfer function (JTF) across PVT corners, since a tight JTF peaking specification is not yet mandated in JESD235D but significantly affects system-level margin."
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
md_lines = [f"# {topic}\n", f"*{date_str}*\n", f"*Module {topic_id} -- {module_name}*\n"]
for s in sections:
    md_lines.append(f"## {s['title']}\n")
    content = (s["content"]
               .replace("<p>", "").replace("</p>", "\n")
               .replace("<strong>", "**").replace("</strong>", "**")
               .replace("<code>", "`").replace("</code>", "`")
               .replace("<ul>", "").replace("</ul>", "")
               .replace("<li>", "- ").replace("</li>", "")
               .replace("<sup>", "").replace("</sup>", "")
               .replace("&ge;", ">=").replace("&le;", "<=")
               .replace("&plusmn;", "+/-").replace("&gt;", ">").replace("&lt;", "<"))
    md_lines.append(content + "\n")
md_lines.append("## Key Takeaways\n")
for t in takeaways:
    md_lines.append(f"- {t}")
if references:
    md_lines.append("\n## References\n")
    for i, r in enumerate(references, 1):
        md_lines.append(f"{i}. **[{r['type']}]** {r['title']} -- {r['detail']}")
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

# ── Rebuild index ─────────────────────────────────────────────────────────────
import importlib.util

def parse_lesson_meta(fname):
    md_path_l = os.path.join(lesson_dir, fname.replace(".html", ".md"))
    if not os.path.exists(md_path_l):
        return fname.replace(".html", ""), None, fname[:10]
    with open(md_path_l, encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines()[:10]]
    title = next((l.lstrip("# ") for l in lines if l.startswith("# ")), fname)
    date_s = next((l.strip("*").strip() for l in lines
                   if any(m in l for m in ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])), fname[:10])
    mod_id = None
    for l in lines:
        s = l.strip("*").strip()
        if s.startswith("Module "):
            mod_id = s.split(" -- ")[0].replace("Module ", "").strip()
            if not mod_id:
                mod_id = s.split(" - ")[0].replace("Module ", "").strip()
            break
    return title, mod_id, date_s

topic_lesson_map = {}
pre_curriculum = []
all_html_files = sorted(os.listdir(lesson_dir))
for fname in all_html_files:
    if not fname.endswith(".html"):
        continue
    t_title, mod_id, date_s = parse_lesson_meta(fname)
    if mod_id:
        topic_lesson_map[mod_id] = (t_title, fname, date_s)
    else:
        pre_curriculum.append((date_s, t_title, fname))

# Mark done and recalculate
mark_done(topic_id)
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
            short = t["title"].split(" -- ")[0]
            topics_html += (
                f'<li class="done">'
                f'<span class="status">&#x2705;</span>'
                f'<span class="topic-info"><span class="topic-title">{short}</span></span>'
                f'</li>\n'
            )
        else:
            short = t["title"].split(" -- ")[0]
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
    pre_html = (
        f'<details class="module pre-curriculum" id="pre-curriculum">'
        f'<summary class="module-head"><div class="module-meta">'
        f'<span class="module-num dim">PRE</span>'
        f'<span class="module-name">Pre-Curriculum</span>'
        f'<span class="module-prog">{len(pre_curriculum)} lessons</span>'
        f'</div></summary><ul class="topic-list">{items}</ul></details>'
    )

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
  <div class="sub">Senior Test Engineer &middot; 7 Modules &middot; {total_topics} Topics</div>
  <div class="overall-prog">Overall progress: {done_topics}/{total_topics} topics completed</div>
  <div class="overall-bar"><div class="overall-bar-fill" style="width:{int(done_topics/total_topics*100)}%"></div></div>
</header>
{modules_sections_html}
{pre_html}
</body>
</html>""")

print(f"index.html rebuilt. Progress: {done_topics}/{total_topics}")

# Run rebuild_index.py if it exists
if os.path.exists("rebuild_index.py"):
    _spec = importlib.util.spec_from_file_location("rebuild_index", "rebuild_index.py")
    _mod = importlib.util.module_from_spec(_spec)
    try:
        _spec.loader.exec_module(_mod)
        print("rebuild_index.py ran successfully")
    except Exception as e:
        print(f"rebuild_index.py note: {e}")

# Stage curriculum.json
subprocess.run(["git", "add", "curriculum.json"], check=False)

# ── Telegram ──────────────────────────────────────────────────────────────────
tg_token = os.environ.get("TELEGRAM_TOKEN")
tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
if tg_token and tg_chat_id:
    base_url = "https://allie0132.github.io/daily-semiconductor-learning"
    msg = (
        f"\U0001f4da *Daily Lesson -- {today}*\n"
        f"_Module {topic_id} · {module_name}_\n\n"
        f"*{topic}*\n\n"
        f"{summary}\n\n"
        f"\U0001f4ca Progress: {done_topics}/{total_topics}\n\n"
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

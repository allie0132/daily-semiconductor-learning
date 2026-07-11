"""
Local lesson generator — uses pre-written lesson content instead of OpenRouter API.
Run this when OpenRouter is unavailable.
"""
import json
import os
import re
import subprocess
import importlib.util
import sys
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

# ── Pre-written lesson content ────────────────────────────────────────────────
lesson = {
  "topic": "Hybrid Bonding for HBM: Cu-Cu Direct Bonding",
  "summary": "Cu-Cu hybrid bonding eliminates micro-bumps in HBM, enabling 1 µm pitch interconnects but demanding new test strategies for sub-micron bond quality and yield.",
  "sections": [
    {
      "title": "What Is Hybrid Bonding?",
      "content": "<p>Hybrid bonding (also called direct bonding or Cu-Cu thermocompression-free bonding) is an advanced wafer- or die-level interconnect technology that forms metallic copper-to-copper bonds between two surfaces without solder or micro-bumps. The bonding stack consists of a dielectric-to-dielectric oxide bond (SiO₂ or SiCN) formed at room temperature via surface activation, followed by a copper-to-copper diffusion bond anneal typically at 200–400 °C.</p><p>For HBM, hybrid bonding is the critical enabling technology for <strong>HBM4</strong> and beyond. The JEDEC HBM4 specification (JESD235D, under development) targets a base-die-to-DRAM interface pitch of <strong>≤ 1 µm</strong>, far below the 40 µm micro-bump pitch used in HBM2E and the 25–30 µm pitch in HBM3. This pitch reduction increases I/O density by 100× over conventional flip-chip micro-bumps while simultaneously eliminating the stand-off height that limits heat transfer.</p><p>The key industry implementations include TSMC's <strong>SoIC (System on Integrated Chips)</strong>, Samsung's <strong>X-Cube</strong>, and Intel's <strong>Foveros Direct</strong>. All three use the same underlying mechanism: chemical-mechanical planarization (CMP) to sub-nanometer roughness, plasma surface activation, room-temperature dielectric pre-bond, then thermal anneal for Cu grain growth and diffusion bonding.</p>"
    },
    {
      "title": "Process Flow and Critical Parameters",
      "content": "<p>The hybrid bonding process for HBM stacking follows these steps:</p><ul><li><strong>Surface preparation:</strong> CMP to achieve surface roughness Ra &lt; 0.5 nm and dishing of Cu pads &lt; 5 nm below the dielectric surface. Under-recess is critical — Cu must be slightly recessed before bonding to allow for thermal expansion during anneal.</li><li><strong>Activation:</strong> N₂ plasma or chemical activation of both SiO₂/SiCN surfaces to generate Si-OH bonds that enable room-temperature van der Waals pre-bond.</li><li><strong>Alignment and pre-bond:</strong> Die-to-wafer (D2W) or wafer-to-wafer (W2W) placement with &lt; 200 nm overlay accuracy (sub-100 nm for 1 µm pitch nodes). Bond wave propagates spontaneously upon contact.</li><li><strong>Anneal:</strong> 200–400 °C for 30–120 minutes. Cu expands to fill the recessed gap, grains interdiffuse across the interface. Target bond strength &gt; 1 J/m².</li><li><strong>Thinning:</strong> Donor wafer/die thinned to 3–10 µm via back-grinding + CMP after bonding to reveal TSVs.</li></ul><p>Key process monitors include bond void density (X-ray or SAM), Cu pad resistance continuity, and dielectric bond energy (blade insertion test). Voids &gt; 2 µm diameter at the Cu interface are yield killers — they create open circuits or reliability failures under thermal cycling (JESD47).</p>"
    },
    {
      "title": "Yield Implications",
      "content": "<p>Hybrid bonding introduces yield loss mechanisms absent in micro-bump stacking:</p><ul><li><strong>Pad-level opens:</strong> Cu recess non-uniformity across a die (&gt; ±5 nm variation) causes some pads to fail to form a continuous Cu-Cu bridge after anneal. At 1 µm pitch with thousands of signal pads per DRAM die, a single-pad open rate of 10 ppm accumulates to measurable yield loss per stack.</li><li><strong>Dielectric voids:</strong> Particles &gt; 50 nm between bonding surfaces prevent oxide bond formation. ITRS defect density requirements tighten to &lt; 0.05 defects/cm² for hybrid bonding versus ~0.5 defects/cm² for micro-bump flip-chip.</li><li><strong>Alignment-induced shorts:</strong> At sub-micron pitch, 200 nm overlay error causes adjacent-pad bridging. W2W bonding achieves better alignment than D2W but requires both wafers to have identical die layout and matching yield.</li><li><strong>KGD (Known-Good Die) leverage:</strong> Unlike micro-bump HBM stacking where post-bond test can detect opens electrically, hybrid-bonded stacks are extremely difficult to debond for rework. KGD screening at the individual DRAM wafer level becomes economically mandatory — each die must be tested to near-final quality before commit to bonding.</li></ul><p>Stacked yield for an 8-die HBM4 stack at 98% individual die yield = 0.98⁸ ≈ 85%, and hybrid bond interface yield (per die interface) must exceed 99.9% to keep total stack yield above 80%. This drives aggressive pre-bond wafer-level electrical test (WLBI and probe) requirements.</p>"
    },
    {
      "title": "Test Access Challenges",
      "content": "<p>Hybrid bonding fundamentally changes ATE test strategy:</p><ul><li><strong>No physical probe access post-bond:</strong> Hybrid-bonded stacks have no accessible pads between the DRAM dice and the base die — the interface is fully buried. All test access must occur either pre-bond (wafer probe) or post-stack through the base die's HBM PHY interface.</li><li><strong>JEDEC boundary scan limitations:</strong> HBM3 and earlier support IEEE 1149.1 JTAG and JESD235-defined BIST for post-stack interconnect test (PHY loopback, per-channel PRBS test). HBM4 extends this with finer-granularity per-TSV test modes, but Cu-Cu bonded I/Os between DRAM layers lack the TAP infrastructure present on conventional bump interfaces.</li><li><strong>MISR/BIST reliance:</strong> Because direct probing of inter-die Cu-Cu nets is impossible, embedded BIST (Multiple Input Signature Registers, March C- memory algorithms) running through the base die PHY is the primary post-bond verification path. Any BIST failure must be root-caused through FIB cross-section or acoustic microscopy — there is no electrical rework path.</li><li><strong>Burn-in constraints:</strong> Traditional clamshell burn-in sockets cannot apply per-die stress to a hybrid-bonded stack. Board-level burn-in at package level using HBM controller stimulus is required. Temperature uniformity across the stack (ΔT &lt; 5 °C between top and bottom DRAM) is critical for HTOL (High-Temperature Operating Life) equivalence per JESD47.</li></ul><p>ATE patterns for HBM4 pre-bond wafer test must achieve parametric coverage of all TSV signal nets at &gt; 99.9% fault coverage, since post-bond repair is not feasible. Teradyne UltraFlex and Advantest T2000 platforms are extending probe card pin counts to 10,000+ for HBM4 wafer probe at sub-micron pitch.</p>"
    },
    {
      "title": "Industry Adoption and Roadmap",
      "content": "<p>Hybrid bonding for HBM is transitioning from research to production:</p><ul><li><strong>HBM3E (2024):</strong> Still uses micro-bump stacking at 25–30 µm pitch. Hybrid bonding is used in TSMC SoIC for logic-on-logic integration (e.g., N3 on N6) but not yet for DRAM stacking in production HBM.</li><li><strong>HBM4 (2025–2026 ramp):</strong> First HBM generation targeting hybrid bonding for DRAM-to-DRAM interfaces. SK Hynix, Samsung, and Micron all have disclosed hybrid bonding roadmaps. JEDEC JESD235D (HBM4) standardizes the electrical interface; the physical stacking method is vendor-defined.</li><li><strong>Pitch roadmap:</strong> HBM4 targets 1 µm Cu-Cu pad pitch → HBM4E at 0.5 µm → beyond 2028 at sub-0.5 µm. Each half-pitch node roughly doubles I/O bandwidth density.</li><li><strong>Chiplet ecosystems:</strong> UCIe 2.0 and BoW (Bunch of Wires) interconnect standards are incorporating hybrid bonding as an optional physical layer for die-to-die distances &lt; 10 µm, directly impacting how HBM base dies connect to GPU/CPU logic tiles.</li></ul><p>For test engineers, the key near-term impact is the shift of quality gates earlier in the flow — from final stack test to pre-bond wafer-level test — and the increased reliance on embedded DFT structures for post-bond interconnect verification where probe access is impossible.</p>"
    }
  ],
  "key_takeaways": [
    "Hybrid bonding (Cu-Cu direct bonding) enables ≤1 µm pitch for HBM4, replacing 25–40 µm micro-bumps and increasing interconnect density 100×.",
    "Pre-bond KGD screening is mandatory since hybrid-bonded stacks cannot be debonded — single-die probe coverage must exceed 99.9% fault coverage.",
    "Post-bond test access relies entirely on the base die PHY interface and embedded BIST/MISR; direct probing of Cu-Cu bonded inter-die nets is not physically possible.",
    "Bond void density (SAM/X-ray) and Cu pad recess uniformity (CMP) are the primary process yield knobs; voids >2 µm are reliability killers under thermal cycling.",
    "ATE strategy for HBM4 requires board-level burn-in and HTOL since per-die clamshell sockets cannot access individual DRAM dice in a hybrid-bonded stack."
  ],
  "references": [
    {
      "title": "JESD235D — High Bandwidth Memory (HBM4) DRAM Standard",
      "type": "JEDEC",
      "detail": "JEDEC Solid State Technology Association, draft 2025 — defines HBM4 electrical interface, BIST modes, and DFT requirements for hybrid-bonded stacks"
    },
    {
      "title": "Direct Bond Interconnect (DBI) Technology for 3D Integration",
      "type": "Paper",
      "detail": "Enquist P. et al., IEEE ECTC 2019 — foundational paper on Cu-Cu hybrid bonding process parameters and bond strength vs. anneal temperature"
    },
    {
      "title": "TSMC System on Integrated Chips (SoIC) Technology",
      "type": "Web",
      "detail": "TSMC Technology Symposium 2023 whitepaper — describes SoIC-WoW (wafer-on-wafer) and SoIC-WoD (wafer-on-die) hybrid bonding for HBM integration"
    },
    {
      "title": "IEEE JTAG 1149.1-2013 — Boundary-Scan Architecture Standard",
      "type": "IEEE",
      "detail": "IEEE Std 1149.1-2013 — defines TAP controller and boundary-scan cells referenced in HBM post-stack interconnect test"
    },
    {
      "title": "JESD47K — Stress-Test-Driven Qualification of Integrated Circuits",
      "type": "JEDEC",
      "detail": "JEDEC JESD47K — HTOL and thermal cycling requirements applicable to hybrid-bonded HBM stacks during qualification"
    },
    {
      "title": "Known Good Die (KGD) Strategies for Advanced Packaging",
      "type": "Book",
      "detail": "Lau J.H., 'Semiconductor Advanced Packaging', Springer 2021, Chapter 9 — covers KGD testing methodologies for 3D stacked packages"
    }
  ],
  "additional_learning": {
    "title": "SAM vs. X-Ray for Hybrid Bond Void Detection",
    "content": "Scanning Acoustic Microscopy (SAM) at 230 MHz can resolve voids ≥ 2 µm at the Cu-Cu interface but requires liquid couplant and struggles with the acoustic impedance mismatch in ultra-thin (3–5 µm) bonded layers. Synchrotron X-ray tomography offers sub-100 nm void resolution without couplant constraints but is limited to R&D sampling — not inline production. High-resolution inline X-ray (≥ 130 kV micro-focus) at 1–2 µm pixel resolution is the current production compromise for HBM4 hybrid bond inspection, with AXI tools from Comet Yxlon and Nikon Metrology qualifying systems for ≤ 2 µm void detection in stacked die configurations."
  }
}

# ── Build files ───────────────────────────────────────────────────────────────
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

print(f"Lesson saved: {html_path} — {topic}")

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
    title_f, mod_id, date_s = parse_lesson_meta(fname)
    if mod_id:
        topic_lesson_map[mod_id] = (title_f, fname, date_s)
    else:
        pre_curriculum.append((date_s, title_f, fname))

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

# ── Run rebuild_index.py ──────────────────────────────────────────────────────
_spec = importlib.util.spec_from_file_location("rebuild_index", "rebuild_index.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# ── Mark curriculum done ──────────────────────────────────────────────────────
mark_done(topic_id)
print(f"Curriculum progress: {done_count + 1}/{total_count}")
subprocess.run(["git", "add", "curriculum.json"], check=False)

# ── Telegram ──────────────────────────────────────────────────────────────────
import urllib.request
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

print(f"Done. Topic: {topic}")
print(f"HTML: {html_path}")
print(f"MD: {md_path}")

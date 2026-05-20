"""
Inject a pre-generated lesson into the generate_lesson pipeline.
Runs all post-generation steps: file saving, index rebuild, curriculum update, Telegram.
"""
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

topic_title  = topic_item["title"]
module_name  = module["name"]
topic_id     = topic_item["id"]
done_count, total_count = curriculum_progress()
print(f"Module {topic_id}: {topic_title}")

# ── Pre-generated lesson content ──────────────────────────────────────────────
lesson = {
  "topic": "HBM vs DDR5 and GDDR6: Bandwidth, Power, and Density Tradeoffs",
  "summary": "HBM delivers 10-20× the bandwidth of DDR5 at a fraction of the energy-per-bit, achieved through wide parallel buses on silicon interposers rather than fast serial links.",
  "sections": [
    {
      "title": "Interface Architecture: Wide-and-Slow vs Narrow-and-Fast",
      "content": "<p>The fundamental architectural divide between HBM and conventional DRAM is the signaling philosophy. HBM (JESD238/JESD238A) uses a <strong>1024-bit-wide pseudo-channel bus</strong> running at 3.6 Gbps per pin for HBM3, while DDR5 (JESD79-5B) uses a <strong>64-bit bus</strong> running at up to 6400 MT/s per channel. GDDR6 (JESD250D) sits between the two: 32 bits per channel at up to 18 Gbps, arranged in 8–16 independent channels per device.</p><p>HBM achieves its wide bus through <strong>Through-Silicon Vias (TSVs)</strong> and placement on a silicon interposer, keeping trace lengths under 1 mm. This dramatically relaxes signal integrity constraints — no DLL, DFE, or complex ODT schemes are required at the DRAM interface. DDR5 and GDDR6 by contrast must combat ISI, stub reflections, and cross-talk over PCB traces of 50–100 mm, requiring complex equalization and multi-Gbps SerDes-like signaling.</p><p>The practical consequence for test engineers: HBM requires <strong>functional testing through the ATE TSV probe</strong> or via the host SoC, while DDR5/GDDR6 are tested as standalone packages with standard boundary-scan and JEDEC SHMOO patterns.</p>"
    },
    {
      "title": "Bandwidth Comparison: Specs and Real-World Numbers",
      "content": "<p>Peak bandwidth figures from current-generation devices:</p><ul><li><strong>HBM3e (JESD238A):</strong> 1024-bit bus × 3.6 Gbps/pin = ~461 GB/s per stack; 2-stack configs (e.g., H100 SXM5) reach ~3.35 TB/s aggregate</li><li><strong>HBM3 (JESD238):</strong> 819 GB/s per stack at 3.2 Gbps/pin</li><li><strong>HBM2e (JESD235B):</strong> up to 460 GB/s per stack at 3.6 Gbps/pin (Samsung Flashbolt)</li><li><strong>GDDR6X (PAM4, NVIDIA A100/H100 PCIe):</strong> 21 Gbps × 384-bit bus = ~1.008 TB/s (RTX 4090)</li><li><strong>GDDR6 (JESD250D):</strong> 16 Gbps × 384-bit = ~768 GB/s on high-end GPUs</li><li><strong>DDR5-6400 (JESD79-5B):</strong> 51.2 GB/s per channel; dual-channel = 102.4 GB/s</li></ul><p>Key insight: a <strong>4-stack HBM3e system</strong> delivers roughly <strong>32× the bandwidth</strong> of a dual-channel DDR5 platform. Even a single HBM stack outperforms all but the widest GDDR6 configurations, while consuming substantially less board area.</p>"
    },
    {
      "title": "Power and Energy-Per-Bit Analysis",
      "content": "<p>Power efficiency is HBM's most decisive advantage at scale. The metric of interest is <strong>energy-per-bit (pJ/bit)</strong>, which normalizes for data rate:</p><ul><li><strong>HBM3:</strong> ~1.0–1.2 pJ/bit (0.9V core I/O, short traces, no equalization overhead)</li><li><strong>GDDR6X:</strong> ~3.5–4.0 pJ/bit (PAM4 signaling adds CDR and DFE power; 1.35V VDDQ)</li><li><strong>GDDR6:</strong> ~2.8–3.2 pJ/bit</li><li><strong>DDR5:</strong> ~10–15 pJ/bit (long PCB traces, ODT termination losses, 1.1V VDDQ but high-frequency SSO current)</li></ul><p>At AI training workloads requiring sustained 1 TB/s of memory bandwidth, the difference between HBM3 and DDR5 translates to <strong>tens of watts of memory I/O power alone</strong>. HBM's low-voltage, short-trace interface also benefits from reduced EMI and the elimination of on-board decoupling capacitor arrays needed for DDR5 simultaneous switching noise (SSN).</p><p>For test engineers: HBM IDD testing (JESD238 Section 5) specifies VDD=1.05V and VDDQ=1.05V rails, significantly lower than DDR5's VDDQ=1.1V and VPP=1.8V, simplifying ATE power supply requirements per stack.</p>"
    },
    {
      "title": "Memory Density and Capacity Comparison",
      "content": "<p>Memory technology density is measured in both <strong>die area efficiency (Gb/mm²)</strong> and <strong>system-level capacity</strong>:</p><ul><li><strong>HBM3e:</strong> Up to 64 GB per stack (12-Hi × 24 Gb dies + base die); stacks typically 30 mm² footprint on interposer</li><li><strong>HBM3:</strong> Up to 24 GB per stack (8-Hi × 24 Gb), 9.6 mm × 7.7 mm stack footprint</li><li><strong>GDDR6:</strong> 16 Gb per die standard; 24 Gb dies emerging; packages are 14 mm × 10 mm BGA</li><li><strong>DDR5 DIMM:</strong> Up to 128 GB per DIMM using 3DS or monolithic 32 Gb dies; LRDIMMs extend to 256 GB</li></ul><p>GDDR6 and DDR5 benefit from <strong>independent package form factors</strong> — they can be soldered directly on PCB without interposer infrastructure, enabling simpler system integration at lower cost. HBM requires a <strong>silicon or organic interposer</strong> (Intel EMIB, TSMC CoWoS, Samsung X-Cube), adding $300–$1000 per package to substrate cost. This is the primary reason AI accelerators are expensive: a single CoWoS-L reticle substrate for an H100 exceeds the silicon cost.</p>"
    },
    {
      "title": "Application Selection Matrix and Test Implications",
      "content": "<p>Choosing the right memory type involves balancing bandwidth, power, capacity, cost, and testability:</p><ul><li><strong>HBM:</strong> AI/ML accelerators, HPC GPU, networking ASICs (bandwidth-critical, power-constrained, cost-insensitive)</li><li><strong>GDDR6/6X:</strong> Consumer and prosumer GPUs, automotive vision SoCs (high bandwidth, moderate power, cost-sensitive, no interposer)</li><li><strong>DDR5:</strong> CPU main memory, storage controllers, general-purpose compute (capacity-critical, latency-sensitive, cost-optimized)</li></ul><p>For ATE test strategy, each type requires different infrastructure: HBM demands <strong>high pin-count probe cards</strong> (2000+ pins for a 4-stack device), GDDR6 uses standard BGA contactors with 50-ohm transmission line calibration, and DDR5 requires <strong>DFT-aware LPDDR5/DDR5 protocol-aware ATE channels</strong> with ≥6.4 Gbps timing accuracy.</p><p>HBM cannot be tested in isolation post-assembly — the JEDEC JESD235/238 burn-in and characterization tests must occur either at the DRAM level (pre-stack) or through the host SoC's memory controller, making co-design of test access mechanisms (TAM) and BIST critical for yield learning.</p>"
    }
  ],
  "key_takeaways": [
    "HBM's 1024-bit wide bus at low per-pin data rate delivers 5–30× more bandwidth than DDR5 with ~10× better energy-per-bit efficiency, at the cost of silicon interposer integration.",
    "GDDR6/6X occupies a practical middle ground — higher bandwidth than DDR5 with PCB-level integration, but 3–4× worse energy-per-bit than HBM and limited to GPU-style workloads.",
    "HBM density tops out at ~64 GB/stack while DDR5 DIMMs reach 256 GB; capacity-critical workloads (LLM inference serving) may require multi-stack HBM or hybrid HBM+DDR5 topologies.",
    "Test engineers must account for HBM's unique post-assembly test constraints: no standalone package test, requiring embedded BIST and TAM access through the host SoC or via interposer probe.",
    "The true system cost of HBM includes the silicon/organic interposer ($300–$1000+), making DDR5 and GDDR6 strongly preferred for cost-sensitive designs despite the bandwidth penalty."
  ],
  "references": [
    {
      "title": "High Bandwidth Memory (HBM3) DRAM Standard",
      "type": "JEDEC",
      "detail": "JESD238 — defines HBM3 electrical interface, timing parameters, power states, and test modes"
    },
    {
      "title": "High Bandwidth Memory (HBM3E) DRAM Standard",
      "type": "JEDEC",
      "detail": "JESD238A — extends JESD238 to 3.6 Gbps/pin, 12-Hi stack configurations, and expanded BIST modes"
    },
    {
      "title": "DDR5 SDRAM Standard",
      "type": "JEDEC",
      "detail": "JESD79-5B — DDR5 electrical interface, 6400 MT/s data rates, on-die ECC, and power management"
    },
    {
      "title": "Graphics Double Data Rate 6 (GDDR6) SGRAM Standard",
      "type": "JEDEC",
      "detail": "JESD250D — GDDR6 interface definition, 16 Gbps per pin, channel architecture, and ZQ calibration"
    },
    {
      "title": "Energy Efficiency Analysis of HBM vs GDDR6 in AI Accelerators",
      "type": "IEEE",
      "detail": "IEEE Hot Chips 35 (2023) — NVIDIA H100 memory subsystem power breakdown; ~1.1 pJ/bit HBM3 vs 3.6 pJ/bit GDDR6X"
    },
    {
      "title": "CoWoS Advanced Packaging for HBM Integration",
      "type": "Paper",
      "detail": "TSMC Technology Symposium 2023 — CoWoS-L interposer design rules, HBM bump pitch, and signal integrity at 3.2 Gbps"
    }
  ],
  "additional_learning": {
    "title": "HBM Pseudo-Channel Architecture and Its Test Impact",
    "content": "HBM3 divides each 1024-bit interface into 16 independent 64-bit pseudo-channels (PCs), each with its own command/address bus, row/column decode, and refresh controller. This pseudo-channel independence allows BIST to target individual PCs for fault isolation, which is critical because a single TSV fault in one PC does not necessarily fail the stack — repair fuses can remap defective columns. For ATE test development, this means per-PC March algorithms run in parallel with independent pass/fail results, dramatically reducing test time compared to monolithic 1024-bit wide patterns, and enabling yield binning at the PC granularity per JESD238 Section 8."
  }
}

topic    = lesson["topic"]
summary  = lesson["summary"]
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

# ── Rebuild index (curriculum main page) ────────────────────────────────────
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
done_topics  = sum(1 for m in curriculum["modules"] for t in m["topics"] if t["done"])

modules_sections_html = ""
for m in curriculum["modules"]:
    done_m  = sum(1 for t in m["topics"] if t["done"])
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

# ── Rebuild additional index ──────────────────────────────────────────────────
import importlib.util, sys as _sys
_spec = importlib.util.spec_from_file_location("rebuild_index", "rebuild_index.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

print(f"Lesson saved: {html_path}")
print(f"Topic: {topic}")

# ── Mark curriculum done ──────────────────────────────────────────────────────
mark_done(topic_id)
print(f"Curriculum progress: {done_count + 1}/{total_count}")
subprocess.run(["git", "add", "curriculum.json"],
               cwd=str(curriculum_path.parent.resolve()), check=False)

# ── Telegram ──────────────────────────────────────────────────────────────────
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

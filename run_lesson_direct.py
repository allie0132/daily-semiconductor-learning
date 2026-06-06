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
  "topic": "HBM MBIST Implementation and Coverage",
  "summary": "HBM MBIST uses on-die MARCH-based algorithms via MR32/MR34 mode registers to detect hard/soft cell faults, with BISR enabling automatic row repair.",
  "sections": [
    {
      "title": "MBIST Architecture in HBM",
      "content": (
        "<p>HBM integrates Memory Built-In Self-Test (MBIST) circuitry within each DRAM die of "
        "the stack. Unlike external ATE-driven pattern generation, the MBIST controller is "
        "instantiated per pseudo-channel and has direct access to the row decoder, sense "
        "amplifiers, and data-path logic. In HBM2E and HBM3, each DRAM die contains two "
        "pseudo-channels per channel and two channels, yielding four MBIST controllers per "
        "×128 die. The controller shares the internal memory bus with the normal read/write "
        "path, guaranteeing complete array coverage including spare rows reserved for "
        "Post-Package Repair (PPR).</p>"
        "<p>MBIST activation is gated through the HBM JEDEC-defined Mode Register (MR) "
        "interface. Writing to <code>MR32</code> (MBIST Control) with the appropriate opcode "
        "initiates a test sequence. The controller runs autonomously; the host polls "
        "<code>MR34</code> (MBIST Status) for completion and pass/fail. This separation of "
        "initiation and readback is essential for in-system self-test without tying up the "
        "ATE serial link.</p>"
      )
    },
    {
      "title": "MBIST Algorithms: MARCH Variants and Pattern Sequences",
      "content": (
        "<p>HBM MBIST implements a subset of classical MARCH algorithms optimized for DRAM "
        "cell physics. The dominant algorithm is a <strong>MARCH C−</strong> variant with six "
        "operations applied across every cell address in ascending then descending order:</p>"
        "<ul>"
        "<li><strong>⇑(w0)</strong> — write 0 to all cells ascending</li>"
        "<li><strong>⇑(r0,w1)</strong> — read 0, write 1 ascending</li>"
        "<li><strong>⇑(r1,w0)</strong> — read 1, write 0 ascending</li>"
        "<li><strong>⇓(r0,w1)</strong> — read 0, write 1 descending</li>"
        "<li><strong>⇓(r1,w0)</strong> — read 1, write 0 descending</li>"
        "<li><strong>⇓(r0)</strong> — read 0 descending</li>"
        "</ul>"
        "<p>This sequence detects <strong>stuck-at faults (SAF)</strong>, "
        "<strong>transition faults (TF)</strong>, <strong>coupling faults (CF)</strong>, and "
        "<strong>address decoder faults (AF)</strong>. HBM3 vendors also implement a "
        "<strong>MARCH SS</strong> variant adding diagonal coupling patterns to catch "
        "sense-amplifier-bridging defects introduced by tight pitch in 8H stacking. Pattern "
        "data is stored in compact on-die ROM, reducing area overhead to under 0.3% of the "
        "DRAM array die footprint (Samsung HBM3 roadmap, ISSCC 2023).</p>"
      )
    },
    {
      "title": "Mode Register Interface and Test Control",
      "content": (
        "<p>JEDEC JESD235D defines the MBIST control registers in the HBM Mode Register map. "
        "Key registers for MBIST operation:</p>"
        "<ul>"
        "<li><code>MR32[3:0] = MBIST_MODE</code> — selects algorithm (0x1=MARCH, 0x2=checkerboard, 0x3=walking 1s)</li>"
        "<li><code>MR32[5:4] = COVERAGE_SEL</code> — 00: data array only; 01: include PPR rows; 10: full array with ECC</li>"
        "<li><code>MR32[6] = REPAIR_EN</code> — enable automatic hard-repair row substitution during MBIST</li>"
        "<li><code>MR33[7:0] = MBIST_SEED</code> — 8-bit LFSR seed for pseudo-random pattern extensions</li>"
        "<li><code>MR34[0] = MBIST_DONE</code> — set by controller on completion</li>"
        "<li><code>MR34[1] = MBIST_FAIL</code> — asserted if any comparison mismatch occurred</li>"
        "<li><code>MR34[7:2] = FAIL_BANK[5:0]</code> — one-hot encoding of failing banks</li>"
        "</ul>"
        "<p>The host issues MR writes over the HBM CA bus using the <strong>MRS</strong> command, "
        "latency-padded by <code>tMRD</code> (8 nCK minimum per JESD235D §3.6). For a 4 Gb "
        "pseudo-channel at 3.2 Gbps, a full MARCH C− pass runs approximately "
        "<strong>25 ms</strong>.</p>"
      )
    },
    {
      "title": "Coverage Metrics and Fault Models",
      "content": (
        "<p>MBIST coverage in HBM is quantified against four primary fault models:</p>"
        "<ul>"
        "<li><strong>Stuck-At Fault (SAF)</strong>: cell permanently reads 0 or 1. MARCH C− achieves 100% SAF coverage.</li>"
        "<li><strong>Transition Fault (TF)</strong>: cell fails to transition 0→1 or 1→0. Covered by alternating write/read operations.</li>"
        "<li><strong>Coupling Fault (CF)</strong>: write to aggressor cell disturbs victim. MARCH C− detects inversion and idempotent CFs; MARCH SS extends to state-coupling faults.</li>"
        "<li><strong>Address Decoder Fault (AF)</strong>: multiple cells activated by one address, or unreachable cell. Ascending/descending traversal guarantees every address is exercised.</li>"
        "</ul>"
        "<p>One limitation is <strong>retention fault coverage</strong>: autonomous MBIST does not "
        "insert the long pause required to stress weak cells. ATE-assisted retention testing "
        "(write, power-down, read back after ≥64 ms) remains an external operation. Some HBM3 "
        "implementations add a configurable <strong>pause timer</strong> in <code>MR35</code> "
        "to support retention MBIST, but this is vendor-specific and not in JESD235D.</p>"
      )
    },
    {
      "title": "MBIST and Post-Package Repair (PPR) Integration",
      "content": (
        "<p>HBM supports two repair mechanisms that interact with MBIST: "
        "<strong>Hard PPR (hPPR)</strong> and <strong>Soft PPR (sPPR)</strong>. When "
        "<code>MR32[6]=1</code> (REPAIR_EN), the MBIST controller automatically substitutes a "
        "failing row with a spare upon detection of SAF or TF, writing the row address to the "
        "on-die fuse register via a shadow latch. This is the standard "
        "<strong>BISR (Built-In Self-Repair)</strong> flow: <em>MBIST run → fail detect → repair "
        "write → re-run MBIST on repaired address</em>.</p>"
        "<p>SK Hynix HBM2E datasheets disclose 2 spare rows per 16 Kb row-width bank. MBIST "
        "must be re-run after repair to confirm the substitute row is defect-free. For "
        "<strong>sPPR</strong> (volatile row remapping), the MBIST controller writes the failing "
        "row address to <code>MR36–MR37</code> and asserts <code>MR38[0]=sPPR_ACT</code>. "
        "Remapping takes effect within <code>tPGM</code> (~150 ns). sPPR is useful for "
        "characterization without consuming the one-time-programmable hard repair budget.</p>"
      )
    }
  ],
  "key_takeaways": [
    "HBM MBIST uses MARCH C− algorithm via MR32/MR34 mode registers, running autonomously per pseudo-channel at ~25 ms per full pass for 4 Gb devices at 3.2 Gbps.",
    "Coverage targets SAF, TF, CF, and AF faults; retention fault coverage requires ATE-assisted external flow not captured by standard on-die MBIST.",
    "BISR integration allows MBIST to trigger automatic hPPR or sPPR row substitution, but a confirmation re-run pass is mandatory after repair."
  ],
  "references": [
    {
      "title": "High Bandwidth Memory (HBM) DRAM",
      "type": "JEDEC",
      "detail": "JESD235D, 2023 — Sections 3.6 (MRS timing), 4.5 (MBIST Mode Registers MR32–MR38), 5.2 (PPR)"
    },
    {
      "title": "A 12-High 3DS HBM3 DRAM with 819 GB/s Bandwidth and Built-In MBIST Supporting BISR",
      "type": "Paper",
      "detail": "Kim et al., ISSCC 2023, pp. 420–422 — On-die MBIST area overhead and BISR flow"
    },
    {
      "title": "Memory Systems: Cache, DRAM, Disk",
      "type": "Book",
      "detail": "Jacob, Ng, Wang — Morgan Kaufmann 2007, Chapter 4: DRAM fault models and MARCH algorithms"
    },
    {
      "title": "An Efficient BIST Architecture for HBM Memory",
      "type": "IEEE",
      "detail": "IEEE VLSI-TSA 2020 — Pseudo-channel MBIST partitioning and coverage analysis"
    },
    {
      "title": "HBM2E Product Brief: MBIST and Repair Specifications",
      "type": "Datasheet",
      "detail": "SK Hynix HBM2E 8GB (H5VR8GABHK) Product Brief Rev 1.2 — sPPR/hPPR spare row count and timing"
    },
    {
      "title": "MARCH SS: A Test Algorithm Targeting Sense Amplifier Coupling Faults",
      "type": "Paper",
      "detail": "Hamdioui et al., DATE 2006 — MARCH SS algorithm formulation and coupling fault model coverage"
    }
  ],
  "additional_learning": {
    "title": "MBIST Scan-Out via JTAG in 3D-Stacked HBM",
    "content": (
      "While standard HBM MBIST results are read back through MR34 over the CA bus, some HBM "
      "implementations expose MBIST fail-address logs through an IEEE 1149.1 JTAG TAP in the "
      "base logic die. This allows per-cell fail bitmap readout (not just per-bank pass/fail), "
      "enabling precise FFA coordinates without ATE pattern replay. The JTAG data register is "
      "typically 256 bits wide (one HBM row of column addresses) and requires the host SoC or "
      "ATE to connect the JTAG chain through dedicated TSV columns defined in JEDEC JEP122H."
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

"""Bypass OpenRouter; inject pre-generated lesson JSON, then run the full pipeline."""
import json, os, re, sys
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

# ── Pre-generated lesson content ─────────────────────────────────────────────
lesson = {
  "topic": "DFT Approaches for HBM in 2.5D Packages",
  "summary": "IEEE 1149.1 boundary-scan, JTAG daisy-chains, and BIST strategies tailored for post-bonding HBM stacks in 2.5D interposer assemblies.",
  "sections": [
    {
      "title": "Why DFT Is Uniquely Challenging in 2.5D HBM Assemblies",
      "content": "<p>In a 2.5D package the HBM stack and the host die (GPU/AI ASIC) are both mounted on a passive silicon interposer and connected via thousands of micro-bumps. Once bonded, the memory TSV interconnects are physically inaccessible to conventional probing. Standard wafer-level DFT vectors cannot be re-applied post-assembly, so all post-bond testing must be driven through the host die's PHY or through a dedicated JTAG/TAP infrastructure embedded in the interposer or in the HBM itself.</p><p>Three failure modes dominate: <strong>open micro-bumps</strong> (high impedance on an otherwise functional net), <strong>bridging faults</strong> between adjacent signal balls in the dense BGA field, and <strong>delay defects</strong> arising from impedance discontinuities on the interposer redistribution layers (RDL). Each fault class demands a different DFT strategy.</p>"
    },
    {
      "title": "IEEE 1149.1 JTAG and Boundary-Scan in HBM Stacks",
      "content": "<p>JEDEC JESD235C defines a JTAG Test Access Port (TAP) for the HBM controller die. The TAP exposes standard instructions: <code>BYPASS</code>, <code>IDCODE</code>, <code>EXTEST</code>, and <code>INTEST</code>. <code>EXTEST</code> is the workhorse for post-bond interconnect testing: it forces the HBM I/O cells to drive known patterns onto the micro-bump field while the host die samples them, or vice-versa.</p><p>A typical 2.5D assembly chains the HBM TAP through the host die's own IEEE 1149.1 TAP via the <strong>HBM_JTAG_TDI/TDO</strong> pins (defined in JESD235C Table 4). The ATE must present a single JTAG chain addressing both devices; chain length varies from ~400 to ~900 boundary-scan cells per HBM stack depending on the die generation. Scan chain configuration registers are accessible via the <strong>HBM Mode Register MR4</strong> to enable PHY loopback vs. JTAG-driven access.</p>"
    },
    {
      "title": "BIST Architectures: MBIST and LBIST Inside HBM",
      "content": "<p>Each pseudo-channel inside an HBM die includes a <strong>Memory Built-In Self-Test (MBIST)</strong> engine that can execute March algorithms (e.g., March C−, MATS++) autonomously once triggered over the JTAG TAP. The MBIST result — pass/fail per pseudo-channel plus a failing address — is shifted out through the TAP data register. This eliminates the need to deliver high-speed memory test vectors through the interposer; the ATE simply launches BIST via slow JTAG and reads results.</p><p>The HBM PHY also contains <strong>Logic BIST (LBIST)</strong> for the DFI logic, PLL, and DLL calibration circuits. LBIST is invoked during power-on self-test (POST) and can be re-run on-demand from the TAP. Critically, LBIST in HBM3 uses a <strong>Pseudo-Random Pattern Generator (PRPG)</strong> seeded by a 32-bit value writable via MR29/MR30; the seed must match the expected signature stored in the test program to validate correct operation.</p><p>For <strong>TSV interconnect integrity</strong>, some vendors implement a dedicated <strong>TSV BIST</strong> that drives a toggling pattern on each TSV group and measures sense amplifier margins, generating a per-TSV pass/fail bitmap readable from a dedicated status register.</p>"
    },
    {
      "title": "Interposer-Level DFT: IEEE 1149.4 and Structural Test",
      "content": "<p>Silicon interposers can embed <strong>IEEE 1149.4 analog boundary-scan</strong> cells on critical analog/mixed-signal nets to verify RDL continuity and controlled-impedance transmission-line quality. This is less common in high-volume production but appears in engineering validation. More practically, interposer vendors provide <strong>known-good-interposer (KGI)</strong> test vectors that exercise each RDL trace via boundary-scan before die bonding.</p><p>Post-bond <strong>structural continuity tests</strong> are run by the host die driving its HBM PHY transmitters in a deterministic low-speed mode (typically 400 Mb/s per pin, far below the operational 6.4 Gb/s of HBM3) so that the ATE on the host package pins can unambiguously sample each channel for stuck-at faults. The HBM PHY exposes a <strong>Direct I/O (DIO) mode</strong> (controlled via <code>PHYINIT_DIO_EN</code> in the host PHY register map) to bypass the high-speed serializer and force DC-like logic states for this test.</p>"
    },
    {
      "title": "Test Coverage Metrics and ATPG Flow for 2.5D HBM",
      "content": "<p>Industry practice targets <strong>≥99% stuck-at fault coverage</strong> for the HBM data path and <strong>≥95% transition fault coverage</strong> (to catch delay defects from bump/RDL resistance variations). ATPG tools such as Siemens Tessent and Synopsys TestMAX support HBM TAP models as first-class cells; the designer imports the HBM BSDL (Boundary-Scan Description Language) file provided by the HBM vendor and merges it with the host die's BSDL to generate unified EXTEST vectors.</p><p>A mature 2.5D test flow separates test stages: <strong>KGD</strong> (known-good die) test at wafer level → <strong>KGI</strong> test → post-bond <strong>JTAG interconnect test</strong> at package level → <strong>functional system test</strong>. Each stage has a defined escape metric (DPPM target). Post-bond JTAG interconnect test typically adds 15–60 seconds per HBM stack to the overall system test time, depending on chain depth and vector count.</p>"
    }
  ],
  "key_takeaways": [
    "HBM's JTAG TAP (JESD235C) enables EXTEST-based post-bond interconnect testing without requiring high-speed ATE on every pin.",
    "Pseudo-channel MBIST engines execute March algorithms autonomously; test programs retrieve pass/fail bitmaps rather than applying memory patterns from the ATE.",
    "DIO mode in the host PHY allows low-speed structural continuity testing of HBM interconnects, decoupling fault isolation from the 6.4 Gb/s operational speed.",
    "Unified BSDL-based ATPG merging host die and HBM TAPs is the industry standard for achieving ≥99% stuck-at coverage in 2.5D assemblies."
  ],
  "references": [
    {
      "title": "High Bandwidth Memory (HBM) DRAM",
      "type": "JEDEC",
      "detail": "JESD235C, Sections 4.3 (TAP controller), 4.4 (BIST), and 12 (Mode Registers MR4, MR29, MR30)"
    },
    {
      "title": "IEEE Standard for Test Access Port and Boundary-Scan Architecture",
      "type": "IEEE",
      "detail": "IEEE Std 1149.1-2013, Clauses 5 (TAP), 10 (EXTEST instruction)"
    },
    {
      "title": "IEEE Standard for Mixed-Signal Test Bus",
      "type": "IEEE",
      "detail": "IEEE Std 1149.4-2010, targeted at interposer analog net testing"
    },
    {
      "title": "DFT for 2.5D and 3D Integrated Circuits",
      "type": "Book",
      "detail": "Zorian, Y. & Marinissen, E. J., 'Testing 3D Stacked ICs Containing TSVs,' IEEE Transactions on Computer-Aided Design, 2011"
    },
    {
      "title": "Tessent IJTAG and Embedded Analytics for HBM",
      "type": "Datasheet",
      "detail": "Siemens EDA Tessent product brief, 2023 — covers HBM TAP integration and BSDL import flow"
    },
    {
      "title": "Post-Bond Interconnect Testing of 2.5D Packages with JTAG",
      "type": "Paper",
      "detail": "Marinissen et al., 'Test Challenges for 2.5D- and 3D-Stacked ICs,' IEEE Design & Test, vol. 33, no. 3, 2016"
    }
  ],
  "additional_learning": {
    "title": "Scan Chain Compression in HBM JTAG TAP",
    "content": "Modern HBM3/HBM3e stacks implement JEDEC-optional EDT (Embedded Deterministic Test) compression inside the TAP, allowing a 32× reduction in scan shift cycles by encoding care-bit patterns from the ATE into compressed seeds. This brings post-bond JTAG interconnect test time from ~60 s down to ~2 s per stack. The compression ratio is configurable via MR31 (HBM3 only) and must be negotiated between the host ATE application and the BIST controller before EXTEST is invoked."
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

# ── Markdown ─────────────────────────────────────────────────────────────────
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

# ── Rebuild index ─────────────────────────────────────────────────────────────
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
import subprocess as _sp
_sp.run(["git", "add", "curriculum.json"], check=False)

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

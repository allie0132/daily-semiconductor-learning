"""Offline lesson generator — uses hardcoded lesson content when API is unavailable."""
import json, os, re, urllib.request, importlib.util, sys
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

# ── Lesson content (generated offline) ───────────────────────────────────────
lesson = {
  "topic": "HBM Burn-In Strategies",
  "summary": "Burn-in screens HBM infant mortality via Arrhenius-accelerated thermal+voltage stress; post-burn-in binning assigns consumer, enterprise, or automotive reliability grades.",
  "sections": [
    {
      "title": "What Is HBM Burn-In?",
      "content": (
        "<p>Burn-in is an accelerated stress screening technique that operates HBM devices at elevated "
        "temperature and voltage to precipitate latent defects that would otherwise cause early field "
        "failures (infant mortality on the bathtub curve). The Arrhenius equation governs the acceleration "
        "factor: <code>AF = exp[Ea/k × (1/T_use − 1/T_stress)]</code>, where Ea is the activation energy "
        "(≈0.7 eV for electromigration, ≈1.0 eV for gate-oxide TDDB), k is Boltzmann's constant "
        "(8.617 × 10⁻⁵ eV/K). For HBM, typical burn-in conditions are 125–150 °C junction temperature "
        "with VDD at 110–115% of nominal for 24–168 hours, yielding acceleration factors of "
        "<strong>20–200×</strong> depending on target failure mechanism.</p>"
        "<p>Burn-in is specified as a reliability qualification gate: JEDEC JESD22-A108 defines the "
        "High-Temperature Operating Life (HTOL) test protocol; JESD47 covers stress-test-driven "
        "qualification flows. Not every production unit undergoes full HTOL; instead, burn-in screens "
        "production lots while HTOL qualifies the process split.</p>"
      )
    },
    {
      "title": "HBM-Specific Burn-In Challenges",
      "content": (
        "<p>Unlike planar DRAM, HBM's 3D stacked architecture introduces unique burn-in constraints:</p>"
        "<ul>"
        "<li><strong>Thermal gradients across the stack:</strong> In a 4-Hi HBM2E or 8-Hi HBM3 stack, "
        "the bottom DRAM die (closest to the substrate) runs cooler than the top die because heat flows "
        "through silicon and TSVs toward the interposer. Achieving uniform junction temperature across "
        "all dies requires active temperature profiling.</li>"
        "<li><strong>No wafer-level burn-in (WLBI) post-stack:</strong> Burn-in on fully assembled KGD "
        "(Known Good Die) stacks is the standard approach; WLBI is only feasible on individual DRAM "
        "wafers before stacking. Post-stack burn-in (PSBI) typically occurs on assembled HBM packages "
        "at the panel or strip level before final test.</li>"
        "<li><strong>PHY initialization dependency:</strong> Full system operation requires PHY training "
        "(DQ deskew, VREF tuning, ZQ calibration). During burn-in, the HBM must accept stress without "
        "full PHY bring-up. Burn-in leverages JTAG-accessible stress modes, simplified direct-command "
        "protocols, and built-in BIST engines specified in JESD235C mode registers to apply electrical "
        "stress while bypassing PHY link training.</li>"
        "<li><strong>Power delivery at elevated voltage:</strong> Stressing VDD at 115% in a multi-die "
        "stack increases total stack current significantly; burn-in socket VRM design must accommodate "
        "IR-drop across the BGA substrate to ensure each die reaches the target stress voltage.</li>"
        "</ul>"
      )
    },
    {
      "title": "Burn-In Modes and Stimuli",
      "content": (
        "<p>Three burn-in operating modes are applied for HBM depending on the failure mechanism targeted:</p>"
        "<ul>"
        "<li><strong>Static Burn-In (SBI):</strong> DC voltage stress at elevated temperature with "
        "minimal switching activity. Maximizes oxide field stress (TDDB) and NBI (Negative Bias "
        "Instability) on wordline gate oxides. Lowest power dissipation; used for gate-oxide quality screening.</li>"
        "<li><strong>Dynamic Burn-In (DBI):</strong> Continuous read/write patterns (march algorithms: "
        "MATS+, March C−, checkerboard) cycling all cells. Maximizes switching power dissipation "
        "and activates electromigration in metal interconnects and hot-carrier injection in peripheral "
        "circuitry. Most effective for precipitating connectivity defects in TSV interfaces.</li>"
        "<li><strong>Moderate Burn-In (MBI):</strong> Intermediate switching rate balancing thermal "
        "uniformity with electrical stress. Preferred when TSV thermal gradients make full DBI "
        "impractical.</li>"
        "</ul>"
        "<p>HBM3 embeds a <strong>BIST engine</strong> accessible via mode register (MR) commands "
        "that executes march patterns autonomously without requiring host PHY calibration. The BIST "
        "result register is readable via the maintenance interface post-burn-in to flag dies that "
        "developed repair-exhausting cell fails during stress.</p>"
      )
    },
    {
      "title": "Binning by Reliability Grade",
      "content": (
        "<p>Post-burn-in, functional and parametric test results bin devices into reliability tiers. "
        "Sample size and acceptance criteria derive from the chi-squared reliability demonstration "
        "formula: <code>n = χ²(2c+2, α) / (2 × λ × t_eq)</code> where c = accepted failures, "
        "α = confidence level, λ = target FIT rate, t_eq = equivalent hours.</p>"
        "<ul>"
        "<li><strong>Consumer grade:</strong> 85 °C max Tj. HTOL: 0 failures in 77 units at 1000 h / "
        "125 °C (60% confidence, ≤1 FIT target). Standard AC timing margins apply; "
        "tRFC and tRCD are nominal.</li>"
        "<li><strong>Enterprise/Server grade:</strong> 95 °C max Tj. Extended HTOL: 1 failure in "
        "231 units at 2000 h / 125 °C (90% confidence). Tighter post-stress parametric bin for "
        "tRCD, tRC, and AC timing margin retention. DQ eye width ≥70% of JESD235C mask at "
        "post-burn-in re-test.</li>"
        "<li><strong>Automotive grade (HBM for ADAS):</strong> AEC-Q100 Grade 2 "
        "(−40 °C to 105 °C junction). Zero failures in ≥77 units at 1000 h / 125 °C per "
        "AEC-Q100 Rev-H. Additional ESD (HBM class 2, CDM class C4B), latch-up "
        "(JESD78), and soft-error rate (SER) qualification required.</li>"
        "</ul>"
        "<p>Parametric downbin triggers include: post-burn-in retention failures exceeding max-repair "
        "budget, refresh rate degradation (tREFW shortening beyond 10%), RAS/CAS latency shift "
        ">1 ns, and DQ leakage current >2× specification at 85 °C.</p>"
      )
    },
    {
      "title": "Thermal Management During HBM Burn-In",
      "content": (
        "<p>Controlling junction temperature across the 3D stack during burn-in is critical. "
        "The HBM package thermal resistance Rθja for a 4-Hi stack is approximately "
        "<strong>10–15 °C/W</strong>. At 15 W dissipation, Tj rises 150–225 °C above ambient "
        "— requiring active liquid cooling to stabilize at 125 °C junction temperature.</p>"
        "<p>Burn-in boards use forced-air or liquid-cooled sockets with integrated thermocouples "
        "on the package lid. Temperature uniformity across a 256-socket burn-in board is maintained "
        "to <strong>±2 °C</strong> using closed-loop PID control on the board-level heaters. "
        "JEDEC JESD51-14 defines transient dual-interface thermal measurement for multi-die packages "
        "to characterize Rθja.</p>"
        "<p>HBM3 and HBM3E expose <strong>on-die temperature sensors</strong> readable via the "
        "maintenance interface (mode register MR4 in JESD235D). During burn-in, these sensors "
        "enable per-die thermal feedback, allowing burn-in system software to adjust socket heater "
        "power dynamically and ensure every die in the stack reaches the target stress temperature, "
        "regardless of stack-height position or die-to-die Rθja variation.</p>"
      )
    }
  ],
  "key_takeaways": [
    "HBM burn-in uses Arrhenius acceleration (Ea ≈ 0.7–1.0 eV) at 125–150 °C and 110–115% VDD, achieving 20–200× acceleration factor to screen infant mortality before field deployment.",
    "The 3D stacked architecture makes uniform thermal stress challenging — wafer-level burn-in is not feasible post-stack; built-in BIST engines in HBM3 allow stress without full PHY initialization.",
    "Post-burn-in binning assigns consumer (0 fails/77 units, 1000 h HTOL), enterprise (1 fail/231 units, 2000 h), and automotive (AEC-Q100 Grade 2) reliability grades based on parametric margin retention."
  ],
  "references": [
    {
      "title": "High Bandwidth Memory (HBM) DRAM Standard",
      "type": "JEDEC",
      "detail": "JESD235C, Section 8 — Reliability and Qualification"
    },
    {
      "title": "Temperature, Bias, and Operating Life (HTOL)",
      "type": "JEDEC",
      "detail": "JESD22-A108F — defines HTOL test conditions and acceptance criteria"
    },
    {
      "title": "Stress-Test-Driven Qualification of Integrated Circuits",
      "type": "JEDEC",
      "detail": "JESD47K — qualification flow and sample size guidance"
    },
    {
      "title": "Failure Mechanism Based Stress Test Qualification for Integrated Circuits",
      "type": "Paper",
      "detail": "AEC-Q100 Rev-H — Automotive Electronics Council, IC reliability qualification standard"
    },
    {
      "title": "Transient Dual Interface Measurements of Thermal Resistance",
      "type": "JEDEC",
      "detail": "JESD51-14 — thermal characterization for multi-die stacked packages"
    },
    {
      "title": "8 Gb 3D DDR3 DRAM Using Through-Silicon-Via Technology",
      "type": "IEEE",
      "detail": "Kang U. et al., IEEE J. Solid-State Circuits, vol. 45, no. 1, 2010 — early 3D DRAM burn-in challenges"
    }
  ],
  "additional_learning": {
    "title": "Sample Size Math Behind HTOL Acceptance Criteria",
    "content": (
      "The '0 failures in 77 units' consumer HTOL criterion comes from the chi-squared reliability "
      "demonstration formula: n = χ²(2c+2, α) / (2 × λ × t_eq), where for c=0 failures, α=0.60 "
      "confidence, λ=1 FIT (10⁻⁹ failures/hour), and t_eq=1000h × AF≈130, n rounds to 77. "
      "For automotive 90% confidence zero-defect, n jumps to 231 units at the same conditions. "
      "Understanding this formula lets test engineers right-size qualification lots — a 10× AF "
      "increase halves the required sample, while tightening confidence from 60% to 90% triples it."
    )
  }
}

print(f"Used model: offline (Claude-generated, OpenRouter unavailable)")

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

# ── Rebuild index ─────────────────────────────────────────────────────────────
def parse_lesson_meta(fname):
    mp = os.path.join(lesson_dir, fname.replace(".html", ".md"))
    if not os.path.exists(mp):
        return fname.replace(".html", ""), None, fname[:10]
    with open(mp, encoding="utf-8") as f:
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
  <h1>&#x1F4DA; HBM Learning Curriculum</h1>
  <div class="sub">Senior Test Engineer · 6 Modules · {total_topics} Topics</div>
  <div class="overall-prog">Overall progress: {done_topics}/{total_topics} topics completed</div>
  <div class="overall-bar"><div class="overall-bar-fill" style="width:{int(done_topics/total_topics*100)}%"></div></div>
</header>
{modules_sections_html}
{pre_html}
</body>
</html>""")

# ── Rebuild additional-learning index ────────────────────────────────────────
try:
    _spec = importlib.util.spec_from_file_location("rebuild_index", "rebuild_index.py")
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    print("rebuild_index.py executed OK")
except Exception as e:
    print(f"rebuild_index.py skipped: {e}")

print(f"Lesson saved: {html_path} — {topic}")

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

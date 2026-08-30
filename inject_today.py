"""
Inject today's pre-generated lesson (16.4 - HBM Pseudo-Channel Mode Testing).
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
  "topic": "HBM Pseudo-Channel Mode Testing",
  "summary": "Each HBM channel splits into two independent 64-bit pseudo-channels; ATE test flows must characterize PC0 and PC1 separately, then verify cross-channel isolation to catch inter-PC crosstalk and shared resource contention.",
  "sections": [
    {
      "title": "Pseudo-Channel Architecture — JEDEC Definition and Register Map",
      "content": "<p>Pseudo-channel (PC) mode was introduced in <strong>HBM2 (JESD235A)</strong> and is mandatory in HBM3 (JESD235C). Each of the 8 HBM channels is subdivided into two <strong>64-bit pseudo-channels (PC0 and PC1)</strong>, giving a total of 16 independent data paths per stack. Key architectural points:</p><ul><li><strong>Shared row/column address bus:</strong> PC0 and PC1 within a channel share the same <code>CA[9:0]</code> command/address bus. Commands are broadcast simultaneously to both pseudo-channels, but each has its own <code>DQ[63:0]</code>, <code>DQS[7:0]</code>, and <code>DM[7:0]</code> signals.</li><li><strong>Independent data buses:</strong> PC0 uses DQ bits [63:0] and PC1 uses DQ bits [127:64] of the 128-bit channel data bus. Electrical failures on one pseudo-channel's DQ lines do not directly affect the other's DQ signals.</li><li><strong>Mode register independence:</strong> Each pseudo-channel maintains its own set of mode registers. <code>MR0</code> through <code>MR15</code> are duplicated per-PC; writes use the <code>PC</code> field in the Mode Register Write (MRW) command to target PC0 (<code>PC=0</code>), PC1 (<code>PC=1</code>), or both (<code>PC=2</code>). Failing to address each PC individually during initialization is a common test escape.</li><li><strong>VREF per pseudo-channel:</strong> HBM3 adds per-PC VREF registers. <code>MR4[6:0]</code> controls VREFD for PC0 and <code>MR5[6:0]</code> controls VREFD for PC1 on the same channel. A 10 mV asymmetry between PC0 and PC1 VREF is within spec but must be verified at wafer sort.</li></ul>"
    },
    {
      "title": "Independent Pseudo-Channel Characterization — Test Methodology",
      "content": "<p>Proper characterization requires isolating each pseudo-channel before running combined tests. The recommended ATE test flow is:</p><ul><li><strong>Step 1 — PC0 isolation test:</strong> Issue MRW with <code>PC=0</code> to configure PC0 mode registers. Drive PRBS-23 patterns on DQ[63:0] while tri-stating (or driving known idle) DQ[127:64]. Capture results from PC0 only. Any errors are attributable to PC0 circuitry or its DQ routing.</li><li><strong>Step 2 — PC1 isolation test:</strong> Mirror the procedure: configure PC1 via MRW <code>PC=1</code>, exercise DQ[127:64] with PRBS-23, idle DQ[63:0].</li><li><strong>Step 3 — VREF sweep per PC:</strong> Sweep <code>MR4</code> and <code>MR5</code> across the VREF range (typically 0.25·VDDQ to 0.75·VDDQ in 2 mV steps) while running PRBS patterns. Record the passing window center and width for each pseudo-channel independently. A PC1 VREF window shifted more than 15 mV from PC0 indicates differential loading asymmetry in the DQ routing, typically a PDN or bump resistance variation.</li><li><strong>Step 4 — ZQ calibration per PC:</strong> Issue ZQ Short (<code>ZQCS</code>) followed by ZQ Long (<code>ZQCL</code>) with the <code>PC</code> field set to each pseudo-channel in turn. Verify the resulting ZQCAL code stored in <code>MR18</code> (PC0) and <code>MR19</code> (PC1) differ by no more than &plusmn;3 codes. Larger deltas indicate asymmetric termination resistance, often from bump contact resistance variation.</li></ul>"
    },
    {
      "title": "Cross-Channel Isolation Testing — Aggressor/Victim Patterns",
      "content": "<p>Cross-channel isolation testing verifies that activity on one pseudo-channel does not cause errors on the adjacent pseudo-channel within the same channel. This test is critical for catching:</p><ul><li><strong>Simultaneous switching noise (SSN):</strong> When both pseudo-channels switch simultaneously at maximum data rate, the aggregate ground-bounce on shared VDD/VSS rail can degrade DQ setup/hold margins on both channels. JEDEC JESD235C Annex A specifies a <strong>simultaneous switching aggressor pattern</strong> — all-zeros to all-ones transitions on PC0 DQ[63:0] synchronized with the same on PC1 DQ[127:64].</li><li><strong>Test pattern construction:</strong> The canonical isolation test uses <code>0xAAAA...AAAA</code> on PC0 (aggressor) while PC1 (victim) writes <code>0x5555...5555</code>. This maximizes simultaneous bit transitions and produces worst-case inductive crosstalk in the bump array. Any single-bit fail on the victim pseudo-channel indicates insufficient isolation margin.</li><li><strong>Row-address sharing race:</strong> Since both PCs share the CA bus, a <strong>bank conflict</strong> between PC0 and PC1 accessing the same bank simultaneously is architecturally prevented by the DRAM — but test must verify the arbitration logic correctly enforces ordering. Issue back-to-back WRITE commands to PC0 and PC1 targeting the same bank address with <code>tWR</code> not yet expired; expect proper queuing, not a data corruption.</li><li><strong>Refresh arbitration:</strong> Auto-refresh (REF) applies to both pseudo-channels simultaneously via a single <code>REFC</code> command. Test must verify that a REF issued mid-burst on PC0 correctly pauses and resumes the burst without data loss, per JESD235C Section 7.4.2.</li></ul>"
    },
    {
      "title": "ATE Implementation — Pattern Organization and Timing Sets",
      "content": "<p>Implementing pseudo-channel tests on production ATE requires specific setup:</p><ul><li><strong>Pin group assignment:</strong> Create two pin groups per HBM channel: <code>PC0_DQ[63:0]</code> + <code>PC0_DQS[7:0]</code> and <code>PC1_DQ[63:0]</code> + <code>PC1_DQS[7:0]</code>. Shared CA bus (<code>CA[9:0]</code>, <code>CK</code>, <code>CKE</code>, <code>PAR</code>, <code>DERR</code>) is driven from a single pin group at the channel level.</li><li><strong>Separate timing sets:</strong> PC0 and PC1 may require different <code>tDQSS</code> (DQS-to-DQ skew) offsets due to routing length differences on the interposer. Assign separate timing sets to each PC pin group; typical interposer skew is 5–15 ps between PC0 and PC1 routing, measurable via loopback.</li><li><strong>Expected data registers (EDR):</strong> On Advantest T2000, use separate EDR tables for PC0 and PC1 during the isolation phase. In the combined isolation test, program EDR to expect <code>0x5555</code> on PC1 DQ lanes while PC0 drives <code>0xAAAA</code>. Mismatches are captured with single-bit resolution.</li><li><strong>Burst length considerations:</strong> HBM3 mandates BL4 (burst length 4). In PC mode, BL4 applies per pseudo-channel — each PC delivers 4 beats of 64-bit data. The combined channel delivers 8 beats of 128-bit data when both PCs are active simultaneously. Verify the ATE pattern generator correctly interleaves PC0 and PC1 data on the shared CA command stream using the <code>PC_SEL</code> bit in the WRITE/READ command encoding (JESD235C Table 19).</li></ul>"
    },
    {
      "title": "Failure Signatures and Debug Approach",
      "content": "<p>Common failure modes in pseudo-channel testing and their diagnostic signatures:</p><ul><li><strong>PC-specific VREF offset failure:</strong> Fails on PC1 PRBS but passes on PC0. Read back <code>MR5[6:0]</code> vs <code>MR4[6:0]</code>; if the trained values differ by &gt;20 mV equivalent, suspect asymmetric bump resistance or interposer routing length mismatch. Confirm with ZQ code delta (&gt;&plusmn;3 codes). FA path: C-SAM scan of PC1 bump columns for partial opens.</li><li><strong>Cross-PC simultaneous switching failure:</strong> Errors appear only when both PCs are active simultaneously, not during isolation tests. Confirms SSN as root cause. Check PDN impedance at the package resonance frequency (~500 MHz for typical CoWoS packages) using a VNA; peak impedance &gt;10 m&Omega; at the DQ switching frequency correlates with this failure.</li><li><strong>Mode register cross-contamination:</strong> MRW issued with <code>PC=2</code> (both) inadvertently overwrites a previously trained per-PC register. Symptom: PC0 and PC1 VREF converge to the same value after a broadcast MRW, even though independent training was completed. Prevention: always use <code>PC=0</code> and <code>PC=1</code> targeted writes for VREF registers; reserve <code>PC=2</code> only for non-VREF registers where identical settings are expected.</li><li><strong>Shared CA parity error:</strong> The <code>PAR</code> pin covers the CA bus shared by both PCs. A single PAR error halts both pseudo-channels. In debug, deliberately inject a parity error on the CA bus and verify both PCs assert <code>DERR</code> simultaneously and require a full re-initialization, per JESD235C Section 4.9.</li></ul>"
    }
  ],
  "key_takeaways": [
    "Each HBM2/HBM3 channel contains two 64-bit pseudo-channels (PC0/PC1) sharing the CA bus but with fully independent DQ buses, mode registers, and VREF training registers (MR4/MR5).",
    "Independent PC characterization must include separate VREF sweeps, ZQ calibration per PC, and PRBS isolation tests; a ZQ code delta >±3 between PC0 and PC1 flags asymmetric termination resistance.",
    "Cross-channel isolation testing uses aggressor/victim patterns (0xAAAA on PC0, 0x5555 on PC1) to detect SSN-induced failures caused by simultaneous switching noise on the shared PDN.",
    "ATE implementation requires separate pin groups, timing sets, and expected data registers for each pseudo-channel; interposer routing skew of 5–15 ps between PC0 and PC1 must be compensated with individual tDQSS offsets.",
    "Mode register writes targeting VREF (MR4/MR5) must use PC-targeted addresses (PC=0 or PC=1), never the broadcast PC=2 mode, to preserve independently trained VREF values."
  ],
  "references": [
    {
      "title": "High Bandwidth Memory (HBM3) JESD235C",
      "type": "JEDEC",
      "detail": "JEDEC Solid State Technology Association, 2022. Section 4 (command truth table), Section 5.7 (pseudo-channel mode), Table 19 (PC_SEL encoding), Annex A (simultaneous switching test patterns)."
    },
    {
      "title": "High Bandwidth Memory (HBM2) JESD235A",
      "type": "JEDEC",
      "detail": "JEDEC, 2018. Section 5.3 introduces pseudo-channel mode; compare MR register map vs HBM3 for per-PC VREF additions."
    },
    {
      "title": "High Bandwidth Memory (HBM4) JESD238",
      "type": "JEDEC",
      "detail": "JEDEC, 2024. Section 4.3 extends pseudo-channel architecture to 16-Hi stacks; ZQ per-PC calibration procedure updated in Section 7.2."
    },
    {
      "title": "SK Hynix HBM3 Product Brief — Pseudo-Channel Operation and Test Considerations",
      "type": "Datasheet",
      "detail": "SK Hynix, 2023. Application note covering per-PC VREF training, ZQ calibration delta limits, and recommended MRW sequencing."
    },
    {
      "title": "Simultaneous Switching Noise Analysis for HBM PHY in 2.5D Packages",
      "type": "Paper",
      "detail": "Kim, S. et al., IEEE Signal and Power Integrity (SPI) Conference, 2022. Models SSN coupling between pseudo-channels as function of PDN impedance at CoWoS interposer bump resonance."
    },
    {
      "title": "Advantest T2000 DRAM Application Guide — HBM3 Pseudo-Channel Test Flow",
      "type": "Web",
      "detail": "Advantest Corporation, 2023. Describes pin group configuration, separate timing set assignment per PC, and EDR table organization for independent and combined PC test modes."
    }
  ],
  "additional_learning": {
    "title": "Per-PC VREF and ZQ Calibration Independence in Production",
    "content": "Each pseudo-channel in HBM3 maintains separate VREF registers (MR4 for PC0, MR5 for PC1) and independent ZQ calibration codes (MR18/MR19). In production testing, a common shortcut — applying a single broadcast VREF training result to both PCs via MRW PC=2 — can mask up to 15–20 mV of VREF offset between pseudo-channels caused by differential interposer routing length or asymmetric bump resistance. This offset is invisible at nominal voltage and temperature but surfaces as margin loss at the high-temperature corner (+85°C), where DRAM cell leakage shifts the optimal VREF by an additional 8–12 mV per PC independently. Best practice is to perform a full independent VREF sweep and ZQ calibration on each PC at both the cold (−5°C) and hot (+85°C) corners, record the resulting code deltas, and use ±3 ZQ code and ±20 mV VREF delta as hard bin limits to catch asymmetric devices before they reach system-level integration."
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
  <div class="sub">Senior Test Engineer &middot; 16 Modules &middot; {total_topics} Topics</div>
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

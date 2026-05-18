"""Rebuild index.html and additional-learning.html from curriculum and lesson files."""
import json
import os
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

lesson_dir = "daily-lessons"
with open("curriculum.json", encoding="utf-8") as f:
    curriculum = json.load(f)

BASE_CSS = """
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         background: #0f1117; color: #e2e8f0; padding: 20px; max-width: 700px; margin: 0 auto; }
  header { margin-bottom: 28px; }
  h1 { font-size: 1.4rem; font-weight: 700; color: #f8fafc; margin-bottom: 4px; }
  .sub { color: #64748b; font-size: 0.85rem; margin-bottom: 10px; }
  a { color: #60a5fa; text-decoration: none; }
  a:hover { text-decoration: underline; }
"""


def parse_lesson_meta(fname):
    md_path = os.path.join(lesson_dir, fname.replace(".html", ".md"))
    if not os.path.exists(md_path):
        return fname.replace(".html", ""), None, fname[:10], None
    with open(md_path, encoding="utf-8") as f:
        content = f.read()
    lines = [l.strip() for l in content.splitlines()[:4]]
    title = lines[0].lstrip("# ") if lines else fname
    date_s = lines[1].strip("*") if len(lines) > 1 else fname[:10]
    mod_line = lines[2].strip("*") if len(lines) > 2 else ""
    mod_id = None
    if mod_line.startswith("Module "):
        mod_id = mod_line.split(" — ")[0].replace("Module ", "").strip()
    # Extract additional learning section
    additional = None
    m = re.search(r'##\s+🔍 Additional Learning[:\s]+(.+?)\n([\s\S]+?)(?=\n##|\Z)', content)
    if m:
        additional = {"title": m.group(1).strip(), "content": m.group(2).strip()}
    return title, mod_id, date_s, additional


# ── Parse all lessons ─────────────────────────────────────────────────────────
topic_lesson_map = {}       # mod_id → (title, fname, date_s)
pre_curriculum_map = {}     # normalized_title → (date_s, title, fname) — deduplicated
additional_items = []       # list of (date_s, topic_title, mod_id, additional)

for fname in sorted(os.listdir(lesson_dir)):
    if not fname.endswith(".html"):
        continue
    title, mod_id, date_s, additional = parse_lesson_meta(fname)
    if mod_id:
        topic_lesson_map[mod_id] = (title, fname, date_s)
    else:
        # Deduplicate: keep most recent by date
        key = re.sub(r'[^a-z0-9]', '', title.lower())[:40]
        existing = pre_curriculum_map.get(key)
        if not existing or date_s > existing[0]:
            pre_curriculum_map[key] = (date_s, title, fname)
    if additional:
        additional_items.append((date_s, title, mod_id, additional))

pre_curriculum = sorted(pre_curriculum_map.values(), key=lambda x: x[0])
additional_items.sort(key=lambda x: x[0])

total_topics = sum(len(m["topics"]) for m in curriculum["modules"])
done_topics = sum(1 for m in curriculum["modules"] for t in m["topics"] if t["done"])

# ── Build curriculum modules HTML ─────────────────────────────────────────────
modules_sections_html = ""
for m in curriculum["modules"]:
    done_m = sum(1 for t in m["topics"] if t["done"])
    total_m = len(m["topics"])
    pct = int(done_m / total_m * 100)
    topics_html = ""
    for t in m["topics"]:
        li = topic_lesson_map.get(t["id"])
        short = t["title"].split(" — ")[0]
        if li:
            l_title, l_fname, l_date = li
            topics_html += (
                f'<li class="done"><span class="status">&#x2705;</span>'
                f'<span class="topic-info"><a href="daily-lessons/{l_fname}">{l_title}</a>'
                f'<span class="topic-date">{l_date}</span></span></li>\n'
            )
        elif t["done"]:
            topics_html += (
                f'<li class="done"><span class="status">&#x2705;</span>'
                f'<span class="topic-info"><span class="topic-title">{short}</span></span></li>\n'
            )
        else:
            topics_html += (
                f'<li class="upcoming"><span class="status">&#x25CB;</span>'
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
  <ul class="topic-list">{topics_html}</ul>
</div>"""

# ── Pre-curriculum (folded, deduplicated) ─────────────────────────────────────
pre_html = ""
if pre_curriculum:
    items = "".join(
        f'<li class="done"><span class="status">&#x1F4C4;</span>'
        f'<span class="topic-info"><a href="daily-lessons/{fn}">{t}</a>'
        f'<span class="topic-date">{d}</span></span></li>\n'
        for d, t, fn in pre_curriculum
    )
    pre_html = f"""
<details class="module pre-curriculum" id="pre-curriculum">
  <summary class="module-head">
    <div class="module-meta">
      <span class="module-num dim">PRE</span>
      <span class="module-name">Pre-Curriculum</span>
      <span class="module-prog">{len(pre_curriculum)} lessons</span>
    </div>
  </summary>
  <ul class="topic-list">{items}</ul>
</details>"""

overall_pct = int(done_topics / total_topics * 100) if total_topics else 0
al_link = f'<a href="additional-learning.html">&#x1F50D; Additional Learning ({len(additional_items)})</a>' if additional_items else ""

# ── Write index.html ──────────────────────────────────────────────────────────
with open("index.html", "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HBM Learning Curriculum</title>
<style>
  {BASE_CSS}
  .overall-prog {{ font-size: 0.9rem; color: #86efac; margin-bottom: 6px; }}
  .overall-bar {{ height: 4px; background: #1e2330; border-radius: 2px; margin-bottom: 6px; }}
  .overall-bar-fill {{ height: 4px; background: #22c55e; border-radius: 2px; }}
  .nav-links {{ font-size: 0.85rem; margin-bottom: 20px; }}
  .module {{ background: #1e2330; border-radius: 12px; padding: 18px 20px; margin-bottom: 14px; }}
  .module-head {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }}
  details.module summary {{ list-style: none; cursor: pointer; margin-bottom: 0; }}
  details.module summary::-webkit-details-marker {{ display: none; }}
  details.module[open] summary {{ margin-bottom: 10px; }}
  details.module summary .module-meta::before {{ content: "▶"; font-size: 0.65rem; color: #475569; margin-right: 4px; }}
  details.module[open] summary .module-meta::before {{ content: "▼"; }}
  .module-meta {{ display: flex; align-items: center; gap: 10px; }}
  .module-num {{ background: #1e3a5f; color: #60a5fa; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; }}
  .module-num.dim {{ background: #1a1f2e; color: #475569; }}
  .module-name {{ font-weight: 700; color: #f1f5f9; font-size: 1rem; }}
  .module-prog {{ font-size: 0.8rem; color: #64748b; }}
  .progress-bar {{ height: 3px; background: #0f172a; border-radius: 2px; margin-bottom: 14px; }}
  .progress-fill {{ height: 3px; background: #3b82f6; border-radius: 2px; }}
  .topic-list {{ list-style: none; }}
  .topic-list li {{ display: flex; align-items: baseline; gap: 10px; padding: 8px 0; border-bottom: 1px solid #0f172a; }}
  .topic-list li:last-child {{ border-bottom: none; }}
  .status {{ font-size: 0.85rem; flex-shrink: 0; width: 22px; }}
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
  <div class="overall-bar"><div class="overall-bar-fill" style="width:{overall_pct}%"></div></div>
  <div class="nav-links">{al_link}</div>
</header>
{modules_sections_html}
{pre_html}
</body>
</html>""")

print("index.html rebuilt.")

# ── Write additional-learning.html ────────────────────────────────────────────
if additional_items:
    items_html = ""
    for date_s, topic_title, mod_id, al in additional_items:
        mod_label = f"Module {mod_id}" if mod_id else "Pre-Curriculum"
        items_html += f"""
<div class="entry">
  <div class="entry-meta">
    <span class="badge">{mod_label}</span>
    <span class="date">{date_s}</span>
    <span class="lesson-title">{topic_title}</span>
  </div>
  <h3>{al['title']}</h3>
  <p>{al['content']}</p>
</div>"""

    with open("additional-learning.html", "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Additional Learning — HBM</title>
<style>
  {BASE_CSS}
  .nav {{ margin-bottom: 20px; font-size: 0.85rem; }}
  .entry {{ background: #1e2330; border-radius: 12px; padding: 18px 20px; margin-bottom: 14px; }}
  .entry-meta {{ display: flex; align-items: center; gap: 10px; margin-bottom: 10px; flex-wrap: wrap; }}
  .badge {{ background: #1a2e1a; color: #86efac; font-size: 0.72rem; font-weight: 700;
            padding: 2px 8px; border-radius: 4px; }}
  .date {{ font-size: 0.75rem; color: #475569; }}
  .lesson-title {{ font-size: 0.8rem; color: #64748b; font-style: italic; }}
  h3 {{ font-size: 1rem; font-weight: 700; color: #c4b5fd; margin-bottom: 8px; }}
  p {{ font-size: 0.9rem; line-height: 1.8; color: #94a3b8; }}
</style>
</head>
<body>
<header>
  <h1>&#x1F50D; Additional Learning</h1>
  <div class="sub">Emerging topics &amp; beyond-curriculum insights · {len(additional_items)} entries</div>
</header>
<div class="nav"><a href="index.html">&#x2190; Back to Curriculum</a></div>
{items_html}
</body>
</html>""")
    print("additional-learning.html rebuilt.")
else:
    print("No additional learning content yet.")

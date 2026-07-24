"""Run the lesson pipeline using a pre-generated JSON lesson file (no API call)."""
import json
import os
import re
import urllib.request
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

LESSON_JSON_PATH = os.environ["LESSON_JSON_PATH"]

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

topic_title = topic_item["title"]
module_name = module["name"]
topic_id = topic_item["id"]
done_count, total_count = curriculum_progress()

print(f"Module {topic_id}: {topic_title}")

with open(LESSON_JSON_PATH, encoding="utf-8") as f:
    lesson = json.load(f)

print("Using pre-generated lesson JSON (OpenRouter unavailable)")

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

# Rebuild index
import importlib.util, sys as _sys
_spec = importlib.util.spec_from_file_location("rebuild_index", "rebuild_index.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

print(f"Lesson saved: {html_path} — {topic}")

mark_done(topic_id)
print(f"Curriculum progress: {done_count + 1}/{total_count}")
import subprocess as _sp
_sp.run(["git", "add", "curriculum.json"], cwd=str(curriculum_path.parent.resolve()), check=False)

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

import json
import os
import re
import time
import urllib.request
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from openai import OpenAI

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

def module_progress_str():
    lines = []
    for m in curriculum["modules"]:
        done = sum(1 for t in m["topics"] if t["done"])
        total = len(m["topics"])
        bar = "▓" * done + "░" * (total - done)
        lines.append(f"M{m['id']} {m['name']}: {bar} {done}/{total}")
    return "\n".join(lines)

module, topic_item = next_topic()
if topic_item is None:
    print("🎉 Curriculum complete!")
    exit(0)

topic_title = topic_item["title"]
module_name = module["name"]
topic_id = topic_item["id"]
done_count, total_count = curriculum_progress()

print(f"Module {topic_id}: {topic_title}")

# ── Generate lesson ───────────────────────────────────────────────────────────
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

prompt = f"""You are an expert semiconductor test engineer with 20+ years of experience in HBM testing, ATE systems, and advanced packaging. Write a daily technical lesson for senior test engineers.

Today's assigned topic (Module {topic_id} — {module_name}):
{topic_title}

Write a focused, technically precise lesson specifically on this topic. Also include one short "additional learning" item — a recent development, emerging technique, or closely related topic beyond the curriculum that a senior engineer should be aware of.

Respond ONLY with a JSON object — no markdown fences, no extra text:
{{
  "topic": "Short topic title under 60 chars",
  "summary": "One sentence for Telegram under 150 chars",
  "sections": [
    {{"title": "Section heading", "content": "HTML body using <p>, <ul>, <li>, <code>, <strong>"}}
  ],
  "key_takeaways": ["takeaway 1", "takeaway 2", "takeaway 3"],
  "references": [
    {{"title": "Reference title", "type": "JEDEC|IEEE|Book|Paper|Datasheet|Web", "detail": "e.g. JESD235C section 4.2, or author/year, or URL"}}
  ],
  "additional_learning": {{
    "title": "Short title under 60 chars",
    "content": "2-3 sentences on a related emerging topic or technique not covered in the main lesson."
  }}
}}

Write 4-5 sections. Include 3-6 real, specific references (JEDEC standards, IEEE papers, vendor datasheets, textbooks). Be technically precise — register names, timing specs, JEDEC references, real equipment behaviour. No fluff."""

models = [
    "openai/gpt-oss-120b:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-27b-it:free",
]
raw = None
for model_id in models:
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
        )
        raw = response.choices[0].message.content.strip()
        print(f"Used model: {model_id}")
        break
    except Exception as e:
        print(f"Model {model_id} failed: {e}, trying next...")
        time.sleep(5)

if raw is None:
    raise RuntimeError("All models failed")
if raw.startswith("```"):
    raw = raw.split("```")[1]
    if raw.startswith("json"):
        raw = raw[4:]
raw = raw.strip()

def fix_json_escapes(s):
    return re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', s)

try:
    lesson = json.loads(raw)
except json.JSONDecodeError:
    lesson = json.loads(fix_json_escapes(raw))

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
    md_lines.append(f"\n## 🔍 Additional Learning: {additional['title']}\n")
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
        f'<h2>🔍 Additional Learning</h2>'
        f'<h3>{additional["title"]}</h3>'
        f'<p>{additional["content"]}</p>'
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
  .additional {{ background: #1a1f2e; border-left: 3px solid #a78bfa; border-radius: 0 10px 10px 0;
                  padding: 18px 22px; margin-bottom: 14px; }}
  .additional h2 {{ color: #a78bfa; font-size: 0.78rem; font-weight: 700; text-transform: uppercase;
                    letter-spacing: .08em; margin-bottom: 8px; }}
  .additional h3 {{ color: #c4b5fd; font-size: 1rem; font-weight: 700; margin-bottom: 10px; }}
  .additional p {{ color: #94a3b8; font-size: 1rem; line-height: 1.8; }}
  .nav {{ margin-top: 24px; font-size: 0.82rem; }}
  .nav a {{ color: #60a5fa; text-decoration: none; }}
  .nav a:hover {{ text-decoration: underline; }}
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
<div class="nav"><a href="../index.html">← All lessons</a></div>
</body>
</html>"""

html_path = os.path.join(lesson_dir, f"{base_name}.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

# ── Rebuild index (grouped by module) ────────────────────────────────────────
def parse_lesson_meta(fname):
    """Return (title, module_id, module_name, date_str) from a lesson md file."""
    md_path = os.path.join(lesson_dir, fname.replace(".html", ".md"))
    if not os.path.exists(md_path):
        return fname.replace(".html", ""), None, None, fname[:10]
    with open(md_path, encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines()[:4]]
    title = lines[0].lstrip("# ") if lines else fname
    date_s = lines[1].strip("*") if len(lines) > 1 else fname[:10]
    mod_line = lines[2].strip("*") if len(lines) > 2 else ""
    if mod_line.startswith("Module "):
        parts = mod_line.split(" — ", 1)
        mod_id = parts[0].replace("Module ", "").strip()
        mod_name = parts[1] if len(parts) > 1 else ""
    else:
        mod_id, mod_name = None, None
    return title, mod_id, mod_name, date_s

all_html = sorted([f for f in os.listdir(lesson_dir) if f.endswith(".html")])

# Group lessons: keyed by (module_num_float, module_name) or None for pre-curriculum
grouped_lessons = {}  # key: (sort_key, label) → list of (date, title, fname)
for fname in all_html:
    title, mod_id, mod_name, date_s = parse_lesson_meta(fname)
    if mod_id:
        try:
            sort_key = float(mod_id.split(".")[0])
        except ValueError:
            sort_key = 99
        key = (sort_key, f"M{mod_id} — {mod_name}")
    else:
        key = (-1, "Pre-Curriculum")
    grouped_lessons.setdefault(key, []).append((date_s, title, fname))

sections_html_idx = ""
for (sort_key, label) in sorted(grouped_lessons.keys()):
    entries = sorted(grouped_lessons[(sort_key, label)])
    items = "".join(
        f'<li><span class="lesson-date">{d}</span> <a href="daily-lessons/{fn}">{t}</a></li>\n'
        for d, t, fn in entries
    )
    header_color = "#64748b" if sort_key == -1 else "#93c5fd"
    sections_html_idx += f'<div class="module-section"><h2 style="color:{header_color}">{label}</h2><ul>{items}</ul></div>\n'

with open("index.html", "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Daily Semiconductor Learning</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         background: #0f1117; color: #e2e8f0; padding: 20px; max-width: 680px; margin: 0 auto; }}
  h1 {{ font-size: 1.3rem; font-weight: 700; color: #f8fafc; margin-bottom: 6px; }}
  .sub {{ color: #64748b; font-size: 0.85rem; margin-bottom: 8px; }}
  .nav-links {{ margin-bottom: 24px; font-size: 0.85rem; }}
  .nav-links a {{ color: #60a5fa; text-decoration: none; margin-right: 16px; }}
  .module-section {{ margin-bottom: 28px; }}
  .module-section h2 {{ font-size: 0.85rem; font-weight: 700; text-transform: uppercase;
                        letter-spacing: .06em; margin-bottom: 10px; }}
  ul {{ list-style: none; background: #1e2330; border-radius: 10px; overflow: hidden; }}
  li {{ padding: 10px 14px; border-bottom: 1px solid #0f172a; display: flex; align-items: baseline; gap: 10px; }}
  li:last-child {{ border-bottom: none; }}
  .lesson-date {{ font-size: 0.75rem; color: #475569; white-space: nowrap; min-width: 80px; }}
  a {{ color: #60a5fa; text-decoration: none; font-size: 0.9rem; }}
  a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
  <h1>📚 Daily Semiconductor Learning</h1>
  <div class="sub">HBM Testing · Senior Engineer Level</div>
  <div class="nav-links"><a href="curriculum.html">📋 Curriculum</a></div>
  {sections_html_idx}
</body>
</html>""")

# ── Rebuild curriculum page ───────────────────────────────────────────────────
# Build a lookup: lesson file slug → html filename (most recent per topic)
lesson_file_map = {}
for fname in sorted(os.listdir(lesson_dir)):
    if fname.endswith(".html"):
        lesson_file_map[fname] = fname

# Build curriculum HTML
modules_html = ""
for m in curriculum["modules"]:
    done_count_m = sum(1 for t in m["topics"] if t["done"])
    total_m = len(m["topics"])
    bar = "▓" * done_count_m + "░" * (total_m - done_count_m)
    topics_html = ""
    for t in m["topics"]:
        # Find matching lesson file by scanning md files for matching topic
        lesson_link = ""
        for fname in sorted(os.listdir(lesson_dir), reverse=True):
            if fname.endswith(".md"):
                md_p = os.path.join(lesson_dir, fname)
                with open(md_p, encoding="utf-8") as mf:
                    first_line = mf.readline().strip().lstrip("# ")
                # loose match on first few words
                topic_words = t["title"].split(" — ")[0].lower().split()[:4]
                if all(w in first_line.lower() for w in topic_words):
                    html_fname = fname.replace(".md", ".html")
                    lesson_link = f'href="daily-lessons/{html_fname}"'
                    break
        status = "✅" if t["done"] else "○"
        link_open = f'<a {lesson_link}>' if lesson_link else '<span>'
        link_close = '</a>' if lesson_link else '</span>'
        short_title = t["title"].split(" — ")[0]
        topics_html += f'<li class="{"done" if t["done"] else "pending"}">{status} {link_open}{short_title}{link_close}</li>\n'

    modules_html += f"""
<div class="module" id="module-{m['id']}">
  <div class="module-header">
    <span class="module-num">M{m['id']}</span>
    <span class="module-name">{m['name']}</span>
    <span class="module-bar">{bar} {done_count_m}/{total_m}</span>
  </div>
  <ul class="topics">{topics_html}</ul>
</div>"""

total_topics = sum(len(m["topics"]) for m in curriculum["modules"])
done_topics = sum(1 for m in curriculum["modules"] for t in m["topics"] if t["done"])

with open("curriculum.html", "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HBM Learning Curriculum</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         background: #0f1117; color: #e2e8f0; padding: 20px; max-width: 720px; margin: 0 auto; }}
  h1 {{ font-size: 1.4rem; font-weight: 700; color: #f8fafc; margin-bottom: 4px; }}
  .sub {{ color: #64748b; font-size: 0.85rem; margin-bottom: 6px; }}
  .progress {{ font-size: 0.9rem; color: #86efac; margin-bottom: 24px; }}
  .nav {{ font-size: 0.85rem; margin-bottom: 20px; }}
  .nav a {{ color: #60a5fa; text-decoration: none; }}
  .module {{ background: #1e2330; border-radius: 12px; padding: 18px 20px; margin-bottom: 14px; }}
  .module-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }}
  .module-num {{ background: #1e3a5f; color: #60a5fa; font-size: 0.75rem; font-weight: 700;
                 padding: 2px 8px; border-radius: 4px; }}
  .module-name {{ font-weight: 700; color: #f1f5f9; font-size: 1rem; flex: 1; }}
  .module-bar {{ font-size: 0.8rem; color: #64748b; font-family: monospace; }}
  .topics {{ list-style: none; padding-left: 4px; }}
  .topics li {{ padding: 6px 0; border-bottom: 1px solid #0f172a; font-size: 0.9rem; color: #94a3b8; }}
  .topics li:last-child {{ border-bottom: none; }}
  .topics li.done {{ color: #cbd5e1; }}
  .topics a {{ color: #60a5fa; text-decoration: none; }}
  .topics a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
  <h1>📋 HBM Learning Curriculum</h1>
  <div class="sub">Senior Test Engineer Level · 6 Modules · {total_topics} Topics</div>
  <div class="progress">Progress: {done_topics}/{total_topics} topics completed</div>
  <div class="nav"><a href="index.html">← All Lessons</a></div>
  {modules_html}
</body>
</html>""")

print(f"Lesson saved: {html_path} — {topic}")

# ── Mark curriculum done ──────────────────────────────────────────────────────
mark_done(topic_id)
print(f"Curriculum progress: {done_count + 1}/{total_count}")

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
        f"[Curriculum]({base_url}/curriculum.html#module-{module['id']})"
        + (f"\n\n🔍 *Additional Learning*\n_{additional['title']}_\n{additional['content']}" if additional else "")
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

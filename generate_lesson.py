import json
import os
import urllib.request
from datetime import date, datetime
from zoneinfo import ZoneInfo
from openai import OpenAI

today = date.today().isoformat()
now_et = datetime.now(ZoneInfo("America/New_York"))
date_str = now_et.strftime("%A, %b %d %Y")
lesson_dir = "daily-lessons"
os.makedirs(lesson_dir, exist_ok=True)

# Collect recent topics to avoid repeats
recent_topics = []
for fname in sorted(os.listdir(lesson_dir), reverse=True)[:10]:
    if fname.endswith(".md"):
        with open(os.path.join(lesson_dir, fname)) as f:
            recent_topics.append(f.readline().strip().lstrip("# "))

recent_str = "\n".join(f"- {t}" for t in recent_topics) if recent_topics else "None yet"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

prompt = f"""You are an expert semiconductor test engineer with 20+ years of experience in HBM testing, ATE systems, and advanced packaging. Write a daily technical lesson for senior test engineers.

Recent topics covered (do NOT repeat):
{recent_str}

Pick a fresh, specific HBM testing topic. Examples:
- HBM PHY interface testing strategies
- JEDEC JESD235 compliance testing details
- HBM2e vs HBM3 electrical test differences
- Pseudo-channel mode test patterns
- TSV continuity testing in HBM stacks
- DFT approaches for HBM in 2.5D packages
- Temperature-aware HBM parametric testing
- HBM repair flow and post-repair verification
- Interposer probe challenges for HBM
- HBM MBIST implementation and coverage

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
  ]
}}

Write 4-5 sections. Include 3-6 real, specific references (JEDEC standards, IEEE papers, vendor datasheets, textbooks). Be technically precise — register names, timing specs, JEDEC references, real equipment behaviour. No fluff."""

import time
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
lesson = json.loads(raw.strip())

topic = lesson["topic"]
summary = lesson["summary"]
sections = lesson["sections"]
takeaways = lesson["key_takeaways"]
references = lesson.get("references", [])

import re
slug = re.sub(r'[^a-z0-9]+', '-', topic.lower()).strip('-')[:60]
base_name = f"{today}-{slug}"

# Markdown
md_lines = [f"# {topic}\n", f"*{date_str}*\n"]
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

md_path = os.path.join(lesson_dir, f"{base_name}.md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines) + "\n")

# HTML
sections_html = "".join(
    f'<div class="section"><h2>{s["title"]}</h2>{s["content"]}</div>\n'
    for s in sections
)
takeaways_html = "".join(f"<li>{t}</li>" for t in takeaways)

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
  h1 {{ font-size: 1.4rem; font-weight: 700; color: #f8fafc; line-height: 1.4; margin-bottom: 6px; }}
  .meta {{ font-size: 0.82rem; color: #64748b; margin-top: 6px; }}
  .badge {{ display: inline-block; background: #1e3a5f; color: #60a5fa;
            font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 4px;
            letter-spacing: .05em; text-transform: uppercase; margin-right: 8px; }}
  .section {{ background: #1e2330; border-radius: 12px; padding: 18px 20px; margin-bottom: 14px; }}
  h2 {{ font-size: 1rem; font-weight: 700; color: #93c5fd; margin-bottom: 12px; }}
  p {{ font-size: 0.9rem; line-height: 1.7; color: #cbd5e1; margin-bottom: 10px; }}
  ul {{ padding-left: 18px; margin-bottom: 10px; }}
  li {{ font-size: 0.9rem; line-height: 1.7; color: #cbd5e1; margin-bottom: 4px; }}
  code {{ background: #0f172a; color: #a5f3fc; padding: 1px 5px; border-radius: 4px;
          font-size: 0.85em; font-family: 'SF Mono', Consolas, monospace; }}
  strong {{ color: #f1f5f9; }}
  .takeaways {{ background: #162032; border-left: 3px solid #3b82f6;
                border-radius: 0 10px 10px 0; padding: 16px 20px; margin-bottom: 14px; }}
  .takeaways h2 {{ color: #60a5fa; margin-bottom: 10px; }}
  .takeaways li {{ color: #94a3b8; }}
  .references {{ background: #1e2330; border-radius: 12px; padding: 18px 20px; margin-bottom: 14px; }}
  .references h2 {{ font-size: 1rem; font-weight: 700; color: #93c5fd; margin-bottom: 12px; }}
  .ref-item {{ display: flex; gap: 10px; align-items: baseline; padding: 6px 0;
               border-bottom: 1px solid #0f172a; font-size: 0.85rem; }}
  .ref-item:last-child {{ border-bottom: none; }}
  .ref-type {{ flex-shrink: 0; background: #0f172a; color: #7dd3fc; font-size: 0.7rem;
               font-weight: 700; padding: 1px 6px; border-radius: 4px; letter-spacing: .04em; }}
  .ref-title {{ color: #e2e8f0; font-weight: 600; }}
  .ref-detail {{ color: #64748b; font-size: 0.8rem; }}
  .nav {{ margin-top: 24px; font-size: 0.82rem; }}
  .nav a {{ color: #60a5fa; text-decoration: none; }}
  .nav a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<header>
  <div><span class="badge">HBM Testing</span><span class="badge">Senior Level</span></div>
  <h1>{topic}</h1>
  <div class="meta">{date_str}</div>
</header>
{sections_html}
<div class="takeaways">
  <h2>⚡ Key Takeaways</h2>
  <ul>{takeaways_html}</ul>
</div>
{references_html}
<div class="nav"><a href="../index.html">← All lessons</a></div>
</body>
</html>"""

html_path = os.path.join(lesson_dir, f"{base_name}.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

# Rebuild index.html
all_lessons = sorted([f for f in os.listdir(lesson_dir) if f.endswith(".html")], reverse=True)
lesson_links = ""
for fname in all_lessons:
    d = fname.replace(".html", "")
    title_line = d
    md_fpath = os.path.join(lesson_dir, fname.replace(".html", ".md"))
    if os.path.exists(md_fpath):
        with open(md_fpath) as f2:
            title_line = f2.readline().strip().lstrip("# ")
    lesson_links += f'<li><a href="daily-lessons/{fname}">{d} — {title_line}</a></li>\n'

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
  .sub {{ color: #64748b; font-size: 0.85rem; margin-bottom: 24px; }}
  ul {{ list-style: none; }}
  li {{ padding: 12px 0; border-bottom: 1px solid #1e2330; font-size: 0.9rem; }}
  li:last-child {{ border-bottom: none; }}
  a {{ color: #60a5fa; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
  <h1>📚 Daily Semiconductor Learning</h1>
  <div class="sub">HBM Testing · Senior Engineer Level</div>
  <ul>{lesson_links}</ul>
</body>
</html>""")

print(f"Lesson saved: {html_path} — {topic}")

# Telegram
tg_token = os.environ.get("TELEGRAM_TOKEN")
tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
if tg_token and tg_chat_id:
    msg = (f"📚 *Daily Lesson — {today}*\n\n*{topic}*\n\n{summary}\n\n"
           f"[Read full lesson](https://allie0132.github.io/daily-semiconductor-learning/daily-lessons/{base_name}.html)")
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

"""
One-time script: send a summary of all lessons learned before the structured
curriculum begins, grouped by curriculum module.
"""
import json
import os
import sys
import io
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

tg_token = os.environ.get("TELEGRAM_TOKEN")
tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

with open("curriculum.json", encoding="utf-8") as f:
    curriculum = json.load(f)

lesson_dir = Path("daily-lessons")
lessons = []
for fname in sorted(lesson_dir.glob("*.md")):
    with open(fname, encoding="utf-8") as f:
        title = f.readline().strip().lstrip("# ")
    lessons.append(title)

total = sum(len(m["topics"]) for m in curriculum["modules"])
done = sum(1 for m in curriculum["modules"] for t in m["topics"] if t["done"])

lines = [
    "📚 *HBM Learning — Pre-Curriculum Summary*\n",
    f"You've completed *{len(lessons)} lessons* before starting the structured curriculum.",
    f"These map to *{done}/{total}* curriculum topics across 3 modules.\n",
]

# Show covered topics grouped by module
for m in curriculum["modules"]:
    covered = [t for t in m["topics"] if t["done"]]
    if covered:
        lines.append(f"*M{m['id']} {m['name']}*")
        for t in covered:
            lines.append(f"  ✅ {t['title'].split(' — ')[0]}")
        lines.append("")

lines.append("─────────────────")
lines.append("*Starting from Module 1 — Foundations tomorrow.*")
lines.append("Each daily lesson follows the curriculum in order.")

msg = "\n".join(lines)

if tg_token and tg_chat_id:
    payload = json.dumps({"chat_id": tg_chat_id, "text": msg, "parse_mode": "Markdown"}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{tg_token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req)
    print("Summary sent to Telegram.")
else:
    print(msg)

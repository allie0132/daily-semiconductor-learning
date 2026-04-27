"""One-time script: updates font sizes in all existing lesson HTML files."""
import os, re

lesson_dir = "daily-lessons"
replacements = [
    (r'font-size: 1\.4rem;(\s*font-weight: 700; color: #f8fafc)', r'font-size: 1.6rem;\1'),
    (r'(\.meta \{[^}]*?)font-size: 0\.82rem;', r'\1font-size: 0.9rem;'),
    (r'(\.badge \{[^}]*?)font-size: 0\.72rem;', r'\1font-size: 0.78rem;'),
    (r'(h2 \{[^}]*?)font-size: 1rem;', r'\1font-size: 1.15rem;'),
    (r'(\.references h2 \{[^}]*?)font-size: 1rem;', r'\1font-size: 1.15rem;'),
    (r'(\bp \{[^}]*?)font-size: 0\.9rem;', r'\1font-size: 1.05rem;'),
    (r'(\bli \{[^}]*?)font-size: 0\.9rem;', r'\1font-size: 1.05rem;'),
    (r'(code \{[^}]*?)font-size: 0\.85em;', r'\1font-size: 0.95em;'),
    (r'(\.ref-item \{[^}]*?)font-size: 0\.85rem;', r'\1font-size: 1rem;'),
    (r'(\.ref-type \{[^}]*?)font-size: 0\.7rem;', r'\1font-size: 0.75rem;'),
    (r'(\.ref-detail \{[^}]*?)font-size: 0\.8rem;', r'\1font-size: 0.9rem;'),
    # padding updates
    (r'(\.section \{[^}]*?)padding: 18px 20px;', r'\1padding: 20px 22px;'),
    (r'(\.takeaways \{[^}]*?)padding: 16px 20px;', r'\1padding: 18px 22px;'),
    (r'(\.references \{[^}]*?)padding: 18px 20px;', r'\1padding: 18px 22px;'),
]

updated = 0
for fname in os.listdir(lesson_dir):
    if not fname.endswith(".html"):
        continue
    path = os.path.join(lesson_dir, fname)
    with open(path, encoding="utf-8") as f:
        content = f.read()
    new_content = content
    for pattern, repl in replacements:
        new_content = re.sub(pattern, repl, new_content, flags=re.DOTALL)
    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated: {fname}")
        updated += 1
    else:
        print(f"No change: {fname}")

print(f"\nDone — {updated} file(s) updated.")

"""Inject today's pre-generated lesson for topic 11.3."""
import json, os, re, urllib.request
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
        for t in module["topics"]:
            if not t["done"]:
                return module, t
    return None, None

def mark_done(topic_id):
    for module in curriculum["modules"]:
        for t in module["topics"]:
            if t["id"] == topic_id:
                t["done"] = True
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

topic_id = topic_item["id"]
module_name = module["name"]
done_count, total_count = curriculum_progress()
print(f"Module {topic_id}: {topic_item['title']}")

# ── Lesson content (generated) ────────────────────────────────────────────────
lesson = {
    "topic": "Predictive Yield Modeling via Wafer Map Correlation",
    "summary": "Correlate inline metrology maps (CMP, overlay, CD) to ATE sort results using regression to predict yield before wafer sort.",
    "sections": [
        {
            "title": "Inline Metrology as Yield Predictors",
            "content": (
                "<p>Inline metrology captures process state at intermediate fabrication steps before electrical test is possible. "
                "Key measurement types used in yield prediction include:</p>"
                "<ul>"
                "<li><strong>CMP uniformity maps</strong>: post-planarization thickness variation (WIWNU), measured by ellipsometry or "
                "reflectometry at 49-121 sites per wafer. Thickness non-uniformity directly impacts resistance and RC delay across die.</li>"
                "<li><strong>Overlay error maps</strong>: lithographic misalignment between layers measured in nm by optical overlay "
                "metrology (e.g., ASML Atlas-H). Overlay &gt;20% of critical dimension budget causes systematic pattern failures.</li>"
                "<li><strong>Critical dimension (CD) maps</strong>: gate or via width variation from CD-SEM or optical CD (OCD) tools. "
                "CD variation shifts Vt distributions and drives leakage spread.</li>"
                "<li><strong>Defect density maps</strong>: particle and scratch counts from inspection tools (KLA-Tencor Surfscan, "
                "KLARF output). Spatial clustering reveals tool-specific signatures.</li>"
                "</ul>"
                "<p>Each measurement type produces a spatial map across the 300 mm wafer. The regression target is the final wafer "
                "sort map from ATE: which dies pass, and at what parametric margin (e.g., Vmin, IDDQ, maximum test frequency).</p>"
            )
        },
        {
            "title": "Wafer Map Registration and Feature Matrix Construction",
            "content": (
                "<p>Before regression can be applied, inline measurement grids must be registered to the die grid from the probe "
                "card layout. Critical alignment steps:</p>"
                "<ul>"
                "<li><strong>Coordinate system alignment</strong>: wafer notch angle and map origin from SEMI M1 must match the "
                "ATE wafer map coordinate system (SEMI G85 format). A rotation or flip error misregisters all die-to-metrology "
                "assignments.</li>"
                "<li><strong>Sparse-to-dense interpolation</strong>: inline tools measure at 13, 49, or 121 sites per wafer, "
                "far fewer than the 500-2000 die on a 300 mm wafer. Spatial interpolation (bilinear, RBF, or kriging) expands "
                "the measurement grid to die resolution before feature extraction.</li>"
                "<li><strong>Multi-layer temporal stacking</strong>: overlay from lithography step N must be paired with CMP "
                "uniformity from step N-2 using lot/wafer/timestamp metadata from the MES. Mismatched layers corrupt the "
                "feature matrix.</li>"
                "</ul>"
                "<p>The result is a per-die feature matrix <code>X[die, feature]</code> where each column is an interpolated "
                "inline measurement, and the target vector <code>y[die]</code> is binary (pass/fail) or continuous "
                "(e.g., <code>IDDQ</code> or Vmin in mV). Typical feature counts range from 10 to several hundred parameters "
                "across all process steps.</p>"
            )
        },
        {
            "title": "Regression Model Selection and Training",
            "content": (
                "<p>For binary yield (pass/fail), <strong>logistic regression</strong> is the baseline; for continuous parametric "
                "prediction (Vmin, leakage), ordinary least squares (OLS) or regularized variants are used.</p>"
                "<ul>"
                "<li><strong>Ordinary Least Squares (OLS)</strong>: <code>y = X&#946; + &#949;</code>. Simple and interpretable "
                "but sensitive to multicollinearity when inline features are correlated (e.g., CMP thickness and overlay "
                "error often share spatial pattern). R-squared and adjusted R-squared are standard fit metrics.</li>"
                "<li><strong>Ridge Regression (L2)</strong>: adds penalty <code>&#955;||&#946;||&#178;</code> to the loss, "
                "shrinking correlated feature coefficients. Lambda is selected by k-fold cross-validation (typically k=5 or 10). "
                "Preferred when feature count exceeds ~20 or features are strongly correlated.</li>"
                "<li><strong>Lasso Regression (L1)</strong>: penalty <code>&#955;||&#946;||&#8321;</code> drives sparse "
                "solutions, automatically zeroing non-predictive features. Valuable for automatic feature selection from "
                "hundreds of inline parameters.</li>"
                "<li><strong>Elastic Net</strong>: linear combination of L1 and L2 penalties, controlled by mixing parameter "
                "<code>&#945;</code>. Best general choice when both feature selection and collinearity management are needed.</li>"
                "</ul>"
                "<p>For non-linear yield surfaces near systematic defect clusters, ensemble methods (XGBoost, LightGBM, random "
                "forests) capture interaction effects missed by linear models at the cost of interpretability.</p>"
            )
        },
        {
            "title": "Model Evaluation Metrics for Yield Prediction",
            "content": (
                "<p>Models must be evaluated on held-out lots — never the training lot — to measure genuine predictive power. "
                "Key metrics in production use:</p>"
                "<ul>"
                "<li><strong>AUC-ROC</strong>: for binary pass/fail prediction. AUC &gt; 0.80 is a practical threshold for "
                "production-quality yield prediction. Compute per wafer, then report mean ± std across a validation lot set.</li>"
                "<li><strong>R&#178; (coefficient of determination)</strong>: fraction of parametric variance explained. "
                "R&#178; &gt; 0.7 indicates useful predictive power for continuous targets such as IDDQ or Vmin.</li>"
                "<li><strong>Lot-level yield correlation (&#961;)</strong>: Pearson or Spearman correlation between predicted "
                "and actual die yield, reported at lot level to smooth within-wafer noise. This is the metric most relevant "
                "to production disposition decisions.</li>"
                "<li><strong>Spatial residual map</strong>: <code>y_actual - y_predicted</code> plotted as a wafer map. "
                "A good model leaves no systematic spatial pattern in residuals. Concentric ring or edge-heavy residuals "
                "indicate an unmodeled CMP or etch non-uniformity effect.</li>"
                "</ul>"
                "<p>Production deployment typically uses a prediction interval rather than a point estimate. If predicted "
                "lot yield falls below a control limit (e.g., mean - 2&#963;), the lot is flagged for engineering disposition "
                "before reaching probe, enabling early scrap or rework decisions.</p>"
            )
        },
        {
            "title": "Closed-Loop Yield Learning and Model Maintenance",
            "content": (
                "<p>Predictive yield models degrade over time as process tools drift, consumables are replaced, or process "
                "recipes are optimized. Production-grade virtual metrology systems require:</p>"
                "<ul>"
                "<li><strong>Drift detection via SPC on residuals</strong>: track prediction residuals (actual - predicted) "
                "using EWMA or Shewhart charts. A shift in residual mean or increase in variance signals process change "
                "requiring model retraining. EWMA with &#955;=0.2 is standard for slowly drifting processes.</li>"
                "<li><strong>Rolling-window retraining</strong>: ATE sort results feed back into the training pipeline via "
                "the MES. A 90-day rolling window is typical in high-volume production; shorter windows (30 days) are used "
                "after process changes or tool PM events.</li>"
                "<li><strong>Confidence scoring via Mahalanobis distance</strong>: lots with feature vectors far from the "
                "training distribution are flagged as low-confidence. Mahalanobis distance D&#178; = (x - &#956;)&#7488; "
                "&#931;&#8315;&#185; (x - &#956;) provides a scalar confidence metric. High-D lots should not be "
                "acted on autonomously without engineering review.</li>"
                "<li><strong>Concept drift vs. data drift</strong>: data drift (new tool with different absolute offset) "
                "is handled by feature normalization or recalibration. Concept drift (yield-metrology relationship changes "
                "after process optimization) requires full model retraining or domain adaptation techniques.</li>"
                "</ul>"
                "<p>The long-term goal is <strong>virtual metrology</strong>: predicting electrical yield at fab completion "
                "or after key inline steps, enabling early disposition and reducing cost-per-wafer at sort.</p>"
            )
        }
    ],
    "key_takeaways": [
        "Inline metrology maps (CMP, overlay, CD) must be registered to die-grid coordinates and spatially interpolated to die resolution before regression modeling.",
        "Ridge or Lasso regression is preferred over OLS for yield prediction due to multicollinearity; Lasso additionally performs automatic feature selection.",
        "Model quality is evaluated by AUC-ROC (binary pass/fail) or R-squared (continuous), with spatial residual maps used to detect unmodeled systematic effects.",
        "Production models require EWMA-based drift monitoring and rolling retraining; Mahalanobis distance identifies out-of-distribution lots that should not be automatically dispositioned."
    ],
    "references": [
        {
            "title": "SEMI M1: Specification for Polished Single Crystal Silicon Wafers",
            "type": "JEDEC",
            "detail": "SEMI M1 standard defining wafer flat/notch and coordinate system for 300 mm wafers — establishes map orientation used in metrology-to-die registration"
        },
        {
            "title": "SEMI G85: ASCII Format for Semiconductor Die Results",
            "type": "JEDEC",
            "detail": "Standard defining the wafer map interchange format used by ATE and MES for sort results; wafer bin map format for die-level pass/fail data"
        },
        {
            "title": "Virtual Metrology for Semiconductor Manufacturing: A Review",
            "type": "Paper",
            "detail": "Hung-En Tseng et al., IEEE Trans. Semiconductor Manufacturing, vol. 25, no. 1, pp. 132-144, 2012 — comprehensive review of VM regression methods and industrial deployment"
        },
        {
            "title": "The Elements of Statistical Learning",
            "type": "Book",
            "detail": "Hastie, Tibshirani, Friedman — Chapter 3 (Linear Methods for Regression) and Chapter 18 (High-Dimensional Problems); 2nd ed., Springer, 2009"
        },
        {
            "title": "KLA KLARF 1.8 File Format Specification",
            "type": "Datasheet",
            "detail": "KLA-Tencor KLARF (KLA Results File) v1.8 format documentation for defect map interchange between inspection tools and downstream analysis — key for defect density feature extraction"
        },
        {
            "title": "Yield Prediction Using Inline Parametric Data in Semiconductor Manufacturing",
            "type": "Paper",
            "detail": "L. Pelegrini et al., IEEE Trans. Semiconductor Manufacturing, vol. 20, no. 4, pp. 391-400, 2007 — case study of logistic regression for sort yield prediction from inline data"
        }
    ],
    "additional_learning": {
        "title": "Kriging Interpolation for Sparse Metrology Upsampling",
        "content": (
            "When inline metrology provides only 49 or 121 measurement sites across a 300 mm wafer but die count is 500-2000, "
            "interpolation quality directly impacts regression accuracy. Ordinary kriging — which models the spatial covariance "
            "structure (variogram) of the metrology field — outperforms bilinear interpolation for CMP thickness maps because it "
            "accounts for anisotropic spatial correlation, such as radial polish patterns from the CMP head rotation. "
            "The variogram fitting step estimates the nugget (measurement noise floor), sill (total process variance), and range "
            "(spatial correlation length) from the available measurement points; these parameters drive Best Linear Unbiased "
            "Prediction (BLUP) estimates at unsampled die locations. Kriging standard errors can also be used as per-die "
            "uncertainty weights when training the downstream regression model, down-weighting die whose interpolated feature "
            "values are less certain."
        )
    }
}

# ── File generation ───────────────────────────────────────────────────────────
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
    # Strip remaining HTML tags for markdown
    content = re.sub(r'<[^>]+>', '', content)
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
print(f"MD saved: {md_path}")

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
print(f"HTML saved: {html_path}")

# ── Rebuild curriculum index ──────────────────────────────────────────────────
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
for fname in sorted(os.listdir(lesson_dir)):
    if not fname.endswith(".html"):
        continue
    title, mod_id, date_s = parse_lesson_meta(fname)
    if mod_id:
        topic_lesson_map[mod_id] = (title, fname, date_s)
    else:
        pre_curriculum.append((date_s, title, fname))

total_topics = sum(len(m["topics"]) for m in curriculum["modules"])
done_topics = done_count  # before mark_done so +1 reflects new lesson

modules_sections_html = ""
for m in curriculum["modules"]:
    done_m = sum(1 for t in m["topics"] if t["done"])
    total_m = len(m["topics"])
    pct = int(done_m / total_m * 100)
    topics_html = ""
    for t in m["topics"]:
        info = topic_lesson_map.get(t["id"])
        if info:
            l_title, l_fname, l_date = info
            topics_html += (
                f'<li class="done"><span class="status">&#x2705;</span>'
                f'<span class="topic-info"><a href="daily-lessons/{l_fname}">{l_title}</a>'
                f'<span class="topic-date">{l_date}</span></span></li>\n'
            )
        elif t["done"]:
            short = t["title"].split(" — ")[0]
            topics_html += (
                f'<li class="done"><span class="status">&#x2705;</span>'
                f'<span class="topic-info"><span class="topic-title">{short}</span></span></li>\n'
            )
        else:
            short = t["title"].split(" — ")[0]
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
        f'<span class="module-num dim">PRE</span><span class="module-name">Pre-Curriculum</span>'
        f'<span class="module-prog">{len(pre_curriculum)} lessons</span></div></summary>'
        f'<ul class="topic-list">{items}</ul></details>'
    )

with open("index.html", "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HBM Learning &mdash; All Lessons</title>
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
  details.module summary .module-meta::before {{ content: "&#x25B6;"; font-size: 0.65rem; color: #475569; margin-right: 4px; }}
  details.module[open] summary .module-meta::before {{ content: "&#x25BC;"; }}
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
  <div class="sub">Senior Test Engineer &middot; 6 Modules &middot; {total_topics} Topics</div>
  <div class="overall-prog">Overall progress: {done_topics + 1}/{total_topics} topics completed</div>
  <div class="overall-bar"><div class="overall-bar-fill" style="width:{int((done_topics + 1)/total_topics*100)}%"></div></div>
</header>
{modules_sections_html}
{pre_html}
</body>
</html>""")
print("index.html rebuilt")

# ── Rebuild additional-learning.html via rebuild_index.py ─────────────────────
import importlib.util
_spec = importlib.util.spec_from_file_location("rebuild_index", "rebuild_index.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# ── Mark done and stage curriculum.json ───────────────────────────────────────
mark_done(topic_id)
print(f"Curriculum marked done: {topic_id} — progress now {done_count + 1}/{total_count}")
import subprocess as _sp
_sp.run(["git", "add", "curriculum.json"], check=False)

# ── Telegram ──────────────────────────────────────────────────────────────────
tg_token = os.environ.get("TELEGRAM_TOKEN")
tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
if tg_token and tg_chat_id:
    base_url = "https://allie0132.github.io/daily-semiconductor-learning"
    msg = (
        f"\U0001F4DA *Daily Lesson — {today}*\n"
        f"_Module {topic_id} · {module_name}_\n\n"
        f"*{topic}*\n\n"
        f"{summary}\n\n"
        f"\U0001F4CA Progress: {done_count + 1}/{total_count}\n\n"
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

print(f"Done. Topic: {topic}")

#!/usr/bin/env python3
"""Regenerate README.md's readings table and the root landing page
(index.html) from every reading.meta.json sidecar in the repo. Run this any
time a reading is added/moved/retitled — do not hand-edit the generated
sections.

    python3 build_readme.py

Grouped by each reading's own `topic_area` field (a short human label like
"Command Line & Environment"), not by module folder.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
PAGES_BASE = "https://the-marcy-lab-school.github.io/SWE_Interactive_Readings"
TABLE_START = "<!-- READINGS_TABLE_START -->"
TABLE_END = "<!-- READINGS_TABLE_END -->"


def find_readings():
    readings = []
    for meta_path in ROOT.glob("Mod*/**/reading.meta.json"):
        meta = json.loads(meta_path.read_text())
        rel_dir = meta_path.parent.relative_to(ROOT)
        meta["url"] = f"{PAGES_BASE}/{rel_dir.as_posix()}/"
        meta["rel_dir"] = rel_dir.as_posix()
        readings.append(meta)
    return sorted(readings, key=lambda r: (r.get("rel_dir", "")))


def _escape_md_cell(text):
    # A literal "|" inside a table cell splits it into an extra column for
    # every Markdown renderer (GitHub included) — always escape.
    return str(text).replace("|", "\\|")


def build_readme_table(readings):
    if not readings:
        return "_No readings published yet._"
    lines = ["| Reading | Topic Area | Est. time | Link |",
             "|---|---|---|---|"]
    for r in readings:
        lines.append(
            f"| {_escape_md_cell(r['title'])} | {_escape_md_cell(r.get('topic_area','?'))} | "
            f"{r.get('time_minutes','?')} min | "
            f'<a href="{r["url"]}" target="_blank" rel="noopener noreferrer">Open</a> |'
        )
    return "\n".join(lines)


def update_readme(table_md):
    readme_path = ROOT / "README.md"
    if readme_path.exists():
        content = readme_path.read_text()
    else:
        content = ""
    if not content.strip() or content.strip() == "# SWE_Interactive_Readings":
        content = (
            "# Software Engineering Fellowship — Interactive Readings\n\n"
            "Short (10-15 minute, video included), standalone interactive readings for the "
            "Marcy Lab School Software Engineering Fellowship, hosted on GitHub Pages. "
            "Each one is centered on a real-world use case and teaches one topic directly — "
            "no prerequisite-recall section, no submission flow, just a \"Copy Plain Text "
            "Answers\" button to keep a copy of your responses.\n\n"
            f"{TABLE_START}\n{TABLE_END}\n"
        )
    if TABLE_START not in content:
        content += f"\n\n{TABLE_START}\n{TABLE_END}\n"
    before = content.split(TABLE_START)[0]
    after = content.split(TABLE_END)[1]
    new_content = f"{before}{TABLE_START}\n{table_md}\n{TABLE_END}{after}"
    readme_path.write_text(new_content)


def build_landing_page(readings):
    by_topic = {}
    for r in readings:
        by_topic.setdefault(r.get("topic_area", "Other"), []).append(r)

    sections = []
    for topic, items in by_topic.items():
        cards = "\n".join(
            f'<a class="mlrk-card mlrk-reading-card" href="{r["url"]}">'
            f'<h3>{r["title"]}</h3>'
            f'<p class="mlrk-small">{r.get("time_minutes","?")} min</p>'
            f"</a>"
            for r in items
        )
        sections.append(
            f'<section class="mlrk-section"><h2>{topic}</h2>'
            f'<div class="mlrk-grid">{cards}</div></section>'
        )

    body = "\n".join(sections) if sections else '<p class="mlrk-small">No readings published yet.</p>'

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Software Engineering Fellowship — Readings</title>
<link rel="stylesheet" href="assets/brand-tokens.css">
<link rel="stylesheet" href="assets/reading-kit.css">
<style>.mlrk-reading-card{{text-decoration:none;display:block}}.mlrk-reading-card h3{{color:var(--mlrk-heading-on-light);margin:0 0 .3rem;font-family:var(--mlrk-font-heading)}}</style>
</head><body>
<header class="mlrk-header"><div class="mlrk-wrap">
<div class="mlrk-eyebrow">Software Engineering Fellowship</div>
<h1>Interactive Readings</h1>
<p class="mlrk-lead">Short, standalone readings — 10-15 minutes each, video included. Grouped by topic area below.</p>
</div></header>
<main class="mlrk-main"><div class="mlrk-wrap">
{body}
</div></main>
<footer class="mlrk-footer">This page is the property of The Marcy Lab School and Angelica Spratley. Contact the owners before republishing, reusing, or monetizing this content elsewhere.</footer>
</body></html>
"""
    (ROOT / "index.html").write_text(html)


def main():
    readings = find_readings()
    build_landing_page(readings)
    update_readme(build_readme_table(readings))
    print(f"Built landing page + README table for {len(readings)} reading(s).")


if __name__ == "__main__":
    main()
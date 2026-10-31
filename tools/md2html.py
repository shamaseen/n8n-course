"""Render the markdown labs as styled, offline, bilingual HTML pages.
  class-*/lab/LAB.md  -> class-*/lab/lab.html
Run from course-v2/:  python3 tools/md2html.py   (the .md files stay the source; re-run after editing them)"""
import html, pathlib, re
import markdown

EXT = ["tables", "fenced_code", "sane_lists", "md_in_html", "attr_list"]


def page(md_text, title, depth, cls):
    md_text = re.sub(r"^(\s*)[-*] \[ \] ", r"\1- ☐ ", md_text, flags=re.M)        # task lists
    md_text = re.sub(r"^(\s*)[-*] \[[xX]\] ", r"\1- ☑ ", md_text, flags=re.M)
    md_text = re.sub(r"<details>", '<details markdown="1">', md_text)          # markdown inside <details>
    body = markdown.markdown(md_text, extensions=EXT)
    up = "../" * depth
    links = (f'<a href="{up}../index.html">🏠 الصفحة الرئيسية · Course home</a>'
             f'<a href="{up}deck.html">🎞️ العرض · Slides</a>'
             f'<a href="{up}handout.pdf">📄 الملخّص · Handout</a>')
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · n8n من الصفر</title>
<link rel="stylesheet" href="{up}../assets/course.css">
</head><body class="doc"><div class="wrap">
<nav class="crumbs">{links}</nav><div class="band"></div>
<article>
{body}
</article>
<p class="foot">n8n من الصفر · {cls}</p>
</div></body></html>
"""


for cls in sorted(pathlib.Path(".").glob("class-*")):
    for src, dst, depth in [(cls / "lab/LAB.md", cls / "lab/lab.html", 1)]:
        if not src.exists():
            continue
        text = src.read_text()
        title = re.search(r"^#\s+(.+)$", text, re.M)
        title = re.sub(r"[`*]", "", title[1]) if title else src.stem
        dst.write_text(page(text, title, depth, cls.name))
        print(f"{src} -> {dst}")

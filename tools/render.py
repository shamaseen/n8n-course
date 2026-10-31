"""render.py <deck.html> <out-dir> — one PNG per slide (1920x1080) using system Chrome.
Also reports overflow: elements whose box leaves the 1920x1080 slide canvas."""
import sys, pathlib, json
from playwright.sync_api import sync_playwright
deck, out = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    pg = b.new_page(viewport={"width":1920,"height":1080})
    pg.goto(deck.as_uri()); pg.wait_for_timeout(800); pg.evaluate("document.fonts.ready")
    n = pg.evaluate("document.querySelectorAll('.deck > section.slide').length")
    issues = []
    for k in range(1, n+1):
        pg.evaluate(f"location.hash='#/{k}'"); pg.wait_for_timeout(900)
        pg.screenshot(path=str(out/f"s{k:02d}.png"))
        bad = pg.evaluate("""() => { const s=document.querySelector('.slide.is-active'); const r=s.getBoundingClientRect(); const sc=r.width/1920;
          const o=[]; s.querySelectorAll('*').forEach(e=>{ if(e.closest('.notes')) return; const q=e.getBoundingClientRect(); if(!q.width) return;
            if(q.bottom>r.bottom+1||q.right>r.right+1||q.left<r.left-1) o.push((e.className||e.tagName)+' '+Math.round((q.bottom-r.top)/sc)); });
          const small=[...s.querySelectorAll('p,li,td,th,small,b,span,h3,code')].filter(e=>!e.closest('.notes')&&e.offsetParent&&parseFloat(getComputedStyle(e).fontSize)<20).length;
          return {title:s.dataset.title, overflow:o.slice(0,4), small}; }""")
        if bad["overflow"] or bad["small"]: issues.append({"slide":k, **bad})
    b.close()
print(f"rendered {n} → {out}"); print(json.dumps(issues, ensure_ascii=False, indent=1) if issues else "no overflow / small-text issues")

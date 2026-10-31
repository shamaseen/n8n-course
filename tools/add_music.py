"""Add a soft background-music bed to every explainer film and re-render it.
Run from course-v2/:  python3 tools/add_music.py <dir with bed-warm-loop.wav and bed-ai-loop.wav> [film ...]
Idempotent: a film that already has <audio id="bgm"> only gets its file refreshed and re-rendered."""
import pathlib, re, shutil, subprocess, sys

beds_dir = pathlib.Path(sys.argv[1])
only = set(sys.argv[2:])
AI_FILMS = {"v4-ai-agent", "v12-llm", "v13-rag", "v14-telegram-bot"}  # electronic bed; everything else: warm acoustic
VOLUME = "0.45"  # bed sits under the sound effects (beds are loudness-normalised to -24 LUFS)

for proj in sorted(pathlib.Path("videos").glob("v*-*/index.html")):
    film = proj.parent.name
    if only and film not in only:
        continue
    if not (pathlib.Path("videos/renders") / f"{film}.mp4").exists():
        print(f"skip {film}: not rendered yet"); continue
    bed = "bed-ai-loop.wav" if film in AI_FILMS else "bed-warm-loop.wav"
    (proj.parent / "assets/music").mkdir(parents=True, exist_ok=True)
    shutil.copy(beds_dir / bed, proj.parent / "assets/music" / bed)
    s = proj.read_text()
    dur = re.search(r'data-composition-id="main"[^>]*data-duration="([\d.]+)"', s).group(1)
    tag = (f'<audio id="bgm" class="clip" src="assets/music/{bed}" data-start="0" data-duration="{dur}" '
           f'data-track-index="9" data-volume="{VOLUME}" data-fade-in="1" data-fade-out="2.5"></audio>')
    if 'id="bgm"' in s:
        s = re.sub(r'<audio id="bgm"[^>]*></audio>', tag, s)
    else:
        i = s.index("<audio ")
        s = s[:i] + tag + "\n      " + s[i:]
    proj.write_text(s)
    r = subprocess.run(["npx", "hyperframes", "render", "--quality", "looks", "--output", f"../renders/{film}.mp4"],
                       cwd=proj.parent, capture_output=True, text=True)
    ok = re.search(r"([\d.]+ MB) · ([\d.]+)s video", r.stdout + r.stderr)
    print(f"{film}: {bed} → {'rendered ' + ok.group(0) if ok else 'RENDER FAILED: ' + (r.stdout + r.stderr)[-300:]}")

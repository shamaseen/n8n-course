# SPEC — n8n من الصفر · 4 explainer films (shared)

GOAL:    a non-IT learner understands ONE idea per film and can say it back in one line.
OUTPUT:  HyperFrames, 1920×1080, 30 fps, single-file composition per film (scenes = timed <section> groups).
TIME:    v1 50 s · v2 54 s · v3 50 s · v4 56 s. No music source available (no HeyGen) → bundled SFX only, on visible actions.
LOOK:    the course deck itself (product UI = the medium): paper ground #fbf8f3 flat, ink #1d1a2b, accent #ea4b71 (one focus per frame),
         secondary ink #4b3fa0 for English lines. Node colours = n8n roles: trigger #ff6d5a, action #3d7cf5, logic #f2a20c, AI #7c5cfc, data #12a37f.
         Type: Cairo (local woff2) — Arabic line 80 px / 800, English line 42 px / 700, hero words 120–160 px / 900. Cards: white, 2 px border rgba(40,30,60,.14),
         radius 28 px, shadow 0 14px 40px rgba(40,30,60,.10). No grain, no vignette.
OBJECTS: email card (envelope + sender + subject), spreadsheet (header row + filling rows), n8n nodes (rounded square 180 px, coloured 6 px border, icon 84 px,
         label under), wires (6 px #b9b3cc, arrowhead), JSON card (monospace, key in #ea4b71, value in #12a37f), chat bubbles (user right/ink, bot left/white),
         restaurant: customer 📱, waiter 🤵, kitchen 🍳; door 🚪 + bell 🔔.
MOTION:  enter expo.out 0.5–0.7 s; move power2.inOut 0.6 s; exit power3.in 0.3 s; wires draw scaleX 0→1 power2.out 0.4 s; pops back.out(1.6) 0.45 s;
         words blur 8→0 px 0.18 s. Lines hold ≥ 0.5 s + 0.3 s/word; final line ≥ 3 s.
SHOTS:   see each film's index.html header comment (time ranges per scene).
BANNED:  dark void, glow/neon, purple gradients, glass cards, everything fading up at once, text moving while read, corner labels/HUD, logo in a corner,
         three identical cards in a row as a "feature grid".
QA:      snapshot every scene midpoint + each payoff frame; Arabic shaping intact; no text < 28 px; nothing outside the 90% action-safe box.

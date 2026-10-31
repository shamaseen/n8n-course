# REVIEW — 14 explainer films (rendered 2026-10-31)

All films are 1920×1080 at 30 fps, bilingual (Arabic lines with English under them), and end on one line to remember.
The MP4s are in `renders/` and the poster frames in `renders/posters/`.

| Film | Length | Used in (deck) | One idea |
|---|---|---|---|
| `v1-automation` | 50 s | Class 1 | Sara's copy-paste loop → trigger / steps / result run by themselves |
| `v2-api-webhook` | 54 s | Class 1 | waiter = API (GET → 200, POST → 201), JSON = a filled form, polling vs the webhook doorbell |
| `v3-data-flow` | 50 s | Class 2 | one coffee order: Form → Edit Fields (+total) → IF → Gmail |
| `v4-ai-agent` | 56 s | Class 4 | two-part question → plan → Calculator → Wikipedia → memory → answer |
| `v5-getting-ready` | 55 s | Classes 1, 2 | no install, no coding: a browser + 4 free things (Google, n8n Cloud trial, Gemini key, Telegram) |
| `v6-api-keys` | 52 s | Classes 1, 3 | an API key is a membership card: never share it, cancel it if it leaks, store it once in Credentials |
| `v7-triggers` | 55 s | Class 2 | 5 triggers and their everyday twins: button, alarm clock, doorbell, reception form, chat |
| `v8-expressions` | 49 s | Class 2 | `{{ $json.name }}` is a blank on a greeting card; drag from INPUT and n8n fills it |
| `v9-test-vs-publish` | 52 s | Class 2 | the chef tastes first (Execute), then opens the restaurant (Publish); runs appear in Executions |
| `v10-if-decisions` | 55 s | Class 3 | IF is a road fork (true / false) and each item takes one road; Switch is a mail sorter |
| `v11-debugging` | 55 s | Class 3 | red is a message, not a failure: read → check INPUT → fix one thing → run again |
| `v12-llm` | 55 s | Class 4 | a well-read reader predicting the next word; 3 limits, each with its fix |
| `v13-rag` | 55 s | Class 4 | closed-book vs open-book exam: load the café FAQ once, search it, then answer |
| `v14-telegram-bot` | 55 s | Class 4 | BotFather → token (never share it) → n8n Telegram API credential → Publish |

## Checked
- **Checks:** `npx hyperframes check` passes on every film. The warnings that remain are deliberate:
  - each film is one file with scene groups;
  - node labels are allowed to run wider than their boxes;
  - the counter animations use helper objects;
  - a few overlaps are marked as intended (props in hands, stamps on cards).
- **Frames:** scene midpoints and payoff frames were snapshotted and looked at, and so were frames decoded from the final MP4s. Arabic shaping, right-to-left order, numbers and Latin words inside Arabic, and type of at least 28 px all read correctly.
- **n8n wording** matches n8n 2.45:
  - the run button says "Execute" (v9 and v11 were corrected from "Execute workflow");
  - Publish is top-right;
  - Unpublish is in the menu next to Publish;
  - the Telegram credential field is "Access Token".

## Sound
- **Effects:** on visible actions only, from the bundled HyperFrames library.
- **Music:** two beds made locally with MusicGen-small (`facebook/musicgen-small`, CPU, seed 7). Each is a 28 s clip crossfade-looped to 78 s and normalised to about −25 LUFS, then mixed at volume 0.45 with a 1 s fade-in and a 2.5 s fade-out.
  - `bed-warm-loop.wav` (light acoustic: marimba, plucked guitar, hand percussion) is used for every film except the AI ones.
  - `bed-ai-loop.wav` (soft electronic pads and plucks) is used for v4, v12, v13 and v14.
- **Final mix:** loudness-normalised to about −20 LUFS integrated with a −1.5 dBTP ceiling. Measured results: −18.8 to −22.6 LUFS, peaks at or below −0.7 dBFS.
- **Licence:** the MusicGen-small model weights are CC-BY-NC 4.0. For commercial use, swap in a licensed track: put it in `videos/music/` under the same file names and re-run `tools/add_music.py`.
- **Levels were measured, not listened to.** A spectrogram confirmed both beds are tonal music with a steady pulse. Have a person listen before the first class.

## Editing / re-rendering
- **To edit:** open a film folder in the HyperFrames desktop app, or run `npx hyperframes preview` inside it.
- **To re-render:** run `npx hyperframes render --quality looks --output ../renders/<film>.mp4`. If the RTK shell hook rewrites the command, run it as `rtk proxy npx hyperframes render …`.
- **To redo music and re-render every film:** run `python3 tools/add_music.py videos/music` from the repository root. The two beds live in `videos/music/`. Re-apply the loudness step afterwards:
  ```bash
  ffmpeg -i in.mp4 -c:v copy -af loudnorm=I=-20:TP=-1.5:LRA=11 -c:a aac -b:a 192k out.mp4
  ```
- **To add new video slides to the decks:** run `python3 tools/add_video_slides.py`. It is idempotent.

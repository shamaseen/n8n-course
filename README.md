# n8n من الصفر · n8n From Zero

دورة أتمتة ثنائية اللغة (عربي + English) لمن **ليس لديه أي خلفية تقنية**: أربعة دروس تبدأ من «ما هي الأتمتة؟» وتنتهي ببناء **روبوت محادثة ذكي** يعمل على تيليجرام.

A bilingual (Arabic + English) workflow-automation course for people with **no IT background**. It has four classes, and it starts from "what is automation?" and ends with learners building an **AI chatbot on Telegram** with n8n.

**ابدأ من هنا · Start here:** open [`index.html`](index.html) in Chrome or Firefox. Everything works offline.

## المحتوى · What's inside

| | Class | Slides | Lab | Videos |
|---|---|---|---|---|
| 01 | **Automation & Tech Basics** · أساسيات الأتمتة والتقنية | 36 | in the browser: design an automation, call an API, ring a webhook · bonus `api-in-n8n.json` | 4 |
| 02 | **Meet n8n** · تعرّف على n8n | 38 | `hello-n8n.json`, `weather-api.json`, build from scratch | 5 |
| 03 | **Flows You Can Try** · سير عمل جاهزة للتجربة | 36 | 5 ready workflows: form → sheet → email, weather + IF, webhook alert, news digest, error alert | 3 |
| 04 | **Build an AI Agent Chatbot** · بناء روبوت محادثة ذكي | 37 | AI chat agent (Gemini), Telegram bot, RAG FAQ (optional) | 4 |

Each class folder contains:
- `deck.html`: the slides, with Arabic speaker notes;
- `handout.html` and `handout.pdf`: a printable A4 summary and glossary;
- `lab/lab.html`: the step-by-step lab, plus importable n8n workflows (`lab/*.json`);

**14 explainer videos** (about 50–55 s each) are in `videos/renders/` and are embedded in the slides. Topics include what you need before starting, API keys, triggers, test vs publish, IF, debugging, what an LLM is, RAG, and setting up a Telegram bot.

## كيف تقدّم · Presenting
- Open `class-N/deck.html`.
- `←` `→` navigate, `F` full screen, `S` presenter window (next slide, notes, timer), `O` overview.
- Labs: in n8n, open a workflow → **⋯** (next to the workflow name) → **Import → From file**, then pick the `.json` file.
- Before the course, learners need: a Google account, an **n8n Cloud** trial (no credit card), a free **Gemini** API key (aistudio.google.com/apikey) and **Telegram** on their phone. See the video `v5-getting-ready`.

## المجلدات · Layout
```
index.html            course home page
assets/               shared design system (course.css), slide runtime, Cairo font
class-1-basics/ … class-4-ai-chatbot/
videos/v*/            editable HyperFrames sources for each video
videos/renders/       the rendered MP4s and poster images
videos/music/         background-music beds (see Credits)
tools/                rebuild scripts
```

## إعادة البناء · Rebuild tools
Run these from the repository root:

| Command | What it does |
|---|---|
| `python3 tools/render.py class-2-meet-n8n/deck.html out/` | renders every slide to PNG and reports overflow or text that is too small |
| `python3 tools/md2html.py` | turns each `lab/LAB.md` into the styled `lab/lab.html` page |
| `python3 tools/make_labs.py .` | regenerates the lab workflow JSON files |
| `python3 tools/add_video_slides.py` | adds a video slide for each explainer film to the matching deck |
| `python3 tools/add_music.py videos/music` | mixes the music beds into each video and re-renders it |

Videos are HyperFrames compositions. To edit one, run `npx hyperframes preview` inside a `videos/v*/` folder. To render it, run `npx hyperframes render --quality looks --output ../renders/<name>.mp4`. More notes are in `videos/REVIEW.md`.

## Credits & licences
- **Font:** Cairo, © The Cairo Project Authors, SIL Open Font License 1.1 (`assets/fonts/OFL.txt`).
- **Slide runtime and base styles:** html-ppt, © lewis, MIT (`assets/LICENSE-html-ppt.txt`).
- **Sound effects:** Pixabay Content License (`videos/*/assets/sfx/CREDITS.md`).
- **Background music:** generated with Meta's MusicGen-small. The model weights are licensed CC-BY-NC 4.0, so check that before any commercial use of the videos, or swap in a licensed track with `tools/add_music.py`.
- **Screenshots:** taken from n8n 2.45. n8n is a trademark of n8n GmbH. This course is independent and not affiliated with n8n.

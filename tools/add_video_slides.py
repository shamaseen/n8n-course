"""Insert one video slide per explainer film into the class decks (idempotent: skips films already embedded
or not yet rendered). Run from course-v2/:  python3 tools/add_video_slides.py"""
import pathlib, re, subprocess

FILMS = {  # id: (English title, Arabic title, "watch for" prompt, Arabic speaker notes)
    "v5-getting-ready": ("What You Need Before We Start", "ما تحتاجه قبل أن نبدأ", "عدّ الأشياء الأربعة التي نحتاجها — وكلها مجانية.",
        "فيديو يطمئن الجميع: لا تثبيت برامج ولا برمجة. نحتاج متصفحاً وأربعة أشياء مجانية: حساب Google، حساب n8n Cloud، مفتاح Gemini، وتيليجرام على الهاتف. بعد الفيديو اطلبوا من كل شخص أن يكتب ما ينقصه وساعدوه في الاستراحة."),
    "v6-api-keys": ("API Keys = Your Membership Card", "المفتاح = بطاقة العضوية", "ماذا يحدث لو نسخ أحدهم بطاقتك؟",
        "المفتاح مثل بطاقة النادي: تفتح الباب لك وحدك. n8n يحفظه في Credentials. اسألوا: أين لا نضع المفتاح أبداً؟ في رسالة أو صورة شاشة أو مجموعة. وإذا تسرّب نلغيه وننشئ جديداً مثل بطاقة ضائعة."),
    "v7-triggers": ("What Starts a Workflow?", "ما الذي يُشغّل سير العمل؟", "طابِق كل مُشغّل مع شبيهه في الحياة اليومية.",
        "كل سير عمل يبدأ بمُشغّل واحد: زر، منبّه، جرس باب، نموذج، أو محادثة. بعد الفيديو العبوا: تقرير كل صباح؟ Schedule. متجر يخبرني بطلب؟ Webhook. زبون يملأ طلباً؟ Form."),
    "v8-expressions": ("Fill in the Blanks", "املأ الفراغ", "راقب كيف يمتلئ الفراغ تلقائياً.",
        "{{ $json.name }} مجرد فراغ في بطاقة تهنئة يملؤه n8n من البيانات السابقة. لا داعي لحفظ الأقواس: السحب والإفلات يكتبها عنكم. اسألوا: لو وصلت بيانات ليلى من الزرقاء، ماذا ستكون الرسالة؟"),
    "v9-test-vs-publish": ("Test vs Publish", "جرّب ثم انشر", "متى نضغط Execute؟ ومتى Publish؟",
        "Execute هو تذوّق الطبق: نجرّب ونرى العقد تخضرّ. Publish هو فتح المطعم: يعمل وحده حتى ونحن نائمون. سير عمل بزر يدوي فقط لا يمكن نشره (زر Publish يكون معطّلاً). وكل تشغيل يُحفظ في Executions."),
    "v10-if-decisions": ("IF = A Road Fork", "IF = مفترق طرق", "كل عنصر يسلك طريقاً واحداً — أيّ طريق؟",
        "IF مفترق طرق: الشرط صحيح ← true، غير صحيح ← false. Switch فرّاز بريد بعدة صناديق. اسألوا: احتمال مطر 50 بالضبط والشرط أكبر من 50، أين يذهب؟ false."),
    "v11-debugging": ("Red Node? Don't Panic", "عقدة حمراء؟ لا تقلق", "ما الخطوات الأربع بعد ظهور الأحمر؟",
        "الأحمر رسالة وليس فشلاً. أربع خطوات: اقرأ الرسالة، افتح العقدة وانظر إلى INPUT، أصلح شيئاً واحداً، شغّل من جديد. وتبويب Executions هو الصندوق الأسود. كرّروا الخطوات بصوت عالٍ."),
    "v12-llm": ("What Is an LLM?", "ما هو النموذج اللغوي؟", "ما الحدود الثلاثة؟ وما علاج كل منها؟",
        "قارئ نَهِم يتوقّع الكلمة التالية. يخترع أحياناً، ومعرفته تتوقف عند تاريخ، وضعيف في الحساب. العلاج: حقائق ومستندات وأدوات. الأرقام في الفيديو توضيحية."),
    "v13-rag": ("RAG = An Open-Book Exam", "RAG = امتحان بكتاب مفتوح", "ما الفرق بين الإجابة من الذاكرة ومن الكتاب؟",
        "بدون كتاب الطالب يخمّن، ومع الكتاب يبحث ثم يجيب. نحمّل معلومات المقهى مرة واحدة، ومع كل سؤال يبحث الوكيل ثم يجيب منها، لا من خياله."),
    "v14-telegram-bot": ("Your Telegram Bot in 4 Steps", "بوت تيليجرام في 4 خطوات", "من يصنع البوتات؟ وما هو الـ token؟",
        "الصورة كاملة قبل البناء: BotFather يصنع البوت، الـ token مفتاحه ولا نشاركه، نضعه في Credentials (حقل Access Token)، ثم Publish ونراسله من الهاتف."),
}

PLACES = {  # deck: [(insert after the slide with this data-title, film id)]
    "class-1-basics/deck.html": [("Keys & Safety", "v6-api-keys"), ("Glossary", "v5-getting-ready")],
    "class-2-meet-n8n/deck.html": [("Cloud or self-host", "v5-getting-ready"), ("Triggers", "v7-triggers"),
                                   ("Expressions analogy", "v8-expressions"), ("Test vs live", "v9-test-vs-publish")],
    "class-3-flows/deck.html": [("Safety tips", "v6-api-keys"), ("IF up close", "v10-if-decisions"),
                                ("Section: when things go wrong", "v11-debugging")],
    "class-4-ai-chatbot/deck.html": [("What is an LLM", "v12-llm"), ("Tools test", "v14-telegram-bot"), ("RAG analogy", "v13-rag")],
}


def seconds(film):
    f = pathlib.Path(f"videos/renders/{film}.mp4")
    if not f.exists():
        return None
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                         capture_output=True, text=True).stdout
    return round(float(out))


def slide(film, secs):
    en, ar, watch, notes = FILMS[film]
    return f'''
<!-- VIDEO · {film} -->
<section class="slide" dir="rtl" data-title="Video · {en}">
  <header class="st"><p class="kicker">VIDEO · {secs} SEC</p><h2 class="t-en">{en}</h2><p class="t-ar">فيديو: {ar}</p></header>
  <div class="video" style="width:1040px"><video src="../videos/renders/{film}.mp4" controls preload="metadata"></video></div>
  <p class="small" style="text-align:center;margin-top:14px">👀 {watch}</p>
  <div class="notes">{notes}</div>
</section>
'''


for deck, places in PLACES.items():
    p = pathlib.Path(deck); s = p.read_text(); added = []
    for title, film in places:
        if f"videos/renders/{film}.mp4" in s:
            continue
        secs = seconds(film)
        if secs is None:
            print(f"skip {film}: not rendered yet"); continue
        m = re.search(r'<section[^>]*data-title="' + re.escape(title) + r'"', s)
        assert m, f"{deck}: no slide titled {title!r}"
        end = s.index("</section>", m.end()) + len("</section>")
        s = s[:end] + slide(film, secs) + s[end:]
        added.append(film)
    p.write_text(s)
    print(deck, "added:", added or "nothing new")

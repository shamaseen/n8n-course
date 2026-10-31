"""Generate the importable n8n lab workflows for course-v2.
Run: python3 tools/make_labs.py <course-v2 dir> [only-paths-containing]"""
import json, sys, uuid, pathlib

ROOT = pathlib.Path(sys.argv[1])
B, L = "n8n-nodes-base.", "@n8n/n8n-nodes-langchain."
uid = lambda: str(uuid.uuid4())
WEBHOOK_TYPES = {B + "webhook", B + "formTrigger", B + "telegramTrigger", L + "chatTrigger"}


def node(name, typ, ver, pos, params=None):
    n = {"parameters": params or {}, "id": uid(), "name": name, "type": typ, "typeVersion": ver, "position": list(pos)}
    if typ in WEBHOOK_TYPES:
        n["webhookId"] = uid()
    return n


def sticky(text, pos, w=420, h=None, color=None):
    p = {"content": text, "height": 56 + 22 * (text.count("\n") + 1), "width": w}  # ponytail: height from line count
    if color: p["color"] = color
    return node("Note " + uid()[:6], B + "stickyNote", 1, pos, p)


def wf(path, name, nodes, links):
    """links: (src, dst) or (src, dst, kind) or (src, dst, kind, out_index)"""
    if len(sys.argv) > 2 and sys.argv[2] not in path:
        return
    con = {}
    for l in links:
        src, dst, kind, idx = (*l, "main", 0)[:4] if len(l) == 2 else ((*l, 0)[:4] if len(l) == 3 else l)
        outs = con.setdefault(src, {}).setdefault(kind, [])
        while len(outs) <= idx: outs.append([])
        outs[idx].append({"node": dst, "type": kind, "index": 0})
    names = {n["name"] for n in nodes}
    assert len(names) == len(nodes), "duplicate node names"
    for s, k in con.items():  # every link must point at a real node
        assert s in names, s
        for outs in k.values():
            for o in outs:
                for c in o: assert c["node"] in names, c["node"]
    data = {"name": name, "nodes": nodes, "connections": con, "pinData": {}, "active": False,
            "settings": {"executionOrder": "v1"}, "meta": {"templateCredsSetupCompleted": False}, "tags": []}
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print("wrote", out.relative_to(ROOT), f"({len(nodes)} nodes)")


def setf(*pairs):
    """Edit Fields (Set) 3.4 assignments from (name, value, type) tuples."""
    return {"assignments": {"assignments": [{"id": uid(), "name": n, "value": v, "type": t} for n, v, t in pairs]}, "options": {}}


def if_num(left, op, right):
    return {"conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
            "conditions": [{"id": uid(), "leftValue": left, "rightValue": right, "operator": {"type": "number", "operation": op}}],
            "combinator": "and"}, "looseTypeValidation": True, "options": {}}


def gmail(to, subject, message):
    return {"sendTo": to, "subject": subject, "emailType": "text", "message": message, "options": {"appendAttribution": False}}


YOU = "your.email@gmail.com"
OPEN_METEO = "https://api.open-meteo.com/v1/forecast"

# ───────────────────────── CLASS 1 (bonus, once the n8n account exists) ─────────────────────────
wf("class-1-basics/lab/api-in-n8n.json", "Lab 1.4 · Same API, now in n8n (نفس الـ API داخل n8n)", [
    sticky("## 💱 نفس الرابط… لكن n8n يطلبه عنك\nفي **Lab 1.2** فتحت رابط أسعار العملات في المتصفح وقرأت الـ JSON بعينك.\nهنا عقدة **HTTP Request** تفعل الشيء نفسه، وعقدة **Edit Fields** تلتقط الرقم المهم.\n\n▶️ اضغط **Execute** ثم افتح كل عقدة وشاهد **OUTPUT**.", (-60, -330), 600),
    node("Click to start", B + "manualTrigger", 1, (0, 0)),
    node("Get exchange rates", B + "httpRequest", 4.2, (240, 0), {"url": "https://open.er-api.com/v6/latest/JOD", "options": {}}),
    node("Find the dollar", B + "set", 3.4, (480, 0), setf(
        ("usd", "={{ $json.rates.USD }}", "number"), ("sar", "={{ $json.rates.SAR }}", "number"),
        ("message", "=💱 1 دينار أردني = {{ $json.rates.USD }} دولار = {{ $json.rates.SAR }} ريال", "string"),
        ("updated", "={{ $json.time_last_update_utc }}", "string"))),
], [("Click to start", "Get exchange rates"), ("Get exchange rates", "Find the dollar")])

# ───────────────────────── CLASS 2 ─────────────────────────
wf("class-2-meet-n8n/lab/hello-n8n.json", "Lab 2.1 · Hello n8n (مرحباً n8n)", [
    sticky("## 👋 أول سير عمل لك\n1. اضغط **Execute workflow** في الأسفل.\n2. افتح كل عقدة وشاهد البيانات في لوحة **OUTPUT**.\n3. غيّر الاسم `Sara` إلى اسمك ثم شغّل مرة أخرى!\n\n**First workflow:** click *Execute workflow*, open each node, change the name.", (-60, -320), 520, 280, 4),
    node("Click to start", B + "manualTrigger", 1, (0, 0)),
    node("My info", B + "set", 3.4, (240, 0), setf(("name", "Sara", "string"), ("city", "Amman", "string"), ("hobby", "coffee ☕", "string"))),
    node("Build message", B + "set", 3.4, (480, 0), setf(
        ("message_ar", "=مرحباً {{ $json.name }} من {{ $json.city }}! 👋", "string"),
        ("message_en", "=Hello {{ $json.name }} from {{ $json.city }}! You like {{ $json.hobby }}", "string"),
        ("today", "={{ $now.format('yyyy-MM-dd') }}", "string"))),
], [("Click to start", "My info"), ("My info", "Build message")])

wf("class-2-meet-n8n/lab/weather-api.json", "Lab 2.2 · Weather from an API (الطقس من API)", [
    sticky("## 🌤️ نطلب الطقس من الإنترنت\n- **City**: نكتب المدينة وإحداثياتها.\n- **Get weather**: عقدة HTTP تطلب البيانات من موقع open-meteo (مجاني، بدون مفتاح).\n- **Weather message**: نحوّل الرقم إلى جملة مفهومة.\n\n🎯 جرّب: غيّر المدينة إلى `Riyadh` (24.71, 46.67) أو `Cairo` (30.04, 31.24).", (-60, -360), 640, 300, 4),
    node("Click to start", B + "manualTrigger", 1, (0, 0)),
    node("City", B + "set", 3.4, (240, 0), setf(("city", "Amman", "string"), ("latitude", 31.95, "number"), ("longitude", 35.93, "number"))),
    node("Get weather", B + "httpRequest", 4.2, (480, 0), {"url": OPEN_METEO, "sendQuery": True, "queryParameters": {"parameters": [
        {"name": "latitude", "value": "={{ $json.latitude }}"}, {"name": "longitude", "value": "={{ $json.longitude }}"},
        {"name": "current", "value": "temperature_2m,wind_speed_10m,precipitation"}, {"name": "timezone", "value": "auto"}]}, "options": {}}),
    node("Weather message", B + "set", 3.4, (720, 0), setf(
        ("temperature", "={{ $json.current.temperature_2m }}", "number"),
        ("message", "=🌡️ الطقس الآن في {{ $('City').item.json.city }}: {{ $json.current.temperature_2m }}°C — الرياح {{ $json.current.wind_speed_10m }} km/h", "string"))),
], [("Click to start", "City"), ("City", "Get weather"), ("Get weather", "Weather message")])

# ───────────────────────── CLASS 3 ─────────────────────────
wf("class-3-flows/lab/form-to-sheet-email.json", "Lab 3.1 · Contact form → Sheet + Email", [
    sticky("## 📝 نموذج تواصل ← جدول ← بريد\n1. **Contact form**: نموذج ويب جاهز (اضغط *Execute* ثم افتح الرابط).\n2. **Save to sheet**: يحفظ كل رد كسطر في Google Sheets.\n   ↳ أنشئ جدولاً بأعمدة: `Name`, `Email`, `Message`.\n3. **Notify me**: يرسل لك بريداً فورياً.\n\n🔑 تحتاج: ربط حساب Google (Credentials) مرة واحدة.", (-60, -400), 620, 330, 4),
    node("Contact form", B + "formTrigger", 2.2, (0, 0), {"formTitle": "Contact us · تواصل معنا", "formDescription": "نرد عليك خلال يوم عمل واحد", "formFields": {"values": [
        {"fieldLabel": "Name", "placeholder": "اسمك", "requiredField": True},
        {"fieldLabel": "Email", "fieldType": "email", "placeholder": "you@example.com", "requiredField": True},
        {"fieldLabel": "Message", "fieldType": "textarea", "placeholder": "رسالتك"}]}, "options": {}}),
    node("Save to sheet", B + "googleSheets", 4.5, (260, 0), {"operation": "append",
        "documentId": {"__rl": True, "value": "", "mode": "list"}, "sheetName": {"__rl": True, "value": "", "mode": "list"},
        "columns": {"mappingMode": "autoMapInputData", "value": {}, "matchingColumns": [], "schema": [], "attemptToConvertTypes": False, "convertFieldsToString": False},
        "options": {}}),
    node("Notify me", B + "gmail", 2.1, (520, 0), gmail(YOU, "=📩 رسالة جديدة من {{ $('Contact form').item.json.Name }}",
        "=الاسم: {{ $('Contact form').item.json.Name }}\nالبريد: {{ $('Contact form').item.json.Email }}\n\nالرسالة:\n{{ $('Contact form').item.json.Message }}")),
], [("Contact form", "Save to sheet"), ("Save to sheet", "Notify me")])

wf("class-3-flows/lab/daily-weather-email.json", "Lab 3.2 · Daily weather email (بريد الطقس اليومي)", [
    sticky("## ☔ هل آخذ المظلة اليوم؟\n- **Every day 7:00**: يعمل تلقائياً كل صباح.\n- **Forecast**: يجلب توقعات اليوم.\n- **Rain likely?**: عقدة **IF** — هل احتمال المطر أكثر من 50%؟\n  - ✅ true ← بريد «خذ المظلة»\n  - ❌ false ← بريد «يوم جميل»\n\n⚠️ لا يعمل تلقائياً إلا بعد **Publish/Activate**.", (-60, -420), 600, 340, 4),
    node("Every day 7:00", B + "scheduleTrigger", 1.2, (0, 0), {"rule": {"interval": [{"triggerAtHour": 7}]}}),
    node("Forecast", B + "httpRequest", 4.2, (240, 0), {"url": OPEN_METEO, "sendQuery": True, "queryParameters": {"parameters": [
        {"name": "latitude", "value": "31.95"}, {"name": "longitude", "value": "35.93"},
        {"name": "daily", "value": "temperature_2m_max,temperature_2m_min,precipitation_probability_max"},
        {"name": "timezone", "value": "auto"}, {"name": "forecast_days", "value": "1"}]}, "options": {}}),
    node("Rain likely?", B + "if", 2.2, (480, 0), if_num("={{ $json.daily.precipitation_probability_max[0] }}", "gt", 50)),
    node("Umbrella email", B + "gmail", 2.1, (760, -120), gmail(YOU, "☔ خذ المظلة اليوم!",
        "=احتمال المطر {{ $json.daily.precipitation_probability_max[0] }}%\nالحرارة: {{ $json.daily.temperature_2m_min[0] }}° – {{ $json.daily.temperature_2m_max[0] }}°")),
    node("Sunny email", B + "gmail", 2.1, (760, 120), gmail(YOU, "☀️ يوم جميل بلا مطر",
        "=احتمال المطر {{ $json.daily.precipitation_probability_max[0] }}% فقط\nالحرارة: {{ $json.daily.temperature_2m_min[0] }}° – {{ $json.daily.temperature_2m_max[0] }}°")),
], [("Every day 7:00", "Forecast"), ("Forecast", "Rain likely?"), ("Rain likely?", "Umbrella email", "main", 0), ("Rain likely?", "Sunny email", "main", 1)])

wf("class-3-flows/lab/webhook-alert.json", "Lab 3.3 · Webhook big-order alert (تنبيه الطلبات الكبيرة)", [
    sticky("## 🔔 جرس الباب: طلب جديد وصل!\n- **New order**: رابط Webhook يستقبل الطلبات من أي متجر/تطبيق.\n- **Big order?**: إذا كان المبلغ أكبر من 100 ← نرسل تنبيهاً.\n- **Small order**: لا شيء، فقط نسجّل.\n\n🧪 للتجربة: اضغط *Execute*، ثم أرسل من hoppscotch.io طلب **POST** إلى رابط الـ Test URL مع:\n`{\"customer\":\"Omar\",\"amount\":250}`", (-60, -440), 640, 360, 4),
    node("New order", B + "webhook", 2, (0, 0), {"httpMethod": "POST", "path": "new-order", "options": {}}),
    node("Big order?", B + "if", 2.2, (240, 0), if_num("={{ $json.body.amount }}", "gt", 100)),
    node("Alert me", B + "gmail", 2.1, (520, -120), gmail(YOU, "=💰 طلب كبير: {{ $json.body.amount }} من {{ $json.body.customer }}",
        "=وصل طلب جديد بقيمة {{ $json.body.amount }}.\nالعميل: {{ $json.body.customer }}")),
    node("Small order", B + "set", 3.4, (520, 120), setf(("note", "=طلب صغير ({{ $json.body.amount }}) — لا حاجة لتنبيه", "string"))),
], [("New order", "Big order?"), ("Big order?", "Alert me", "main", 0), ("Big order?", "Small order", "main", 1)])

wf("class-3-flows/lab/news-digest.json", "Lab 3.4 · Morning news digest (ملخص الأخبار الصباحي)", [
    sticky("## 📰 أهم 5 أخبار في بريدك كل صباح\n- **Every day 8:00** ← **BBC Arabic RSS** يقرأ الأخبار.\n- **Top 5**: عقدة **Limit** تأخذ أول 5 فقط.\n- **Combine**: عقدة **Aggregate** تجمع العناوين في قائمة واحدة.\n- **Send digest**: بريد واحد فيه كل العناوين.\n\n🎯 جرّب: ضع رابط RSS لموقع تحبه.", (-60, -400), 620, 320, 4),
    node("Every day 8:00", B + "scheduleTrigger", 1.2, (0, 0), {"rule": {"interval": [{"triggerAtHour": 8}]}}),
    node("BBC Arabic RSS", B + "rssFeedRead", 1.1, (240, 0), {"url": "https://feeds.bbci.co.uk/arabic/rss.xml", "options": {}}),
    node("Top 5", B + "limit", 1, (480, 0), {"maxItems": 5}),
    node("Combine", B + "aggregate", 1, (720, 0), {"fieldsToAggregate": {"fieldToAggregate": [{"fieldToAggregate": "title"}, {"fieldToAggregate": "link"}]}, "options": {}}),
    node("Send digest", B + "gmail", 2.1, (960, 0), gmail(YOU, "=📰 أخبار الصباح — {{ $now.format('yyyy-MM-dd') }}",
        "={{ $json.title.map((t, i) => (i + 1) + '. ' + t + '\\n' + $json.link[i]).join('\\n\\n') }}")),
], [("Every day 8:00", "BBC Arabic RSS"), ("BBC Arabic RSS", "Top 5"), ("Top 5", "Combine"), ("Combine", "Send digest")])

wf("class-3-flows/lab/error-alert.json", "Lab 3.5 · Error alert (تنبيه الأخطاء)", [
    sticky("## 🚨 أخبرني إذا فشل أي سير عمل\n1. احفظ هذا الـ workflow.\n2. افتح أي workflow آخر ← **Settings** ← **Error workflow** ← اختر هذا.\n3. عند أي فشل يصلك بريد فيه اسم الـ workflow ورسالة الخطأ ورابط التنفيذ.", (-60, -340), 600, 260, 3),
    node("When a workflow fails", B + "errorTrigger", 1, (0, 0)),
    node("Email the error", B + "gmail", 2.1, (260, 0), gmail(YOU, "=🚨 فشل: {{ $json.workflow.name }}",
        "=الـ workflow: {{ $json.workflow.name }}\nالعقدة: {{ $json.execution.lastNodeExecuted }}\nالخطأ: {{ $json.execution.error.message }}\n\nافتح التنفيذ: {{ $json.execution.url }}")),
], [("When a workflow fails", "Email the error")])

# ───────────────────────── CLASS 4 ─────────────────────────
CAFE_PROMPT = """أنت "قهوة بوت" ☕ — مساعد ودود لمقهى "قفزة" في عمّان.
You are "Qahwa Bot", a friendly assistant for Qafza Café in Amman.

القواعد / Rules:
- أجب بنفس لغة السائل (عربي أو English). Reply in the user's language.
- جمل قصيرة وواضحة، مع إيموجي واحد على الأكثر.
- معلومات المقهى: نفتح يومياً 8 صباحاً – 11 مساءً. القهوة العربية 1.5 دينار، لاتيه 2.5 دينار، كيك الشوكولاتة 3 دنانير. الموقع: شارع الرينبو.
- استخدم أداة Calculator لأي حساب (مثل مجموع طلب أو خصم).
- استخدم Wikipedia فقط لأسئلة المعرفة العامة.
- إذا لم تعرف الجواب قل ذلك بصراحة ولا تخترع."""

ai_common = [
    ("Gemini model", "AI Agent", "ai_languageModel"),
    ("Memory", "AI Agent", "ai_memory"),
    ("Calculator", "AI Agent", "ai_tool"),
]
wf("class-4-ai-chatbot/lab/chat-agent.json", "Lab 4.1 · AI chat agent (روبوت المحادثة الذكي)", [
    sticky("## 🤖 وكيل ذكي = عقل + ذاكرة + أدوات\n- 🧠 **Gemini model**: العقل (يحتاج مفتاح مجاني من aistudio.google.com).\n- 📒 **Memory**: يتذكر آخر 10 رسائل.\n- 🧮 **Calculator** و 📚 **Wikipedia**: الأدوات (اليدين).\n\n▶️ اضغط **Open chat** في الأسفل واسأل:\n«كم سعر 2 لاتيه وكيكة؟» أو «من هو ابن سينا؟»", (-80, -440), 620, 330, 4),
    node("When chat message received", L + "chatTrigger", 1.1, (0, 0), {"options": {}}),
    node("AI Agent", L + "agent", 2.2, (300, 0), {"options": {"systemMessage": CAFE_PROMPT}}),
    node("Gemini model", L + "lmChatGoogleGemini", 1.2, (180, 240), {"options": {"temperature": 0.4}}),
    node("Memory", L + "memoryBufferWindow", 1.3, (340, 240), {"contextWindowLength": 10}),
    node("Calculator", L + "toolCalculator", 1, (500, 240)),
    node("Wikipedia", L + "toolWikipedia", 1, (640, 240)),
], [("When chat message received", "AI Agent"), *ai_common, ("Wikipedia", "AI Agent", "ai_tool")])

TG_CHAT = "={{ $('Telegram Trigger').item.json.message.chat.id }}"
wf("class-4-ai-chatbot/lab/telegram-agent.json", "Lab 4.2 · Telegram AI bot (بوت تيليجرام الذكي)", [
    sticky("## 📱 نفس الوكيل… على تيليجرام\n1. في تيليجرام افتح **@BotFather** ← `/newbot` ← انسخ الـ **token**.\n2. أضف الـ token في Credentials لعقدتي Telegram.\n3. اضغط **Publish/Activate** ثم راسل البوت من هاتفك!\n\n🧠 الذاكرة مفصولة لكل محادثة عبر `chat.id`.", (-80, -420), 620, 300, 4),
    node("Telegram Trigger", B + "telegramTrigger", 1.1, (0, 0), {"updates": ["message"], "additionalFields": {}}),
    node("AI Agent", L + "agent", 2.2, (300, 0), {"promptType": "define", "text": "={{ $json.message.text }}", "options": {"systemMessage": CAFE_PROMPT}}),
    node("Gemini model", L + "lmChatGoogleGemini", 1.2, (180, 240), {"options": {"temperature": 0.4}}),
    node("Memory", L + "memoryBufferWindow", 1.3, (340, 240), {"sessionIdType": "customKey", "sessionKey": TG_CHAT, "contextWindowLength": 10}),
    node("Calculator", L + "toolCalculator", 1, (500, 240)),
    node("Reply on Telegram", B + "telegram", 1.2, (660, 0), {"chatId": TG_CHAT, "text": "={{ $json.output }}", "additionalFields": {"appendAttribution": False}}),
], [("Telegram Trigger", "AI Agent"), *ai_common, ("AI Agent", "Reply on Telegram")])

FAQ = """قائمة مقهى قفزة / Qafza Café FAQ
- ساعات العمل: يومياً من 8 صباحاً حتى 11 مساءً. الجمعة من 2 ظهراً.
- القهوة العربية 1.5 دينار. لاتيه 2.5 دينار. كابتشينو 2.5 دينار. شاي بالنعناع 1 دينار.
- كيك الشوكولاتة 3 دنانير. كرواسون 1.75 دينار.
- يوجد واي فاي مجاني. كلمة السر تُطلب من الكاشير.
- نقبل الدفع نقداً وبالبطاقة وCliQ.
- التوصيل عبر طلبات وكريم داخل عمّان فقط.
- خصم 10% للطلاب مع البطاقة الجامعية.
- الموقع: شارع الرينبو، جبل عمّان، بجانب المكتبة."""
wf("class-4-ai-chatbot/lab/rag-faq.json", "Lab 4.3 · RAG café FAQ (اختياري: وكيل يقرأ مستنداتك)", [
    sticky("## 📚 RAG = امتحان بكتاب مفتوح\n**الجزء ①**: اضغط *Execute* على «Load FAQ» مرة واحدة ← يحفظ معلومات المقهى في الذاكرة.\n**الجزء ②**: افتح **Chat** واسأل: «هل يوجد خصم للطلاب؟»\nالوكيل يبحث في المستند قبل أن يجيب.\n\n⚠️ Simple Vector Store يُمسح عند إعادة تشغيل n8n.", (-80, -480), 640, 300, 4),
    node("Load FAQ", B + "manualTrigger", 1, (0, 0)),
    node("Café FAQ text", B + "set", 3.4, (220, 0), setf(("text", FAQ, "string"))),
    node("Save to knowledge base", L + "vectorStoreInMemory", 1.1, (460, 0), {"mode": "insert", "memoryKey": "cafe_faq"}),
    node("Embeddings (insert)", L + "embeddingsGoogleGemini", 1, (400, 220), {"modelName": "models/gemini-embedding-001"}),
    node("Document loader", L + "documentDefaultDataLoader", 1.1, (560, 220), {"options": {}}),
    node("When chat message received", L + "chatTrigger", 1.1, (0, 520), {"options": {}}),
    node("AI Agent", L + "agent", 2.2, (300, 520), {"options": {"systemMessage": "أنت مساعد مقهى قفزة. أجب فقط من أداة cafe_faq. إذا لم تجد الجواب فيها قل: لا أعرف، اسأل الكاشير. Reply in the user's language."}}),
    node("Gemini model", L + "lmChatGoogleGemini", 1.2, (200, 760), {"options": {"temperature": 0.2}}),
    node("Café knowledge", L + "vectorStoreInMemory", 1.1, (460, 760), {"mode": "retrieve-as-tool", "toolName": "cafe_faq",
        "toolDescription": "Café information: opening hours, menu prices, wifi, payment, delivery, discounts, location.", "memoryKey": "cafe_faq", "topK": 4}),
    node("Embeddings (search)", L + "embeddingsGoogleGemini", 1, (460, 960), {"modelName": "models/gemini-embedding-001"}),
], [("Load FAQ", "Café FAQ text"), ("Café FAQ text", "Save to knowledge base"),
    ("Embeddings (insert)", "Save to knowledge base", "ai_embedding"), ("Document loader", "Save to knowledge base", "ai_document"),
    ("When chat message received", "AI Agent"), ("Gemini model", "AI Agent", "ai_languageModel"),
    ("Café knowledge", "AI Agent", "ai_tool"), ("Embeddings (search)", "Café knowledge", "ai_embedding")])

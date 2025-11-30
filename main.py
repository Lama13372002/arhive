import os, asyncio, json, re, ssl, socket, traceback
from typing import Tuple, Optional, Dict, Any, List
import aiohttp, certifi
from aiohttp import web

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

# ====== КОНФИГ (заполни) ======
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"
SUNO_API_KEY = "YOUR_SUNO_API_KEY_HERE"
PUBLIC_BASE_URL = "https://api.aibot.kz"     # домен с https
SUNO_API_BASE  = "https://api.sunoapi.org"
HTTP_PORT = 8080

# Необязательно: стикер на “генерацию”.
# Узнать file_id можно, прислав боту стикер и глянув в логах, либо оставить пустым.
STICKER_ID = ""  # например: "CAACAgIAAxkBA..."

# ====== СЕТЬ: SSL + IPv4 ======
import certifi, ssl, socket
SSL_CTX = ssl.create_default_context(cafile=certifi.where())
def session(timeout_sec: int = 60) -> aiohttp.ClientSession:
    return aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=timeout_sec),
        connector=aiohttp.TCPConnector(ssl=SSL_CTX, family=socket.AF_INET),
        trust_env=False,
    )

# ====== TELEGRAM ======
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Преднастройки для кнопок (можно расширять)
GENRES = ["pop", "rap", "rnb", "rock", "edm", "house", "drill", "phonk", "indie", "jazz", "lofi"]
MOODS  = ["happy", "romantic", "epic", "sad", "motivational", "chill", "dark", "uplifting", "cinematic"]
LANGS  = ["ru", "kz", "en"]
TEMPOS = ["slow", "medium", "fast", "bpm_85", "bpm_100", "bpm_120", "bpm_140"]
VOCALS = ["vocal:on", "vocal:off"]
INSTRS = ["guitar", "piano", "strings", "brass", "808", "synth", "drums", "pad", "choir"]

def grid_buttons(items: List[str], prefix: str, cols: int = 3, toggles: bool = True):
    kb = []
    row = []
    for i, item in enumerate(items, 1):
        row.append(InlineKeyboardButton(text=item, callback_data=f"{prefix}:{item}"))
        if i % cols == 0:
            kb.append(row); row = []
    if row: kb.append(row)
    if toggles:
        kb.append([InlineKeyboardButton(text="Готово ✅", callback_data=f"{prefix}:__done")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Одобрить и сгенерить 🎵", callback_data="confirm:approve")],
        [InlineKeyboardButton(text="Править текст ✍️", callback_data="confirm:edit_lyrics"),
         InlineKeyboardButton(text="Править prompt 🎛️", callback_data="confirm:edit_prompt")],
        [InlineKeyboardButton(text="Перегенерить ♻️", callback_data="confirm:regenerate")],
        [InlineKeyboardButton(text="Отмена ❌", callback_data="confirm:cancel")],
    ])

class Flow(StatesGroup):
    for_who = State()
    occasion = State()
    style_step = State()
    lang_step = State()
    mood_step = State()
    tempo_step = State()
    vocal_step = State()
    instr_step = State()
    details = State()
    ready_preview = State()
    edit_lyrics = State()
    edit_prompt = State()

# ====== ХЭНДЛЕРЫ ОПРОСА ======
@dp.message(CommandStart())
async def start(m: Message, state: FSMContext):
    await state.clear()
    await state.update_data(style_list=[], lang=None, mood=None, tempo=None, vocal=None, instr=[])
    await m.answer("Создаём песню. Для кого она?")
    await state.set_state(Flow.for_who)

@dp.message(Flow.for_who)
async def ask_occ(m: Message, state: FSMContext):
    await state.update_data(for_who=m.text.strip())
    await m.answer("Повод (ДР, признание, реклама, юбилей и т.д.)?")
    await state.set_state(Flow.occasion)

@dp.message(Flow.occasion)
async def ask_genre(m: Message, state: FSMContext):
    await state.update_data(occasion=m.text.strip())
    await m.answer("Выбери ЖАНР(ы) (multi-select), затем «Готово ✅».", reply_markup=grid_buttons(GENRES, "genre"))
    await state.set_state(Flow.style_step)

@dp.callback_query(F.data.startswith("genre:"), Flow.style_step)
async def pick_genre(c: CallbackQuery, state: FSMContext):
    _, val = c.data.split(":", 1)
    data = await state.get_data()
    styles = set(data.get("style_list", []))
    if val == "__done":
        await c.message.edit_reply_markup()
        await c.message.answer("Выбери ЯЗЫК.", reply_markup=grid_buttons(LANGS, "lang", cols=3, toggles=False))
        await state.set_state(Flow.lang_step)
    else:
        if val in styles: styles.remove(val)
        else: styles.add(val)
        await state.update_data(style_list=list(styles))
        await c.answer(f"{'✔️' if val in styles else '✖️'} {val}")

@dp.callback_query(F.data.startswith("lang:"), Flow.lang_step)
async def pick_lang(c: CallbackQuery, state: FSMContext):
    _, val = c.data.split(":", 1)
    await state.update_data(lang=val)
    await c.message.edit_text(f"Язык: {val}\n\nТеперь выбери НАСТРОЕНИЕ:", reply_markup=grid_buttons(MOODS, "mood", cols=3, toggles=False))
    await state.set_state(Flow.mood_step)

@dp.callback_query(F.data.startswith("mood:"), Flow.mood_step)
async def pick_mood(c: CallbackQuery, state: FSMContext):
    _, val = c.data.split(":", 1)
    await state.update_data(mood=val)
    await c.message.edit_text(f"Настроение: {val}\n\nВыбери ТЕМП:", reply_markup=grid_buttons(TEMPOS, "tempo", cols=3, toggles=False))
    await state.set_state(Flow.tempo_step)

@dp.callback_query(F.data.startswith("tempo:"), Flow.tempo_step)
async def pick_tempo(c: CallbackQuery, state: FSMContext):
    _, val = c.data.split(":", 1)
    await state.update_data(tempo=val)
    await c.message.edit_text(f"Темп: {val}\n\nВокал включить/выключить:", reply_markup=grid_buttons(VOCALS, "vocal", cols=2, toggles=False))
    await state.set_state(Flow.vocal_step)

@dp.callback_query(F.data.startswith("vocal:"), Flow.vocal_step)
async def pick_vocal(c: CallbackQuery, state: FSMContext):
    _, val = c.data.split(":", 1)
    await state.update_data(vocal=val)
    await c.message.edit_text(f"Вокал: {val}\n\nВыбери ИНСТРУМЕНТЫ (multi-select), затем «Готово ✅».",
                              reply_markup=grid_buttons(INSTRS, "instr", cols=3))
    await state.set_state(Flow.instr_step)

@dp.callback_query(F.data.startswith("instr:"), Flow.instr_step)
async def pick_instr(c: CallbackQuery, state: FSMContext):
    _, val = c.data.split(":", 1)
    data = await state.get_data()
    instr = set(data.get("instr", []))
    if val == "__done":
        await c.message.edit_reply_markup()
        await c.message.answer("Добавь имена/факты/внутренние шутки (через запятую).")
        await state.set_state(Flow.details)
    else:
        if val in instr: instr.remove(val)
        else: instr.add(val)
        await state.update_data(instr=list(instr))
        await c.answer(f"{'✔️' if val in instr else '✖️'} {val}")

@dp.message(Flow.details)
async def make_preview(m: Message, state: FSMContext):
    await state.update_data(details=m.text.strip())
    data = await state.get_data()

    await m.answer("Формирую черновик текста…")
    lyrics, suno_prompt, title, style_text, style_list = await build_prompt_and_lyrics(data)

    # сохраним черновик, чтобы можно было править
    await state.update_data(lyrics=lyrics, prompt=suno_prompt, title=title, style_text=style_text, style_list=style_list)

    # Предпросмотр
    preview = (f"🎼 *{title}*\n"
               f"Style (массив): `{style_list}`\n"
               f"Style (текст): `{style_text}`\n"
               f"Prompt (≤400): `{suno_prompt}`\n\n"
               f"{lyrics}")
    await m.answer(preview, parse_mode="Markdown", reply_markup=confirm_kb())
    await state.set_state(Flow.ready_preview)

# ====== КНОПКИ ПРЕДПРОСМОТРА ======
@dp.callback_query(F.data == "confirm:approve", Flow.ready_preview)
async def approve(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = c.from_user.id

    # загрузочная “анимация”
    if STICKER_ID:
        await c.message.answer_sticker(STICKER_ID)
    else:
        await bot.send_chat_action(chat_id=c.message.chat.id, action="upload_audio")

    try:
        task_id = await suno_generate_music(lyrics=data["lyrics"],
                                            prompt=data["prompt"],
                                            title=data["title"],
                                            style=data["style_text"],
                                            user_id=user_id)
        # параллельный polling на всякий случай
        asyncio.create_task(poll_and_send(task_id, user_id))
        await c.message.answer("Отправил в Suno. Придут 1–2 версии, пришлю сюда.")
    except Exception as e:
        await c.message.answer(f"Ошибка Suno: {e}")

@dp.callback_query(F.data == "confirm:edit_lyrics", Flow.ready_preview)
async def edit_lyrics_btn(c: CallbackQuery, state: FSMContext):
    await c.message.answer("Пришли полностью *исправленный текст* (с [Verse]/[Chorus]/[Bridge]).", parse_mode="Markdown")
    await state.set_state(Flow.edit_lyrics)

@dp.message(Flow.edit_lyrics)
async def edited_lyrics(m: Message, state: FSMContext):
    await state.update_data(lyrics=m.text.strip())
    data = await state.get_data()
    preview = (f"🎼 *{data.get('title','Song')}*\n"
               f"Style (массив): `{data.get('style_list',[])}`\n"
               f"Style (текст): `{data.get('style_text','')}`\n"
               f"Prompt (≤400): `{data.get('prompt','')}`\n\n"
               f"{m.text.strip()}")
    await m.answer("Обновил текст. Проверяй 👇", parse_mode="Markdown")
    await m.answer(preview, parse_mode="Markdown", reply_markup=confirm_kb())
    await state.set_state(Flow.ready_preview)

@dp.callback_query(F.data == "confirm:edit_prompt", Flow.ready_preview)
async def edit_prompt_btn(c: CallbackQuery, state: FSMContext):
    await c.message.answer("Пришли *короткий Suno prompt* (≤400 символов).", parse_mode="Markdown")
    await state.set_state(Flow.edit_prompt)

@dp.message(Flow.edit_prompt)
async def edited_prompt(m: Message, state: FSMContext):
    p = " ".join(ln.strip() for ln in m.text.splitlines() if ln.strip())[:400]
    await state.update_data(prompt=p)
    data = await state.get_data()
    preview = (f"🎼 *{data.get('title','Song')}*\n"
               f"Style (массив): `{data.get('style_list',[])}`\n"
               f"Style (текст): `{data.get('style_text','')}`\n"
               f"Prompt (≤400): `{p}`\n\n"
               f"{data.get('lyrics','')}")
    await m.answer("Обновил prompt. Проверяй 👇", parse_mode="Markdown")
    await m.answer(preview, parse_mode="Markdown", reply_markup=confirm_kb())
    await state.set_state(Flow.ready_preview)

@dp.callback_query(F.data == "confirm:regenerate", Flow.ready_preview)
async def regenerate(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await c.message.answer("Перегенерирую черновик…")
    lyrics, suno_prompt, title, style_text, style_list = await build_prompt_and_lyrics(data)
    await state.update_data(lyrics=lyrics, prompt=suno_prompt, title=title, style_text=style_text, style_list=style_list)
    preview = (f"🎼 *{title}*\nStyle (массив): `{style_list}`\nStyle (текст): `{style_text}`\nPrompt: `{suno_prompt}`\n\n{lyrics}")
    await c.message.answer(preview, parse_mode="Markdown", reply_markup=confirm_kb())

@dp.callback_query(F.data == "confirm:cancel", Flow.ready_preview)
async def cancel(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await c.message.answer("Окей, отменил. Нажми /start, когда будешь готов заново.")

# ====== GPT ======
def _one_line(s: str) -> str:
    return " ".join(ln.strip() for ln in s.splitlines() if ln.strip())

def _safe(s: str, n: int) -> str:
    return s[:n] if len(s) > n else s

async def build_prompt_and_lyrics(data: dict) -> Tuple[str, str, str, str, List[str]]:
    # собираем style-массив из выбранных пунктов
    style_list = []
    style_list += data.get("style_list", [])
    if data.get("mood"): style_list.append(data["mood"])
    if data.get("tempo"): style_list.append(data["tempo"])
    if data.get("vocal"): style_list.append(data["vocal"])
    if data.get("instr"): style_list += data["instr"]
    if data.get("lang"): style_list.append(f"language: {data['lang']}")

    style_text = ", ".join(style_list)

    sys = (
        "Ты — профессиональный сонграйтер. Пиши исполнимый текст 60–90 сек "
        "с метками [Verse]/[Chorus]/[Bridge], без мата и клише."
    )
    user = f"""
Бриф:
Для кого: {data.get('for_who')}
Повод: {data.get('occasion')}
Style (массив): {style_list}
Язык: {data.get('lang')}
Доп. детали: {data.get('details')}

Отдай в формате:
Title: <до 80 символов>
Prompt: <до 400 символов, кратко и по делу>
<далее текст с метками [Verse]/[Chorus]/[Bridge]>
""".strip()

    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "system", "content": sys},
                     {"role": "user", "content": user}],
        "temperature": 0.8,
    }
    async with session(60) as s:
        async with s.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}",
                     "Content-Type": "application/json"},
            data=json.dumps(payload),
        ) as r:
            body = await r.text()
            if r.status >= 400:
                raise RuntimeError(f"OpenAI HTTP {r.status}: {body}")
            j = json.loads(body)

    content = j["choices"][0]["message"]["content"]
    t = re.search(r"(?i)^Title:\s*(.+)$", content, re.M)
    p = re.search(r"(?i)^Prompt:\s*(.+)$", content, re.M)
    mark = re.search(r"\[(Verse|Chorus|Bridge)\]", content, flags=re.I)

    title = _safe((t.group(1).strip() if t else "New Song"), 80)
    suno_prompt = _safe(_one_line(p.group(1)) if p else "pop, medium tempo, language: ru, vocal: on", 400)
    lyrics = content[mark.start():].strip() if mark else content.strip()
    return lyrics, suno_prompt, title, style_text, style_list

# ====== SUNO (callback + polling, отправляем ВСЕ версии) ======
pending: Dict[str, int] = {}  # taskId -> telegram user_id

def _extract_mp3s(obj: Any) -> List[str]:
    links = []
    if isinstance(obj, dict):
        for k in ("audioUrl", "downloadUrl", "streamUrl"):
            v = obj.get(k)
            if isinstance(v, str) and v.startswith("http"):
                links.append(v)
        for v in obj.values():
            links.extend(_extract_mp3s(v))
    elif isinstance(obj, list):
        for it in obj:
            links.extend(_extract_mp3s(it))
    # уникализируем порядок
    seen = set(); out = []
    for u in links:
        if u not in seen:
            seen.add(u); out.append(u)
    return out

async def suno_generate_music(lyrics: str, prompt: str, title: str, style: str, user_id: int) -> str:
    headers = {"Authorization": f"Bearer {SUNO_API_KEY}", "Content-Type": "application/json"}

    # Custom Mode сначала (если провайдер разрешает)
    custom_payload = {
        "customMode": True,
        "instrumental": False,
        "title": title,
        "style": style,
        "prompt": lyrics,  # в custom prompt=LYRICS
        "callBackUrl": f"{PUBLIC_BASE_URL}/suno/callback",
        "model": "V4_5"
    }
    async with session(45) as s:
        async with s.post(f"{SUNO_API_BASE}/api/v1/generate", headers=headers, data=json.dumps(custom_payload)) as r:
            body = await r.text()

    if 200 <= r.status < 300:
        try:
            j = json.loads(body)
            code = j.get("code")
            if code in (None, 200):
                task_id = (j.get("data") or {}).get("taskId") or j.get("taskId")
                if task_id:
                    pending[task_id] = user_id
                    return task_id
        except Exception as e:
            print("Custom parse error -> fallback:", e)
    else:
        print(f"Custom HTTP {r.status}: {body}")

    # Фолбэк: Non-custom
    non_payload = {
        "customMode": False,
        "instrumental": False,
        "prompt": prompt[:400],
        "callBackUrl": f"{PUBLIC_BASE_URL}/suno/callback",
        "model": "V4_5"
    }
    async with session(30) as s:
        async with s.post(f"{SUNO_API_BASE}/api/v1/generate", headers=headers, data=json.dumps(non_payload)) as r2:
            body2 = await r2.text()

    if r2.status >= 400:
        raise RuntimeError(f"Generate HTTP {r2.status}: {body2}")

    try:
        j2 = json.loads(body2)
    except Exception:
        raise RuntimeError(f"Generate non-JSON: {body2[:300]}")

    code2 = j2.get("code")
    if code2 not in (None, 200):
        raise RuntimeError(f"Suno error code={code2}: {j2.get('msg') or j2.get('message') or body2}")

    task_id2 = (j2.get("data") or {}).get("taskId") or j2.get("taskId")
    if not task_id2:
        raise RuntimeError(f"Suno response without taskId: {j2}")

    pending[task_id2] = user_id
    return task_id2

async def poll_and_send(task_id: str, user_id: int, timeout_s: int = 420):
    """Параллельный поллинг record-info до 7 минут, шлём все найденные версии."""
    url = f"{SUNO_API_BASE}/api/v1/generate/record-info"
    headers = {"Authorization": f"Bearer {SUNO_API_KEY}"}
    deadline = asyncio.get_event_loop().time() + timeout_s
    sent_any = False

    async with session(20) as s:
        while asyncio.get_event_loop().time() < deadline:
            await asyncio.sleep(5)
            try:
                async with s.get(url, headers=headers, params={"taskId": task_id}) as r:
                    body = await r.text()
                    if r.status >= 400:
                        continue
                    j = json.loads(body)
                links = _extract_mp3s(j.get("data"))
                for idx, link in enumerate(links[:4], start=1):  # перестраховка — максимум 4
                    await bot.send_audio(user_id, link, caption=f"Версия {idx} 🎵")
                    sent_any = True
                if sent_any:
                    return
            except Exception:
                continue

# ====== CALLBACK ======
async def suno_callback(request: web.Request):
    try:
        body = await request.json()
    except Exception:
        raw = await request.text()
        print("CALLBACK non-JSON:", raw[:500])
        return web.json_response({"ok": False}, status=400)

    print("CALLBACK:", json.dumps(body)[:1000])
    task_id = body.get("taskId") or (body.get("data") or {}).get("taskId")
    user_id = pending.get(task_id)

    links = _extract_mp3s(body)
    if user_id and links:
        for idx, link in enumerate(links[:4], start=1):
            await bot.send_audio(user_id, link, caption=f"Версия {idx} 🎵")
    else:
        if user_id and task_id:
            await asyncio.sleep(5)
            await poll_and_send(task_id, user_id, timeout_s=30)
    return web.json_response({"ok": True})

# ====== Aiohttp app ======
def make_app():
    app = web.Application()
    app.router.add_get("/", lambda request: web.json_response({"status": "ok"}))
    app.router.add_post("/suno/callback", suno_callback)
    return app

# ====== ENTRY ======
async def main():
    if not (BOT_TOKEN and OPENAI_API_KEY and SUNO_API_KEY and PUBLIC_BASE_URL.startswith("https://")):
        raise SystemExit("Проверь BOT_TOKEN/OPENAI_API_KEY/SUNO_API_KEY и PUBLIC_BASE_URL=https://...")

    # на всякий случай отключим webhook, чтобы polling не конфликтовал
    try:
        await bot.delete_webhook(drop_pending_updates=False)
    except Exception:
        pass

    web_app = make_app()
    loop = asyncio.get_event_loop()
    # аккуратно стартуем web-сервер
    try:
        loop.create_task(web._run_app(web_app, host="127.0.0.1", port=HTTP_PORT))
        print(f"[health] http://127.0.0.1:{HTTP_PORT}/  -> {{\"status\":\"ok\"}}")
    except OSError as e:
        if getattr(e, "errno", None) == 98:
            print(f"[warn] порт {HTTP_PORT} уже занят — пропускаю запуск web-сервера")
        else:
            raise

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
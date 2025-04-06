import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from agents.code_refactor import generate_patch_review
import os
import sys
import json
import time
import subprocess
from datetime import datetime
from goal_pipeline import process_scan, process_accept, process_reject, get_status
from dotenv import load_dotenv
from agents.code_refactor import (
    generate_all_reviews_markdown,
    send_review_markdown_to_telegram
)
sys.path.append(os.path.abspath("."))
from utils.gpt_sanitizer import split_into_safe_chunks

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

def safe_patch_slice(patch_text, max_chars=3000):
    lines = patch_text.splitlines(keepends=True)
    result = ""
    total = 0
    for line in lines:
        if total + len(line) > max_chars:
            break
        result += line
        total += len(line)
    return result

def saci_run(module: str):
    try:
        subprocess.Popen(["python", "-m", module])
    except Exception as e:
        print(f"❌ Ошибка запуска модуля {module}: {e}")

def send_long_text(chat_id, header, body, chunk_limit=3900):
    paragraphs = body.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_limit:
            current += para + "\n\n"
        else:
            chunks.append(current.strip())
            current = para + "\n\n"
    if current:
        chunks.append(current.strip())

    for i, chunk in enumerate(chunks):
        prefix = f"{header} (часть {i+1}/{len(chunks)}):\n\n" if len(chunks) > 1 else f"{header}\n\n"
        bot.send_message(chat_id, prefix + chunk)

@bot.message_handler(commands=['panel'])
def patch_panel(message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📄 Просмотр последнего", callback_data="review:last"),
        InlineKeyboardButton("✅ Применить", callback_data="apply:last")
    )
    markup.row(
        InlineKeyboardButton("🧪 Протестировать патч", callback_data="test:last")
    )   

    markup.row(
        InlineKeyboardButton("🧠 Architect", callback_data="review_agent:last:architect"),
        InlineKeyboardButton("👨‍💻 Developer", callback_data="review_agent:last:developer"),
        InlineKeyboardButton("🎯 Strategist", callback_data="review_agent:last:strategist")
    )
    markup.row(
        InlineKeyboardButton("📘 Лог ревью", callback_data="review_file:last"),
        InlineKeyboardButton("🔄 Перегенерировать", callback_data="refactor:latest"),
        InlineKeyboardButton("⏹ Остановить", callback_data="stop:auto")
    )
    bot.send_message(
        message.chat.id,
        "🛠 SACI ПАНЕЛЬ: выбери действие с последним патчем:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    import glob
    data = call.data

    def get_latest_patch_name():
        patch_files = sorted([
            f.replace(".patch", "").replace(".diff", "")
            for f in os.listdir("patches")
            if f.endswith((".patch", ".diff"))
        ])
        return patch_files[-1] if patch_files else None

    if data == "stop:auto":
        with open(".saci_stop", "w") as f:
            f.write("stop")
        bot.send_message(call.message.chat.id, "🛑 AutoLoop остановлен.")

    elif data == "test:last":
        bot.send_message(call.message.chat.id, "🧪 Запускаю тесты...")
        import subprocess
        try:
            result = subprocess.run(
                ["python", "-m", "unittest", "discover", "tests"],
                capture_output=True, text=True
            )
            output = result.stdout + result.stderr
            if len(output) > 3900:
                output = output[:3900] + "\n...\n[обрезано]"
            bot.send_message(call.message.chat.id, f"🧪 Результат:\n\n{output}")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Ошибка запуска тестов: {e}")

    elif data == "refactor:latest":
        bot.send_message(call.message.chat.id, "🔄 Запускаю multi-pass GPT рефакторинг...")
        subprocess.Popen(["python", "-m", "agents.code_refactor", "multi"], shell=False)

    elif data == "review_file:last":
        files = sorted(glob.glob("logs/patch_reviews/*.md"))
        if files:
            with open(files[-1], "rb") as f:
                bot.send_document(call.message.chat.id, f, caption="📘 Последнее ревью всех агентов")
        else:
            bot.send_message(call.message.chat.id, "⚠️ Ревью не найдено.")

    elif data.startswith("review:last") or data.startswith("apply:last") or data.startswith("review_agent:last"):
        latest = get_latest_patch_name()
        if not latest:
            bot.send_message(call.message.chat.id, "❌ Нет доступных патчей.")
            return

        if data.startswith("review:last"):
            call.data = f"review:{latest}"
        elif data.startswith("apply:last"):
            call.data = f"apply:{latest}"
        elif data.startswith("review_agent:last"):
            agent = data.split(":")[-1]
            call.data = f"review_agent:{latest}:{agent}"
        handle_callback(call)

    elif data.startswith("review:"):
        patch = data.split(":")[1]
        for ext in [".patch", ".diff"]:
            path = f"patches/{patch}{ext}"
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                    preview = text[:3900] + "\n...\n[усечено]" if len(text) > 3900 else text
                bot.send_message(call.message.chat.id, f"📄 Patch `{patch}`:\n\n{preview}")
                return
        bot.send_message(call.message.chat.id, "❌ Patch не найден.")

    elif data.startswith("apply:"):
        patch = data.split(":")[1]
        for ext in [".patch", ".diff"]:
            path = f"patches/{patch}{ext}"
            if os.path.exists(path):
                os.system(f"git apply {path}")
                bot.send_message(call.message.chat.id, f"✅ Патч `{patch}` применён.")

                # Генерация ревью и отправка
                generate_all_reviews_markdown(patch)
                send_review_markdown_to_telegram(patch)

                markup = InlineKeyboardMarkup()
                markup.add(
                    InlineKeyboardButton("👍 Да, согласовано", callback_data=f"agree:{patch}"),
                    InlineKeyboardButton("👎 Нет", callback_data=f"reject:{patch}")
                )
                bot.send_message(call.message.chat.id, "Согласовать патч и внести в журнал целей?", reply_markup=markup)
                return
        bot.send_message(call.message.chat.id, "❌ Patch не найден.")

    elif data.startswith("agree:"):
        patch = data.split(":")[1]
        log_path = "logs/goals_log.json"
        log = []
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                log = json.load(f)

        log.append({
            "type": "patch",
            "patch": patch,
            "status": "applied",
            "agreed": True,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=4, ensure_ascii=False)
        bot.send_message(call.message.chat.id, "📘 Патч зафиксирован в журнале.")

    elif data.startswith("reject:"):
        bot.send_message(call.message.chat.id, "🚫 Патч не зафиксирован.")

    elif data.startswith("review_agent:"):
        _, patch, agent = data.split(":")
        review_text = generate_patch_review(patch, agent)

        for chunk in split_into_safe_chunks(review_text):
            bot.send_message(call.message.chat.id, f"🧠 {agent.title()}:\n\n{chunk}")

@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        KeyboardButton("/scan"),
        KeyboardButton("/status")
    )
    markup.row(
        KeyboardButton("/accept"),
        KeyboardButton("/reject")
    )
    markup.row(
        KeyboardButton("/analyze all"),
        KeyboardButton("/refactor")
    )
    markup.row(
        KeyboardButton("/summary"),
        KeyboardButton("/log last")
    )
    bot.send_message(
        message.chat.id,
        "Привет. Я SACI Telegram Interface.\n\nКоманды:\n"
        "/scan — начать анализ\n"
        "/accept — принять цель\n"
        "/reject — отклонить\n"
        "/status — текущее состояние\n"
        "/analyze all — анализ кода\n"
        "/refactor — предложить патч\n"
        "/summary — дневной отчёт\n"
        "/log last — последнее действие",
        reply_markup=markup
    )
@bot.message_handler(commands=['scan'])
def scan(message):
    result = process_scan()
    bot.send_message(message.chat.id, result)

@bot.message_handler(commands=['accept'])
def accept(message):
    result = process_accept()
    bot.send_message(message.chat.id, result)

@bot.message_handler(commands=['reject'])
def reject(message):
    result = process_reject()
    bot.send_message(message.chat.id, result)

@bot.message_handler(commands=['status'])
def status(message):
    result = get_status()
    bot.send_message(message.chat.id, result)

@bot.message_handler(commands=['summary'])
def summary(message):
    try:
        from agents.project_manager import generate_summary_rich
        text = generate_summary_rich()
        bot.send_message(message.chat.id, text)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка при генерации отчёта: {e}")

@bot.message_handler(commands=['stop'])
def stop(message):
    with open(".saci_stop", "w") as f:
        f.write("stop")
    bot.send_message(message.chat.id, "🛑 Автопоток SACI остановлен.")

@bot.message_handler(commands=['analyze'])
def analyze(message):
    text = message.text.strip()
    if "all" in text:
        bot.send_message(message.chat.id, "📡 Запускаю полный анализ всех файлов...")
        subprocess.Popen("python agents/code_analyst.py all", shell=True)
    else:
        bot.send_message(message.chat.id, "🔍 Запускаю анализ ключевых модулей...")
        subprocess.Popen("python agents/code_analyst.py", shell=True)

@bot.message_handler(commands=['apply'])
def apply_patch(message):
    try:
        name = message.text.replace("/apply patch", "").strip()
        patch_variants = [
            f"patches/{name}.diff",
            f"patches/{name}.patch"
        ]

        patch_path = next((p for p in patch_variants if os.path.exists(p)), None)

        if not patch_path:
            all_patches = "\n".join(os.listdir("patches"))
            bot.send_message(message.chat.id, f"❌ Патч `{name}` не найден.\n\n📂 В наличии:\n{all_patches}")
            return

        os.system(f"git apply {patch_path}")
        bot.send_message(message.chat.id, f"✅ Патч `{os.path.basename(patch_path)}` применён.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка применения патча: {e}")

@bot.message_handler(commands=['review'])
def review_patch(message):
    try:
        text = message.text.replace("/review patch", "").strip()
        patch_path = f"patches/{text}.diff"

        if not os.path.exists(patch_path):
            bot.send_message(message.chat.id, f"❌ Патч `{text}` не найден.")
            return

        with open(patch_path, "r", encoding="utf-8") as f:
            patch_text = f.read()

        # Telegram ограничен 4096 символами
        if len(patch_text) > 3900:
            patch_text = patch_text[:3900] + "\n...\n[усечено]"

        bot.send_message(message.chat.id, f"📄 Patch `{text}`:\n\n{patch_text}")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка чтения патча: {e}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    data = call.data

    if data.startswith("review:"):
        patch = data.split(":", 1)[1]
        path = f"patches/{patch}.patch"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()[:3900]
            bot.send_message(call.message.chat.id, f"📄 Patch `{patch}`:\n\n{content}")
        else:
            bot.send_message(call.message.chat.id, "❌ Patch не найден.")

    elif data == "stop:auto":
        with open(".saci_stop", "w") as f:
            f.write("stop")
        bot.send_message(call.message.chat.id, "🛑 AutoLoop остановлен.")

    elif data == "refactor:latest":
        bot.send_message(call.message.chat.id, "🔄 Перегенерирую патч...")
        subprocess.Popen(["python", "-m", "agents.code_refactor"])

    elif data == "review_file:last":
        import glob
        latest = sorted(glob.glob("logs/patch_reviews/*.md"))[-1]
        if latest:
            with open(latest, "rb") as f:
                bot.send_document(call.message.chat.id, f, caption="📘 Последнее ревью")
        else:
            bot.send_message(call.message.chat.id, "⚠️ Ревью не найдено.")

    elif data.startswith("review:last"):
        latest = sorted(os.listdir("patches"))[-1].replace(".patch", "").replace(".diff", "")
        call.data = f"review:{latest}"
        handle_callback(call)

    elif data.startswith("apply:last"):
        latest = sorted(os.listdir("patches"))[-1].replace(".patch", "").replace(".diff", "")
        call.data = f"apply:{latest}"
        handle_callback(call)

    elif data.startswith("review_agent:last"):
        _, _, agent = data.split(":")
        latest = sorted(os.listdir("patches"))[-1].replace(".patch", "").replace(".diff", "")
        call.data = f"review_agent:{latest}:{agent}"
        handle_callback(call)

    elif data.startswith("apply:"):
        patch = data.split(":")[1]
        patch_path = None
        for ext in [".patch", ".diff"]:
            candidate = f"patches/{patch}{ext}"
            if os.path.exists(candidate):
                patch_path = candidate
                break

        if patch_path:
            os.system(f"git apply {patch_path}")
            bot.send_message(call.message.chat.id, f"✅ Патч `{patch}` применён.")

            # 📄 Сгенерировать .md ревью от всех агентов
            generate_all_reviews_markdown(patch)
            send_review_markdown_to_telegram(patch)

            # 👍 Предложить согласование
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("👍 Да, согласовано", callback_data=f"agree:{patch}"),
                InlineKeyboardButton("👎 Нет", callback_data=f"reject:{patch}")
            )
            bot.send_message(call.message.chat.id, "Согласовать патч и внести в журнал целей?", reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, "❌ Patch не найден.")

    elif data.startswith("review_agent:"):
        _, patch, agent = data.split(":")
        review = generate_patch_review(patch, agent)
        send_long_text(call.message.chat.id, f"🧠 Ревью от {agent.title()}:", review)

    elif data.startswith("view_rev:"):
        _, patch, agent = data.split(":")
        review = generate_patch_review(patch, agent)
        send_long_text(chat_id=call.message.chat.id, header=f"🧠 Ревью от {agent.title()}:", body=review)

print("🤖 SACI Telegram Bot запущен.")
bot.polling()

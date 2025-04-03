# ✅ main.py (отремонтированная версия)
import os
import re
import subprocess
import logging
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
import openai

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from core.saci_protocol import SACIProtocol
from agents.strategist import Strategist
from agents.architect import Architect
from agents.project_manager import ProjectManager
from agents.developer import Developer
from agents.tester import Tester
from agents.deployer import Deployer
from agents.metrics_master import MetricsMaster

# === SETUP ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GITHUB_REPO_PATH = os.getenv("GITHUB_REPO_PATH", ".")

# === ЛОГИ ===
logging.basicConfig(filename="agent.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
user_states = {}

# === ФИЛЬТРАЦИЯ ===
FORBIDDEN_KEYWORDS = ["os.remove", "shutil.rmtree", "eval", "exec", "subprocess", "open("]

def is_description_safe(description: str) -> bool:
    return not any(keyword in description.lower() for keyword in FORBIDDEN_KEYWORDS)

def bootstrap_workspace():
    for folder in ["modules", "core", "tests", "logs", "__pycache__"]:
        Path(folder).mkdir(parents=True, exist_ok=True)
    Path(".gitignore").write_text(".env\n__pycache__/\nlogs/\nagent.log\n", encoding="utf-8")
    Path("README.md").write_text("# ChatGPT-Agent\n\nАвтоматический Telegram-бот для генерации Python-модулей и деплоя.\n", encoding="utf-8")

def strip_markdown(content: str) -> str:
    match = re.search(r"```python(.*?)```", content, re.DOTALL)
    return match.group(1).strip() if match else content.strip()

def inject_project_root_path(code: str) -> str:
    if "sys.path.append" in code:
        return code
    return (
        "import sys, os\n"
        "sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))\n\n" + code
    )

async def process_new_module(description: str) -> str:
    if not is_description_safe(description):
        return "🚫 Описание содержит потенциально опасный код."

    prompt = f"""
    Ты — AI-разработчик. Сгенерируй Python-модуль строго в виде кода.
    Обязательно:
    - подробные комментарии
    - строка описания
    - валидный код без Markdown

    Описание: {description}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        raw = response['choices'][0]['message']['content']
        code = inject_project_root_path(strip_markdown(raw))
        filename = Path("modules/gen_module.py")
        filename.write_text(code, encoding="utf-8")

        try:
            subprocess.run(["git", "-C", GITHUB_REPO_PATH, "add", str(filename)], check=True)
            subprocess.run(["git", "-C", GITHUB_REPO_PATH, "commit", "-m", f"Add module: {description}"], check=True)
            subprocess.run(["git", "-C", GITHUB_REPO_PATH, "push"], check=True)
            git_result = "✅ Код запушен."
        except subprocess.CalledProcessError as e:
            logging.exception("Git push error")
            git_result = f"⚠️ Git ошибка: {e}"

        try:
            result = subprocess.run(["python", str(filename)], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return f"✅ Код выполнен.\n{git_result}\n📄 {result.stdout}"
            return f"⚠️ Выполнение завершилось с ошибкой:\n{git_result}\n❌ {result.stderr}"
        except subprocess.TimeoutExpired:
            return "⏱️ Код превысил лимит времени."

    except Exception as e:
        logging.exception("Ошибка генерации")
        return f"❌ Ошибка генерации: {e}"

# === TELEGRAM ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Я SACI-будда. Напиши /new_module чтобы начать.")

async def new_module(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = "AWAITING_MODULE_DESCRIPTION"
    await update.message.reply_text("✍️ Напиши описание модуля:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_states.get(user_id) == "AWAITING_MODULE_DESCRIPTION":
        await update.message.reply_text("🤖 Генерирую код...")
        result = await process_new_module(text)
        await update.message.reply_text(result)
        user_states[user_id] = None
    else:
        await update.message.reply_text("Напиши /new_module, чтобы начать.")

def main():
    bootstrap_workspace()
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("new_module", new_module))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Бот запущен")
    app.run_polling()

# === Sprint Execution ===
def run_sprint(goal: str, minutes: int):
    start_time = time.time()
    end_time = start_time + minutes * 60
    logging.info(f"🎯 Запуск спринта: {goal} на {minutes} мин")

    agents = [
        Strategist(), Architect(), ProjectManager(),
        Developer(), Tester(), Deployer(), MetricsMaster()
    ]
    iteration = 1
    data = {"goal": goal}

    while time.time() < end_time:
        logging.info(f"--- Итерация {iteration} ---")
        for agent in agents:
            data = agent.execute(data)
            logging.info(f"{agent.__class__.__name__} завершил итерацию.")
            try:
                requests.post(
                    f'https://api.telegram.org/bot{os.getenv("TELEGRAM_TOKEN")}/sendMessage',
                    data={
                        'chat_id': os.getenv('TELEGRAM_CHAT_ID'),
                        'text': f'{agent.__class__.__name__} завершил итерацию {iteration}.'
                    }
                )
            except Exception as e:
                logging.error(f"Telegram ошибка: {e}")
        iteration += 1

    logging.info("✅ Спринт завершён.")
    try:
        requests.post(
            f'https://api.telegram.org/bot{os.getenv("TELEGRAM_TOKEN")}/sendMessage',
            data={
                'chat_id': os.getenv('TELEGRAM_CHAT_ID'),
                'text': 'Спринт завершён.'
            }
        )
    except Exception as e:
        logging.error(f"Telegram ошибка: {e}")

if __name__ == "__main__":
    main()

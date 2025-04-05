import os
import json
import openai
import requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

openai.api_key = OPENAI_API_KEY

FILE_MAP_PATH = "logs/saci_file_map.json"
FILES_TO_ANALYZE = ["agents/developer.py", "agents/tester.py", "agents/goal_runner.py"]


def load_file_map():
    if not os.path.exists(FILE_MAP_PATH):
        return {}
    with open(FILE_MAP_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def analyze_code_with_gpt(filename, content):
    prompt = f"""
Ты — AI-код-ревьюер SACI. Проанализируй файл `{filename}`. Дай рекомендации по:
- улучшению архитектуры
- устранению повторов
- читаемости
- эффективности

Выведи кратко в виде списка с эмоджи:
{content[:3000]}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты — AI-архитектор SACI."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=600
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Ошибка GPT: {e}"

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("📬 Анализ отправлен в Telegram.")
    else:
        print(f"❌ Ошибка Telegram: {response.status_code} {response.text}")

def run_analysis(all_files=False):
    print("🧠 Запуск анализа кода...")
    file_map = load_file_map()
    if not file_map:
        send_to_telegram("⚠️ Файл saci_file_map.json не найден.")
        return

    files_to_process = file_map.keys() if all_files else FILES_TO_ANALYZE

    for filename in files_to_process:
        content = file_map.get(filename)
        if not content:
            continue

        print(f"🔍 Анализ: {filename}")
        result = analyze_code_with_gpt(filename, content)
        send_to_telegram(f"📄 Анализ `{filename}`:\n\n{result}")

if __name__ == "__main__":
    import sys
    run_analysis(all_files="all" in sys.argv)

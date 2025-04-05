import os
import json
import subprocess
import requests
from dotenv import load_dotenv

load_dotenv()

GOAL_STATE = "saci_goal_state.json"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"❌ Ошибка отправки в Telegram: {e}")

def run_tests():
    if not os.path.exists(GOAL_STATE):
        print("❌ Нет активной цели.")
        return

    with open(GOAL_STATE) as f:
        data = json.load(f)

    if data["status"] != "done":
        print("ℹ️ Цель ещё не завершена.")
        return

    if "test_patch_predictor.py" not in data["goal"]:
        print("ℹ️ Текущая цель не требует запуска тестов.")
        return

    print("🧪 Запуск unittest на tests/")
    result = subprocess.run(["python", "-m", "unittest", "discover", "tests"], capture_output=True, text=True)

    summary = "✅ Все тесты прошли успешно." if result.returncode == 0 else "❌ Обнаружены ошибки в тестах."

    report = f"""📊 *SACI Test Report*
🎯 Цель: {data['goal']}
📦 Файл: test_patch_predictor.py
📋 Результат: {"✅ PASSED" if result.returncode == 0 else "❌ FAILED"}
"""

    print(report)
    send_telegram_message(report)

if __name__ == "__main__":
    run_tests()

import json
import os
from datetime import datetime
import requests
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

GOAL_STATE = "saci_goal_state.json"
GOAL_LOG = "logs/goals_log.json"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def log_current_goal():
    if not os.path.exists(GOAL_STATE):
        return

    with open(GOAL_STATE) as f:
        goal_data = json.load(f)

    goal_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    if not os.path.exists(GOAL_LOG):
        log = []
    else:
        with open(GOAL_LOG) as f:
            log = json.load(f)

    log.append(goal_data)

    with open(GOAL_LOG, "w") as f:
        json.dump(log, f, indent=4, ensure_ascii=False)

    print("📘 Цель зафиксирована в журнале.")

def extract_filename_from_goal(goal):
    words = goal.split()
    for word in words:
        if word.endswith((".py", ".md", ".json", ".yml", ".yaml")):
            return word
    return None

def generate_summary_rich():
    if not os.path.exists(GOAL_LOG):
        return "Нет журналов целей для анализа."

    with open(GOAL_LOG) as f:
        log = json.load(f)

    today = datetime.now().strftime("%Y-%m-%d")
    today_goals = [g for g in log if g['timestamp'].startswith(today)]

    if not today_goals:
        return "Сегодня ещё не было активности."

    statuses = Counter(g["status"] for g in today_goals)
    all_goals = [g["goal"] for g in today_goals]
    files = [extract_filename_from_goal(g["goal"]) for g in today_goals if extract_filename_from_goal(g["goal"])]
    extensions = [os.path.splitext(f)[-1] for f in files if f]

    # Находим повторяющиеся цели
    repeated = [item for item, count in Counter(all_goals).items() if count > 1]

    summary = f"""📊 SACI /summary — {today}

🎯 Целей за день: {len(today_goals)}
✅ Выполнено: {statuses.get('complete', 0)}
⚠️ Повторы целей: {len(repeated)}
📁 Новых файлов: {len(set(files))}
📂 Типы: {', '.join(sorted(set(extensions))) or '—'}

📌 Последняя цель: {today_goals[-1]['goal']}
🕒 Время последней активности: {today_goals[-1]['timestamp']}
"""

    return summary

def send_summary_to_telegram():
    summary = generate_summary_rich()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": summary}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("📬 Дневной отчёт отправлен в Telegram.")
    else:
        print(f"❌ Ошибка Telegram: {response.status_code} {response.text}")

if __name__ == "__main__":
    log_current_goal()
    send_summary_to_telegram()

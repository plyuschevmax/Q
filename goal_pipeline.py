import os
import json
import subprocess
from agents.architect import analyze_repo_and_suggest_goal

GOAL_STATE = "saci_goal_state.json"

def archive_completed_goal():
    if not os.path.exists(GOAL_STATE):
        return
    with open(GOAL_STATE) as f:
        goal_data = json.load(f)
    if goal_data.get("status") == "complete":
        print("📦 Архивируем завершённую цель.")
        subprocess.run(["python", "agents/project_manager.py"])
        os.remove(GOAL_STATE)

def process_scan():
    try:
        archive_completed_goal()

        # 1. Скан проекта
        subprocess.run(["python", "saci_remote_agent.py"])
        print("✅ Структура собрана.")

        # 2. Генерация цели
        goal = analyze_repo_and_suggest_goal()
        goal_data = {
            "goal": goal,
            "status": "in_progress",
            "timestamp": subprocess.getoutput("date '+%Y-%m-%d %H:%M'"),
            "dev_done": False,
            "test_done": False
        }
        with open(GOAL_STATE, "w") as f:
            json.dump(goal_data, f, indent=4, ensure_ascii=False)
        print(f"🎯 Цель сформирована: {goal}")

        # 3. Запуск goal_runner.py в фоне
        subprocess.Popen("python agents/goal_runner.py", shell=True)
        return f"✅ Цикл запущен.\n🎯 Цель: {goal}"

    except Exception as e:
        return f"❌ Ошибка в process_scan: {e}"

def process_accept():
    if not goal_exists(): return "Нет активной цели."
    update_goal_status("in_progress")
    return "✅ Цель принята. Передаём агенту на исполнение..."

def process_reject():
    if not goal_exists(): return "Нет цели для отклонения."
    update_goal_status("rejected")
    return "🚫 Цель отклонена."

def get_status():
    if not goal_exists(): return "Нет активной цели."
    with open(GOAL_STATE) as f:
        data = json.load(f)
    return f"📌 Статус цели: {data['status']}\n🎯 Цель: {data['goal']}"

def goal_exists():
    return os.path.exists(GOAL_STATE)

def update_goal_status(new_status):
    with open(GOAL_STATE) as f:
        data = json.load(f)
    data["status"] = new_status
    with open(GOAL_STATE, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    print(process_scan())

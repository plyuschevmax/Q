import subprocess
import time
import json
import os
from agents.architect import analyze_repo_and_suggest_goal

GOAL_STATE = "saci_goal_state.json"
STOP_FILE = ".saci_stop"
GOAL_LOG = "logs/goals_log.json"

def archive_completed():
    if not os.path.exists(GOAL_STATE):
        return
    with open(GOAL_STATE) as f:
        goal = json.load(f)
    if goal.get("status") == "complete":
        subprocess.run(["python", "agents/project_manager.py"])
        os.remove(GOAL_STATE)
        print("📦 Завершённая цель заархивирована.")

def already_done(goal_text):
    if not os.path.exists(GOAL_LOG):
        return False
    with open(GOAL_LOG) as f:
        log = json.load(f)
    return any(goal_text in g.get("goal", "") for g in log)

def create_new_goal():
    subprocess.run(["python", "saci_remote_agent.py"])
    goal = analyze_repo_and_suggest_goal()
    if already_done(goal):
        print(f"⚠️ Цель уже выполнялась: {goal} — пропускаем.")
        return False
    goal_data = {
        "goal": goal,
        "status": "in_progress",
        "timestamp": subprocess.getoutput("date '+%Y-%m-%d %H:%M'"),
        "dev_done": False,
        "test_done": False
    }
    with open(GOAL_STATE, "w") as f:
        json.dump(goal_data, f, indent=4, ensure_ascii=False)
    print(f"🎯 Новая цель: {goal}")
    return True

def run_chain():
    subprocess.run(["python", "agents/developer.py"])
    subprocess.run(["python", "agents/tester.py"])
    subprocess.run(["python", "agents/project_manager.py"])
    with open(GOAL_STATE) as f:
        goal_data = json.load(f)
    goal_data["status"] = "complete"
    with open(GOAL_STATE, "w") as f:
        json.dump(goal_data, f, indent=4)
    print("✅ Цикл завершён.")

def auto_loop():
    print("🔁 Запуск SACI AutoLoop v2.0")
    while True:
        if os.path.exists(STOP_FILE):
            print("🛑 Получен сигнал остановки. Цикл завершён.")
            break
        archive_completed()
        success = create_new_goal()
        if success:
            run_chain()
        else:
            print("⏳ Ждём 60 секунд перед новой попыткой...\n")
            time.sleep(60)

if __name__ == "__main__":
    auto_loop()

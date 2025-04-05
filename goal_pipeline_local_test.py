import json
import subprocess
from agents.architect import analyze_repo_and_suggest_goal
import os


GOAL_STATE = "saci_goal_state.json"

def process_scan():
    try:
        subprocess.run(["python", "saci_remote_agent.py"])
        print("✅ saci_remote_agent.py завершён")

        goal = analyze_repo_and_suggest_goal()
        with open(GOAL_STATE, "w") as f:
            json.dump({"status": "pending", "goal": goal}, f, indent=4)

        print(f"\n🎯 Предлагаемая цель:\n{goal}\n")
        return True

    except Exception as e:
        print(f"❌ Ошибка в process_scan: {e}")
        return False

def show_goal_status():
    if not os.path.exists(GOAL_STATE):
        print("Нет активной цели.")
        return
    with open(GOAL_STATE) as f:
        data = json.load(f)
    print(f"\n📌 Текущий статус: {data['status']}\n🎯 Цель: {data['goal']}")

if __name__ == "__main__":
    print("▶️ Запуск локального теста SACI Goal Pipeline...\n")
    success = process_scan()
    if success:
        show_goal_status()

import os
import json
import subprocess
import time

GOAL_STATE = "saci_goal_state.json"

def load_goal():
    if not os.path.exists(GOAL_STATE):
        return None
    with open(GOAL_STATE) as f:
        return json.load(f)

def save_goal(data):
    with open(GOAL_STATE, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def run_cycle():
    while True:
        goal_data = load_goal()
        if not goal_data:
            print("⏳ Ожидание новой цели...")
            time.sleep(10)
            continue

        status = goal_data.get("status", "")
        goal = goal_data.get("goal", "").lower()

        print(f"📍 Статус цели: {status}")

        if status == "in_progress":
            if "test" in goal and not goal_data.get("dev_done"):
                print("👨‍💻 Запуск developer.py")
                subprocess.run(["python", "agents/developer.py"])
            elif "test" in goal and not goal_data.get("test_done"):
                print("🧪 Запуск tester.py")
                subprocess.run(["python", "agents/tester.py"])
            elif "test" in goal and goal_data.get("dev_done") and goal_data.get("test_done"):
                print("📘 Завершаем цикл через project_manager")
                subprocess.run(["python", "agents/project_manager.py"])
                goal_data["status"] = "complete"
                save_goal(goal_data)

        elif status == "done":
            print("📘 Завершаем цикл (без тестов) через project_manager")
            subprocess.run(["python", "agents/project_manager.py"])
            goal_data["status"] = "complete"
            save_goal(goal_data)

        else:
            print(f"📌 Текущий статус: {status} → ожидание...")

        time.sleep(5)

if __name__ == "__main__":
    run_cycle()

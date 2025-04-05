import json
from datetime import datetime

GOAL_STATE = "saci_goal_state.json"

goal = {
    "goal": "Добавить тестовый модуль: tests/test_patch_predictor.py",
    "status": "complete",
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "dev_done": True,
    "test_done": True
}

with open(GOAL_STATE, "w", encoding="utf-8") as f:
    json.dump(goal, f, indent=4, ensure_ascii=False)

print("✅ saci_goal_state.json успешно обновлён.")

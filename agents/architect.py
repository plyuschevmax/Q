import json


def analyze_repo_and_suggest_goal():
    with open("logs/saci_project_map.json") as f:
        structure = json.load(f)

    if "tests" in structure and not structure["tests"]:
        return "Добавить тестовый модуль: tests/test_patch_predictor.py"

    if "agents" in structure and "agent_hub.py" not in structure["agents"]:
        return "Создать agent_hub.py — координатор между стратегами, девелопером и тестером"

    return (
        "Оптимизировать структуру core/ и создать saci_memory.py для хранения состояния"
    )

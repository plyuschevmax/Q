import os
import json
from datetime import datetime

LOG_PATH = "logs/code_metrics.json"

def collect_code_metrics():
    total_lines = 0
    file_count = 0
    for root, _, files in os.walk("."):
        if any(x in root for x in ["venv", "__pycache__", "node_modules", "logs"]):
            continue
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    total_lines += len(lines)
                    file_count += 1
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "files": file_count,
        "lines": total_lines
    }

def append_to_log(metrics):
    os.makedirs("logs", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            log = json.load(f)
    else:
        log = []
    log.append(metrics)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)

def show_growth():
    if not os.path.exists(LOG_PATH):
        print("Нет сохранённых метрик.")
        return
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        log = json.load(f)
    if len(log) < 2:
        print("Недостаточно данных для анализа роста.")
        return

    last = log[-1]
    prev = log[-2]
    delta_lines = last["lines"] - prev["lines"]
    delta_files = last["files"] - prev["files"]

    print(f"📊 Рост кода с последнего запуска:")
    print(f"+ {delta_files} файлов")
    print(f"+ {delta_lines} строк")

if __name__ == "__main__":
    metrics = collect_code_metrics()
    append_to_log(metrics)
    print(f"📦 Строк: {metrics['lines']} в {metrics['files']} файлах")
    show_growth()

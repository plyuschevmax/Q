import os
import subprocess
import json
from datetime import datetime
from dotenv import load_dotenv
import openai

# Загрузка .env и API-ключа
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_patch():
    # Проверка изменений в git
    status = subprocess.run(["git", "status", "--porcelain"], stdout=subprocess.PIPE)
    if not status.stdout.strip():
        print("ℹ️ Нет изменений для патча.")
        return None

    # Генерация патча
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    patch_dir = "patches"
    os.makedirs(patch_dir, exist_ok=True)
    patch_path = os.path.join(patch_dir, f"auto_patch_{timestamp}.patch")

    with open(patch_path, "w") as f:
        subprocess.run(["git", "diff"], stdout=f)

    print(f"📦 Патч сохранён: {patch_path}")
    analyze_patch_with_gpt(patch_path, timestamp)
    return patch_path


def analyze_patch_with_gpt(patch_path, timestamp):
    with open(patch_path, "r", encoding="utf-8") as f:
        diff = f.read()

    prompt = f"""
Ты — AI-аналитик SACI. На основе git diff определи:
- "type": feature, bugfix, refactor, doc, config, test
- "risk_score": от 0.0 до 1.0
- "conflict_probability": от 0.0 до 1.0
- "summary": краткое описание сути изменений

Ответ верни в JSON. Вот diff:
```diff
    {diff}
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты — AI-аналитик SACI."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=500,
        )

        reply = response["choices"][0]["message"]["content"]
        prediction = json.loads(reply)
        prediction["timestamp"] = timestamp

        # Сохраняем прогноз
        os.makedirs("logs", exist_ok=True)
        with open("logs/commit_meta.json", "w", encoding="utf-8") as f:
            json.dump(prediction, f, indent=4)

        print("🧠 GPT-анализ готов.")
        update_saci_log(prediction)

    except Exception as e:
        print(f"❌ Ошибка GPT-анализа: {e}")


def update_saci_log(prediction):
    entry = f"""
### 🧠 SACI-Agent
🕒 {prediction['timestamp']}
🎯 {prediction['summary']}
🧠 Тип: {prediction['type']}
⚠️ Риск: {prediction['risk_score']}
🔁 Конфликт: {prediction['conflict_probability']}
—
"""
    log_file = "SACI_LOG_TEMPLATE.md"
    if not os.path.exists(log_file):
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("# SACI Commit Log 📘\n\n")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)

    print("📌 SACI_LOG_TEMPLATE.md обновлён.")

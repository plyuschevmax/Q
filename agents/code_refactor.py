import os
import json
import openai
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from dotenv import load_dotenv
import subprocess  # для автоматического запуска remote_agent / splitter
import sys
import os

sys.path.append(os.path.abspath("."))


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

openai.api_key = OPENAI_API_KEY

FILE_MAP_PATH = "logs/saci_file_map.json"
PATCH_DIR = "patches"

CHUNKS_PATH = "logs/saci_code_chunks.json"


def safe_patch_slice(text, max_chars=2500):
    lines = text.splitlines(keepends=True)
    result = ""
    total = 0
    for line in lines:
        if total + len(line) > max_chars:
            break
        result += line
        total += len(line)
    return result


def run_multi_pass_refactor():
    subprocess.run(["python", "saci_remote_agent.py"])

    with open("logs/saci_code_chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)

    batches = split_chunks_into_batches(chunks, batch_size=10)
    combined_diff = ""
    print(f"🔁 Обработка {len(batches)} batch'ей...")

    for i, batch in enumerate(batches):
        print(f"📦 Batch {i+1}/{len(batches)}")
        diff = request_gpt_patch(batch)
        combined_diff += diff + "\n\n"

    # Save combined patch
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"auto_gpt_patch_{ts}_combined.patch"
    path = os.path.join("patches", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(combined_diff)

    print(f"✅ Объединённый патч сохранён: {filename}")
    send_patch_with_buttons(filename)


def split_chunks_into_batches(chunks: dict, batch_size: int = 25):
    keys = list(chunks.keys())
    return [
        dict((k, chunks[k]) for k in keys[i : i + batch_size])
        for i in range(0, len(keys), batch_size)
    ]


def generate_all_reviews_markdown(patch_name):
    agents = {
        "architect": "🧠 Architect",
        "developer": "👨‍💻 Developer",
        "tester": "🧪 Tester",
        "strategist": "🎯 Strategist",
    }

    md = f"# 🔍 Patch Review — `{patch_name}`\n\n---\n"

    for agent_key, emoji_title in agents.items():
        review = generate_patch_review(patch_name, agent_key)
        md += f"\n## {emoji_title}\n\n{review}\n\n---\n"

    os.makedirs("logs/patch_reviews", exist_ok=True)
    path = f"logs/patch_reviews/{patch_name}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)

    return path


def send_review_markdown_to_telegram(patch_name):
    path = f"logs/patch_reviews/{patch_name}.md"
    if not os.path.exists(path):
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(path, "rb") as doc:
        files = {"document": doc}
        data = {
            "chat_id": CHAT_ID,
            "caption": f"📄 Общее ревью от всех агентов по `{patch_name}`",
            "parse_mode": "Markdown",
        }
        requests.post(url, files=files, data=data)


def generate_patch_review(patch_name, agent="architect"):
    patch_path = None
    for ext in [".patch", ".diff"]:
        path = f"patches/{patch_name}{ext}"
        if os.path.exists(path):
            patch_path = path
            break

    if not patch_path:
        return "❌ Patch не найден."

    with open(patch_path, "r", encoding="utf-8") as f:
        patch_text = f.read()

    persona = {
        "architect": "Ты — архитектурный AI, оцениваешь стратегически.",
        "developer": "Ты — опытный Python-разработчик SACI.",
        "tester": "Ты — AI-тестировщик, ищешь слабые места.",
        "strategist": "Ты — AI-стратег, смотришь на пользу в будущем.",
    }.get(agent, "Ты — AI-помощник.")

    prompt = f"""
{persona}
Дай ревью на следующий patch (diff):
- Что улучшает?
- Какие плюсы?
- Есть ли риски?
{safe_patch_slice(patch_text)}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": persona},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=400,
    )

    return response["choices"][0]["message"]["content"].strip()


def generate_all_patch_reviews(patch_name):
    agents = ["architect", "developer", "tester", "strategist"]
    results = {}
    for agent in agents:
        review = generate_patch_review(patch_name, agent)
        results[agent] = review
    return results


def send_patch_with_reviews(filename):
    base = filename.replace(".patch", "").replace(".diff", "")
    reviews = generate_all_patch_reviews(base)

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📄 Просмотр patch", callback_data=f"review:{base}"),
        InlineKeyboardButton("✅ Применить", callback_data=f"apply:{base}"),
    )
    markup.row(
        InlineKeyboardButton(
            "🧠 Architect", callback_data=f"view_rev:{base}:architect"
        ),
        InlineKeyboardButton(
            "👨‍💻 Developer", callback_data=f"view_rev:{base}:developer"
        ),
        InlineKeyboardButton("🧪 Tester", callback_data=f"view_rev:{base}:tester"),
        InlineKeyboardButton(
            "🎯 Strategist", callback_data=f"view_rev:{base}:strategist"
        ),
    )

    review_text = "\n".join(
        [f"*{agent.title()}*:\n{review[:200]}" for agent, review in reviews.items()]
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": f"📦 GPT-патч `{filename}`\n\n🧠 Ревью агентов:\n\n{review_text}\n\nВыбери действие ниже:",
        "reply_markup": json.dumps(markup.to_dict()),
        "parse_mode": "Markdown",
    }
    requests.post(url, json=payload)


from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def send_patch_with_buttons(filename):
    base = filename.replace(".diff", "").replace(".patch", "")

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📄 Просмотреть", callback_data=f"review:{base}"),
        InlineKeyboardButton("✅ Применить", callback_data=f"apply:{base}"),
        InlineKeyboardButton(
            "🧠 Architect", callback_data=f"review_agent:{base}:architect"
        ),
        InlineKeyboardButton(
            "👨‍💻 Developer", callback_data=f"review_agent:{base}:developer"
        ),
        InlineKeyboardButton(
            "🎯 Strategist", callback_data=f"review_agent:{base}:strategist"
        ),
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": f"📦 GPT предложил патч: `{filename}`\n\n📎 Выбери действие:",
        "reply_markup": json.dumps(markup.to_dict()),
        "parse_mode": "Markdown",
    }

    requests.post(url, json=payload)


def load_chunks():
    # По умолчанию — Tree-sitter
    tree_chunks_path = "logs/saci_code_chunks.json"
    if os.path.exists(tree_chunks_path):
        with open(tree_chunks_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        print("⚠️ Чанки Tree-sitter не найдены. Используется старый split.")
        with open("logs/saci_file_map.json", "r", encoding="utf-8") as f:
            file_map = json.load(f)


# removed call to split_all_py_files (module was deleted)


def generate_patch_prompt(file_map):
    file_bundle = "\n\n".join(
        [
            f"### {fname}\n```python\n{content[:1500]}\n```"
            for fname, content in file_map.items()
            if fname.endswith(".py")
        ]
    )
    return f"""
Ты — AI-архитектор SACI. Проанализируй следующий код и предложи улучшения в формате unified diff (git diff).

Только один diff-файл со всеми изменениями. Внизу — краткие пояснения (1–2 предложения). Никаких лишних комментариев.

Вот код:
{file_bundle}
"""


def request_gpt_patch(chunks_batch):
    prompt = (
        "Ты — AI-архитектор. Вот чанки кода. Предложи patch в формате unified diff:\n\n"
    )
    for name, code in chunks_batch.items():
        sliced = code[:2000]
        prompt += f"### {name} ###\n```\n{sliced}\n```\n\n"
    prompt += "\nОтвети только git patch (unified diff), без markdown, без пояснений."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ты — AI-ревьюер. Верни только .diff patch."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=1200,
    )
    return response.choices[0].message.content.strip()


def priority_sort(name):
    if "goal_runner" in name:
        return 1
    if "developer" in name:
        return 2
    if "tester" in name:
        return 3
    if "core/" in name:
        return 4
    return 99


def save_patch(content):
    os.makedirs(PATCH_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"auto_gpt_patch_{ts}.diff"
    path = os.path.join(PATCH_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return filename, path


def is_patch_valid(content):
    return content.startswith("diff --git") and "@@" in content and "--- " in content


def repair_patch_with_gpt(content):
    print("🔧 Патч повреждён. Запрашиваем восстановление у GPT...")

    prompt = f"""
Ниже находится повреждённый или неполный git patch. Восстанови его в корректном формате unified diff. Без пояснений, только patch:
{content[:3000]}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ты — AI-патчер SACI. Исправляй git-patch."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=1000,
    )

    return response.choices[0].message.content.strip()


def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("📬 Сообщение отправлено в Telegram.")
    else:
        print(f"❌ Ошибка Telegram: {response.status_code} {response.text}")


def run_refactor():
    print("🔄 Обновляем кодовую базу перед анализом...")
    subprocess.run(["python", "saci_remote_agent.py"])

    print("🧠 GPT-анализ чанков кода...")
    chunks = load_chunks()
    if not chunks:
        send_to_telegram("⚠️ Нет чанков для анализа.")
        return

    patch = request_gpt_patch(chunks)
    if not patch:
        print("⚠️ GPT не вернул патч.")
        return

    patch_text = request_gpt_patch(chunks)
    if not is_patch_valid(patch_text):
        patch_text = repair_patch_with_gpt(patch_text)
        print("✅ Патч восстановлен GPT.")

    filename, path = save_patch(patch_text)

    send_patch_with_buttons(filename)


if __name__ == "__main__":
    import sys

    if "multi" in sys.argv:
        run_multi_pass_refactor()
    else:
        run_refactor()

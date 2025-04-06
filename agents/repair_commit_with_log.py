import os
import json
import openai
from datetime import datetime
from utils.gpt_sanitizer import safe_patch_slice
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

PATCH_DIR = "patches"
REPAIR_LOG = "logs/patch_repair_log.json"
REPAIRED_DIR = "patches"


def get_last_patch():
    patches = sorted(
        [f for f in os.listdir(PATCH_DIR) if f.endswith((".patch", ".diff"))]
    )
    return patches[-1] if patches else None


def is_patch_broken(text):
    return not text.startswith("diff --git") or "@@" not in text or "--- " not in text


def repair_patch_with_gpt(original_patch_text):
    prompt = f"""
Ты — AI-патчер. Вот повреждённый git patch.
Восстанови его в формате unified diff:
- Используй строки: diff --git, --- a/..., +++ b/...
- Не добавляй пояснений
- Только валидный patch ниже:

{safe_patch_slice(original_patch_text)}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ты — AI-патчер SACI."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=1000,
    )
    return response.choices[0].message.content.strip()


def write_log(patch_name, status, note=""):
    os.makedirs("logs", exist_ok=True)
    entry = {
        "patch": patch_name,
        "status": status,
        "note": note,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    log = []
    if os.path.exists(REPAIR_LOG):
        with open(REPAIR_LOG, "r", encoding="utf-8") as f:
            log = json.load(f)
    log.append(entry)
    with open(REPAIR_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def run_repair():
    patch_file = get_last_patch()
    if not patch_file:
        print("❌ Нет патчей для восстановления.")
        return

    path = os.path.join(PATCH_DIR, patch_file)
    with open(path, "r", encoding="utf-8") as f:
        original_patch = f.read()

    if not is_patch_broken(original_patch):
        print(f"✅ Патч {patch_file} валиден. Восстановление не требуется.")
        write_log(patch_file, "valid")
        return

    print(f"🔧 Патч {patch_file} повреждён. Запрашиваем GPT восстановление...")
    repaired = repair_patch_with_gpt(original_patch)

    repaired_name = patch_file.replace(".patch", "_repaired.patch").replace(
        ".diff", "_repaired.patch"
    )
    repaired_path = os.path.join(REPAIRED_DIR, repaired_name)

    with open(repaired_path, "w", encoding="utf-8") as f:
        f.write(repaired)

    print(f"✅ Восстановленный патч сохранён: {repaired_name}")
    write_log(patch_file, "repaired", note=f"saved as {repaired_name}")


if __name__ == "__main__":
    run_repair()

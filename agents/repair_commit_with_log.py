import os
import openai
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

PATCH_DIR = "patches"
REPAIRED_DIR = "patches/repaired"

def is_patch_broken(text):
    return not text.startswith("diff --git") or "@@" not in text or "--- " not in text

def fix_patch_with_gpt(bad_patch):
    prompt = f"""
Ниже находится повреждённый или неполный git patch. Восстанови его в корректном формате unified diff.
{bad_patch[:3000]}

Верни только исправленный diff. Без пояснений.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ты — AI-патчер SACI."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=1000
    )
    return response['choices'][0]['message']['content'].strip()

def run_patch_fix():
    os.makedirs(REPAIRED_DIR, exist_ok=True)

    for file in os.listdir(PATCH_DIR):
        if not file.endswith(".patch"):
            continue

        path = os.path.join(PATCH_DIR, file)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        if is_patch_broken(content):
            print(f"❌ Патч {file} повреждён. GPT восстанавливает...")
            fixed = fix_patch_with_gpt(content)
            repaired_path = os.path.join(REPAIRED_DIR, file)
            with open(repaired_path, "w", encoding="utf-8") as f:
                f.write(fixed)
            print(f"✅ Исправлено и сохранено: {repaired_path}")
        else:
            print(f"✅ Патч {file} в порядке.")

if __name__ == "__main__":
    run_patch_fix()

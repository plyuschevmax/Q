import os
import json
import re

FILE_MAP_PATH = "logs/saci_file_map.json"
CHUNK_OUTPUT = "logs/saci_code_chunks.json"

def split_py_file(name, code):
    chunks = {}
    lines = code.split('\n')
    current_chunk = []
    current_name = "header"
    indent_base = None

    for i, line in enumerate(lines):
        func_match = re.match(r'^def ([a-zA-Z0-9_]+)\(', line)
        class_match = re.match(r'^class ([a-zA-Z0-9_]+)', line)

        if func_match or class_match:
            # save previous
            if current_chunk:
                chunks[f"{name}::{current_name}"] = '\n'.join(current_chunk).strip()
                current_chunk = []

            if func_match:
                current_name = f"def_{func_match.group(1)}"
            elif class_match:
                current_name = f"class_{class_match.group(1)}"

        current_chunk.append(line)

    if current_chunk:
        chunks[f"{name}::{current_name}"] = '\n'.join(current_chunk).strip()

    return chunks

def split_all_py_files(file_map):
    all_chunks = {}
    for name, content in file_map.items():
        if name.endswith(".py"):
            chunks = split_py_file(name, content)
            all_chunks.update(chunks)
    return all_chunks

def run_split():
    if not os.path.exists(FILE_MAP_PATH):
        print("❌ Не найден saci_file_map.json")
        return

    with open(FILE_MAP_PATH, "r", encoding="utf-8") as f:
        file_map = json.load(f)

    chunks = split_all_py_files(file_map)
    os.makedirs("logs", exist_ok=True)
    with open(CHUNK_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"✅ Разделено чанков: {len(chunks)}")
    print(f"📦 Сохранено в {CHUNK_OUTPUT}")

if __name__ == "__main__":
    run_split()

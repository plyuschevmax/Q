import os
import json
from tree_sitter import Language, Parser

# Компилируем язык (один раз)
if not os.path.exists('build/my-languages.so'):
    Language.build_library(
        'build/my-languages.so',
        ['vendor/tree-sitter-python']
    )

PY_LANGUAGE = Language('build/my-languages.so', 'python')
parser = Parser()
parser.set_language(PY_LANGUAGE)

SRC_DIR = "."
CHUNKS_PATH = "logs/saci_code_chunks.json"

def extract_chunks_from_source(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    tree = parser.parse(bytes(code, "utf8"))
    root_node = tree.root_node

    lines = code.split("\n")
    chunks = {}

    def get_text(start, end):
        return "\n".join(lines[start:end+1]).strip()

    for node in root_node.children:
        if node.type in ("function_definition", "class_definition"):
            name = node.child_by_field_name("name")
            if name:
                id = f"{filepath}::{'def' if node.type == 'function_definition' else 'class'}_{name.text.decode()}"
                chunk = get_text(node.start_point[0], node.end_point[0])
                chunks[id] = chunk

    return chunks

def scan_all_files():
    all_chunks = {}
    for root, _, files in os.walk(SRC_DIR):
        if "venv" in root or "__pycache__" in root or "node_modules" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                chunks = extract_chunks_from_source(path)
                all_chunks.update(chunks)
    return all_chunks

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    result = scan_all_files()
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"✅ Tree-sitter чанки сохранены → {CHUNKS_PATH}")

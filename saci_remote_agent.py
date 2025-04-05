import os
import json

def scan_repository(root="."):
    structure = {}
    for dirpath, _, filenames in os.walk(root):
        if any(x in dirpath for x in ['.git', '__pycache__', 'venv', 'node_modules']):
            continue
        rel_path = os.path.relpath(dirpath, root)
        structure[rel_path] = [f for f in filenames if f.endswith(('.py', '.md', '.json', '.yml', '.yaml'))]
    return structure

def read_file_contents(structure, root="."):
    file_map = {}
    for folder, files in structure.items():
        for file in files:
            path = os.path.join(root, folder, file) if folder != '.' else os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                file_map[os.path.join(folder, file)] = content
            except Exception as e:
                file_map[os.path.join(folder, file)] = f"[Ошибка чтения файла: {e}]"
    return file_map

def save_outputs(structure, file_map):
    os.makedirs("logs", exist_ok=True)
    with open("logs/saci_project_map.json", "w", encoding="utf-8") as f:
        json.dump(structure, f, indent=4, ensure_ascii=False)

    with open("logs/saci_file_map.json", "w", encoding="utf-8") as f:
        json.dump(file_map, f, indent=2, ensure_ascii=False)

    print("📍 Структура и содержимое файлов сохранены в logs/")

if __name__ == "__main__":
    project_structure = scan_repository()
    file_contents = read_file_contents(project_structure)
    save_outputs(project_structure, file_contents)
    print("✅ Готов к анализу.")

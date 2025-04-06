import subprocess
import os
import json

GOAL_STATE = "saci_goal_state.json"


def run_developer_agent():
    if not os.path.exists(GOAL_STATE):
        print("❌ Нет цели.")
        return

    with open(GOAL_STATE) as f:
        goal_data = json.load(f)

    goal = goal_data.get("goal", "")
    updated = False

    filename = extract_filename_from_goal(goal)
    if filename:
        extension = os.path.splitext(filename)[-1]
        if extension == ".py" and filename.startswith("test_"):
            generate_py_test(filename)
        elif extension == ".py":
            generate_python_stub(filename)
        elif extension == ".md":
            generate_markdown_doc(filename, goal)
        elif extension == ".json":
            generate_json_config(filename)
        elif extension in [".yml", ".yaml"]:
            generate_yaml_config(filename)
        else:
            print(f"⚠️ Неизвестное расширение: {extension}")
        updated = True

    if updated:
        goal_data["dev_done"] = True
        goal_data["status"] = "done"
        with open(GOAL_STATE, "w") as f:
            json.dump(goal_data, f, indent=4, ensure_ascii=False)
        print(f"✅ Цель developer.py завершена: {goal}")
    else:
        print("⚠️ Цель developer.py не распознана.")


def extract_filename_from_goal(goal):
    words = goal.split()
    for word in words:
        if any(word.endswith(ext) for ext in [".py", ".md", ".json", ".yml", ".yaml"]):
            return word
    return None


def generate_python_stub(filename):
    path = ensure_path(filename)
    class_name = class_from_filename(filename)
    content = f'''"""
{filename} — автосгенерированный SACI модуль.
"""

class {class_name}:
    def __init__(self):
        pass

    def run(self):
        print("🚀 {class_name} готов к работе.")

if __name__ == "__main__":
    agent = {class_name}()
    agent.run()
'''
    write_file(path, content)


def generate_py_test(filename):
    path = ensure_path(filename)
    content = f"""import unittest

class TestGenerated(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
"""
    write_file(path, content)


def generate_markdown_doc(filename, goal):
    path = ensure_path(filename)
    title = (
        goal.split(" создать ")[-1]
        if "создать" in goal
        else filename.replace(".md", "")
    )
    content = f"""# {title.title()}

> Автосгенерированный SACI документ по цели:

🎯 **{goal}**

---

## TODO

- [ ] Определить структуру
- [ ] Добавить описание
- [ ] Завершить реализацию
"""
    write_file(path, content)


def generate_json_config(filename):
    path = ensure_path(filename)
    default = {
        "name": filename.replace(".json", ""),
        "description": "",
        "version": "1.0",
        "config": {},
    }
    write_file(path, json.dumps(default, indent=4, ensure_ascii=False))


def generate_yaml_config(filename):
    path = ensure_path(filename)
    content = f"""# {filename}
name: sample_pipeline
description: SACI auto-generated YAML config
steps:
  - name: analyze
    run: python analyze.py
  - name: generate
    run: python developer.py
"""
    write_file(path, content)


def ensure_path(filename):
    parts = filename.split("/")
    if len(parts) > 1:
        dir_path = os.path.join(*parts[:-1])
        os.makedirs(dir_path, exist_ok=True)
    return filename


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"📦 Создан файл: {path}")


def class_from_filename(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    return "".join(word.capitalize() for word in base.split("_"))


if __name__ == "__main__":
    run_developer_agent()

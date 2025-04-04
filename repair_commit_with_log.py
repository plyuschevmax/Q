import os

FILE = "saci_orchestrator/orchestrator.py"
START_TAG = "        def commit_with_log(self, file, content, message, log_file=\"SACI_LOG_TEMPLATE.md\"):"
INDENT = "    "

# Чтение исходного файла
with open(FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Найти начало commit_with_log внутри sync_after_commit
start_index = None
for i, line in enumerate(lines):
    if START_TAG.strip() in line.strip():
        start_index = i
        break

if start_index is None:
    print("❌ Метод `commit_with_log` не найден или уже исправлен.")
    exit(0)

# Собрать тело метода
method_lines = []
brace_stack = []
inside_method = False

for i in range(start_index, len(lines)):
    line = lines[i]

    # Начало метода
    if not inside_method and line.strip().startswith("def commit_with_log"):
        inside_method = True

    if inside_method:
        method_lines.append(line)

        # Удаляемые отступы = 8 пробелов (вложенность внутри def)
        if line.strip() == "":
            continue
        leading_spaces = len(line) - len(line.lstrip())
        if leading_spaces < 8 and line.strip() != "":
            # Конец метода
            break

# Удалить старый блок
del lines[start_index:start_index + len(method_lines) - 1]

# Убрать вложенные отступы (4 пробела из 8)
cleaned_method = []
for line in method_lines:
    if line.strip() == "":
        cleaned_method.append(line)
    else:
        cleaned_method.append(line[4:])  # убрать один уровень вложенности

# Вставим после sync_after_commit
insert_index = None
for i, line in enumerate(lines):
    if "def sync_after_commit" in line:
        insert_index = i
        break

if insert_index is None:
    print("❌ Метод `sync_after_commit` не найден.")
    exit(1)

# Найти конец sync_after_commit
sync_indent = len(INDENT)
for i in range(insert_index + 1, len(lines)):
    if lines[i].strip().startswith("def "):
        insert_index = i
        break

# Вставка метода
lines = lines[:insert_index] + ["\n"] + cleaned_method + ["\n"] + lines[insert_index:]

# Запись исправленного файла
with open(FILE, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("✅ Метод `commit_with_log` успешно перемещён на уровень класса.")

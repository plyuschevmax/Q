import re
import os

def fix_imports_in_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    stdlib = []
    external = []
    internal = []
    current_imports = set()
    rest_of_code = []

    for line in lines:
        if re.match(r"^\s*(import|from)\s+", line):
            if line.strip() in current_imports:
                continue
            current_imports.add(line.strip())

            if line.startswith("import os") or "datetime" in line or "json" in line or "sys" in line:
                stdlib.append(line)
            elif "telebot" in line or "dotenv" in line or "openai" in line or "requests" in line:
                external.append(line)
            else:
                internal.append(line)
        else:
            rest_of_code.append(line)

    # Сортируем и объединяем
    result = []
    result.extend(sorted(stdlib))
    result.append("\n")
    result.extend(sorted(external))
    result.append("\n")
    result.extend(sorted(internal))
    result.append("\n")
    result.extend(rest_of_code)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(result)

    print(f"✅ Импорты отформатированы в {filepath}")

if __name__ == "__main__":
    # Пример: автофикс только telegram_bot.py
    fix_imports_in_file("telegram_bot.py")

# patch_in_place.py

import os

TARGET_FILE = "saci_orchestrator/orchestrator.py"

METHOD_DEF = """
    def commit_with_log(self, file, content, message, log_file="SACI_LOG_TEMPLATE.md"):
        # Коммит основного файла
        self.commit_from_bot(file=file, content=content, message=message)

        # Генерация записи в лог
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
        log_entry = f\"""\"
### 🧠 SACI-Agent
🕒 {timestamp}  
🎯 {message}  
🔄 Изменения:  
- `{file}` обновлён автоматически
\"""\"

        try:
            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8") as f:
                    existing = f.read()
            else:
                existing = "# SACI Commit Log 📘\\n"

            updated_log = existing.strip() + "\\n\\n" + log_entry.strip() + "\\n"

            with open(log_file, "w", encoding="utf-8") as f:
                f.write(updated_log)

            self.commit_from_bot(
                file=log_file,
                content=updated_log,
                message=f"Обновлён SACI-лог после коммита {file}"
            )

        except Exception as e:
            print(f"⚠️ Ошибка при обновлении SACI-лога: {e}")
"""

def patch_file():
    if not os.path.exists(TARGET_FILE):
        print("❌ Файл не найден:", TARGET_FILE)
        return

    with open(TARGET_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    if "def commit_with_log(" in content:
        print("✅ Метод `commit_with_log` уже существует. Патч не нужен.")
        return

    insert_point = content.rfind("def sync_after_commit(")
    if insert_point == -1:
        print("❌ Не найден метод `sync_after_commit`, некуда вставлять.")
        return

    before = content[:insert_point]
    after = content[insert_point:]

    # Вставим метод после sync_after_commit
    updated = before + after + "\n\n" + METHOD_DEF.strip() + "\n"

    with open(TARGET_FILE, "w", encoding="utf-8") as f:
        f.write(updated)

    print("✅ Метод `commit_with_log` вставлен в", TARGET_FILE)

if __name__ == "__main__":
    patch_file()

import os
from dotenv import load_dotenv
from saci_orchestrator.orchestrator import GitHubAgent

# Загружаем .env переменные
load_dotenv()

# Получаем данные
token = os.getenv("GITHUB_TOKEN")
repo = os.getenv("GITHUB_REPO")
username = os.getenv("GITHUB_USERNAME")
assert token and repo and username, "Ошибка: не переданы переменные окружения."

# Создаём агента
agent = GitHubAgent(token, repo, username)

# Подготавливаем push
file_path = "main.py"
file_content = "# SACI: автоматическое обновление main.py\nprint('Hello from SACI!')"
commit_msg = "Автообновление main.py для теста push"

# Запуск
agent.update_file(file_path, file_content, commit_msg)

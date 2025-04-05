import os
from dotenv import load_dotenv
from patch_in_place import generate_patch
from saci_orchestrator.orchestrator import GitHubAgent

# Загрузка переменных окружения
load_dotenv()

token = os.getenv("GITHUB_TOKEN")
repo = os.getenv("GITHUB_REPO")
username = os.getenv("GITHUB_USERNAME")

# 1. Генерация патча до любых действий
generate_patch()

# 2. Создание агента
agent = GitHubAgent(token, repo, username)

# 3. Пример действия агента
file_path = "README.md"
file_content = "# SACI Agent: Auto-update\n\nThis file was updated by SACI."
commit_msg = "SACI: auto-update README"

agent.update_file(file_path, file_content, commit_msg)

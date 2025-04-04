import os
from dotenv import load_dotenv
from saci_orchestrator.orchestrator import GitHubAgent

# Загрузить переменные окружения
load_dotenv()

# Получить из .env
token = os.getenv("GITHUB_TOKEN")
repo = os.getenv("GITHUB_REPO")
username = os.getenv("GITHUB_USERNAME")

# Создать агента
agent = GitHubAgent(token, repo, username)

agent.commit_with_log(
    file="README.md",
    content="# QIP Repo\n\nАвтообновление через SACI Agent Пук-Среньк 🤖",
    message="Коммит README.md и лог от ÆON-Agent"
)
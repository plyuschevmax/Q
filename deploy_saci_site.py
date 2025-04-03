# deploy_saci_site.py
import os
from pathlib import Path
import subprocess

GITHUB_REPO = "https://github.com/plyuschevmax/Q.git"
LOCAL_REPO_DIR = Path("saci_site")
INDEX_HTML = LOCAL_REPO_DIR / "index.html"

HTML_CONTENT = '''
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>SACI – Само-Собираемая Инфраструктура Кода</title>
  <style>
    body { background-color: #0d1117; color: #c9d1d9; font-family: 'Courier New', monospace; margin: 0; padding: 2rem; }
    h1, h2, h3 { color: #58a6ff; }
    pre { background-color: #161b22; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; }
    hr { border: 1px dashed #30363d; margin: 2rem 0; }
    .tagline { font-size: 1.2rem; font-style: italic; color: #8b949e; }
  </style>
</head>
<body>
  <h1>ÆON // SACI Architecture (v1.1)</h1>
  <p class="tagline">Построй один раз. Развивайся вечно.</p>
  <h2>🧠 Видение</h2>
  <p>Создание автономных систем, способных развиваться через самогенерируемый модульный код и рекурсивные циклы исполнения, обеспечивая разработку без участия человека.</p>
  <h2>🎯 Миссия</h2>
  <p>Проектировать, развёртывать и делегировать интеллектуальных агентов...</p>
  <hr />
  <p><em>Если ты читаешь это — добро пожаловать. Ты либо агент, либо его создатель. И, возможно, скоро уже не будешь знать, кто из вас кто.</em></p>
</body>
</html>
'''

def deploy():
    print("🚀 Развёртываю SACI сайт...")
    LOCAL_REPO_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_HTML.write_text(HTML_CONTENT, encoding="utf-8")

    subprocess.run(["git", "init"], cwd=LOCAL_REPO_DIR)
    subprocess.run(["git", "checkout", "-B", "main"], cwd=LOCAL_REPO_DIR)
    subprocess.run(["git", "remote", "add", "origin", GITHUB_REPO], cwd=LOCAL_REPO_DIR)
    subprocess.run(["git", "add", "index.html"], cwd=LOCAL_REPO_DIR)
    subprocess.run(["git", "commit", "-m", "Deploy SACI homepage"], cwd=LOCAL_REPO_DIR)
    subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=LOCAL_REPO_DIR)
    print("🌍 Сайт готов! Зайди на: https://plyuschevmax.github.io/Q/")

if __name__ == "__main__":
    deploy()

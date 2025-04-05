# saci_web_orchestrator.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import subprocess
import os
import json
import openai
from datetime import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class PromptInput(BaseModel):
    prompt: str
    agent: str = "architect"

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
      <head>
        <title>SACI WebApp</title>
        <style>
          body { font-family: sans-serif; max-width: 800px; margin: 40px; }
          textarea { width: 100%; }
          .block { margin-top: 30px; padding: 15px; background: #f5f5f5; border-radius: 8px; }
          code { background: #eee; padding: 2px 6px; border-radius: 4px; }
        </style>
        <script>
          async function refreshData() {
            const status = await fetch('/status').then(r => r.json());
            const patch = await fetch('/patch').then(r => r.json());
            const review = await fetch('/review').then(r => r.json());
            const metrics = await fetch('/metrics').then(r => r.json());

            document.getElementById("goal").innerText = status.goal || '—';
            document.getElementById("status").innerText = status.status || '—';
            document.getElementById("patch").innerText = patch.patch || '—';
            document.getElementById("review").innerText = (review.review || '').slice(0, 1000);
            document.getElementById("metrics").innerText = metrics.current ?
              `📄 Файлов: ${metrics.current.files}, 📏 Строк: ${metrics.current.lines}` : '—';
          }
          setInterval(refreshData, 8000);
          window.onload = refreshData;
        </script>
      </head>
      <body>
        <h2>🧠 SACI Web Dashboard</h2>

        <form method="post" action="/prompt">
          <textarea name="prompt" rows="4" placeholder="Введите промпт..." required></textarea><br>
          <select name="agent">
            <option value="architect">🧠 Architect</option>
            <option value="developer">👨‍💻 Developer</option>
            <option value="strategist">🎯 Strategist</option>
          </select>
          <button type="submit">🚀 Запустить задачу</button>
        </form>

        <div class="block">
          <h4>📌 Текущая цель</h4>
          <div id="goal">—</div>

          <h4>🧬 Статус</h4>
          <div id="status">—</div>

          <h4>📄 Последний патч</h4>
          <div><code id="patch">—</code></div>

          <h4>📘 Последнее ревью</h4>
          <pre id="review">—</pre>

          <h4>📊 Метрики</h4>
          <div id="metrics">—</div>
        </div>

        <form onsubmit="return fetchAndAlert(event, '/apply')">
  <button type="submit">✅ Применить патч</button>
</form>

<form onsubmit="return fetchAndAlert(event, '/agree')">
  <button type="submit">📘 Согласовать</button>
</form>

<script>
  async function fetchAndAlert(e, endpoint) {
    e.preventDefault();
    const res = await fetch(endpoint, { method: "POST" });
    const txt = await res.text();
    alert(txt);
    await refreshData();
    return false;
  }
</script>


        <p><a href="/docs">📖 Swagger API Docs</a></p>
      </body>
    </html>
    """

@app.post("/prompt")
def receive_prompt_form(prompt: str = Form(...), agent: str = Form("architect")):
    task_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    goal = f"Создать модуль на основе запроса: {prompt}"

    goal_state = {
        "goal": goal,
        "status": "in_progress",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "source": "webapp",
        "task_id": task_id,
        "dev_done": False,
        "test_done": False
    }
    with open("saci_goal_state.json", "w", encoding="utf-8") as f:
        json.dump(goal_state, f, indent=4, ensure_ascii=False)

    subprocess.Popen(["python", "agents/code_refactor.py"])
    return RedirectResponse("/", status_code=303)

@app.post("/apply")
def apply_patch_web():
    patch_name = None
    if os.path.exists("patches"):
        patches = sorted([f for f in os.listdir("patches") if f.endswith((".patch", ".diff"))])
        patch_name = patches[-1].replace(".patch", "").replace(".diff", "") if patches else None

    if not patch_name:
        return HTMLResponse("<p>❌ Нет доступных патчей.</p>")

    for ext in [".patch", ".diff"]:
        path = f"patches/{patch_name}{ext}"
        if os.path.exists(path):
            os.system(f"git apply {path}")
            return RedirectResponse("/", status_code=303)
    return HTMLResponse("<p>❌ Patch не найден.</p>")

@app.post("/agree")
def agree_patch_web():
    patch_name = None
    if os.path.exists("patches"):
        patches = sorted([f for f in os.listdir("patches") if f.endswith((".patch", ".diff"))])
        patch_name = patches[-1].replace(".patch", "").replace(".diff", "") if patches else None

    if not patch_name:
        return HTMLResponse("<p>❌ Нет патча для согласования.</p>")

    log_path = "logs/goals_log.json"
    os.makedirs("logs", exist_ok=True)
    log = []
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            log = json.load(f)

    log.append({
        "type": "patch",
        "patch": patch_name,
        "status": "applied",
        "agreed": True,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=4, ensure_ascii=False)

    return RedirectResponse("/", status_code=303)

@app.get("/status")
def get_status():
    if not os.path.exists("saci_goal_state.json"):
        return {"status": "нет активной цели"}
    with open("saci_goal_state.json", "r", encoding="utf-8") as f:
        state = json.load(f)
    return state

@app.get("/patch")
def get_latest_patch():
    if not os.path.exists("patches"):
        return {"patch": None}
    patches = sorted([f for f in os.listdir("patches") if f.endswith((".patch", ".diff"))])
    if not patches:
        return {"patch": None}
    return {"patch": patches[-1]}

@app.get("/review")
def get_review():
    if not os.path.exists("logs/patch_reviews"):
        return {"review": None}
    reviews = sorted(os.listdir("logs/patch_reviews"))
    if not reviews:
        return {"review": None}
    latest = reviews[-1]
    with open(os.path.join("logs/patch_reviews", latest), "r", encoding="utf-8") as f:
        content = f.read()
    return {"review": content, "file": latest}

@app.get("/metrics")
def get_code_metrics():
    path = "logs/code_metrics.json"
    if not os.path.exists(path):
        return {"message": "Нет метрик"}
    with open(path, "r", encoding="utf-8") as f:
        log = json.load(f)
    return {"current": log[-1], "previous": log[-2] if len(log) > 1 else None}
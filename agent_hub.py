def generate_agent_hub():
    code = '''"""
SACI Agent Hub
Роутер между стратегами, разработчиком, тестером.
"""

def route_goal(goal):
    if "strategy" in goal:
        from strategist import plan
        return plan(goal)
    elif "test" in goal:
        from tester import run_tests
        return run_tests(goal)
    else:
        from developer import build
        return build(goal)

if __name__ == "__main__":
    print("🧠 Agent Hub готов к приёму целей.")
'''
    with open("agents/agent_hub.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("🧠 agent_hub.py создан.")

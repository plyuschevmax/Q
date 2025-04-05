"""
SACI Agent Hub — маршрутизатор задач между AI-агентами.
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
    print("🧠 Agent Hub запущен.")

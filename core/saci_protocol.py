class SACIProtocol:
    def __init__(self, agent_name: str = "SACI-Core-Agent"):
        self.agent_name = agent_name

    def log_task(self, task: str):
        print(f"[SACI] {self.agent_name} выполняет: {task}")

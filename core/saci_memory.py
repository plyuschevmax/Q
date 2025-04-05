"""
SACI Memory Core — отвечает за хранение краткосрочного состояния и хода выполнения целей.
"""

class SACIMemory:
    def __init__(self):
        self.state = {}

    def set(self, key, value):
        self.state[key] = value

    def get(self, key):
        return self.state.get(key)

    def reset(self):
        self.state = {}

if __name__ == "__main__":
    memory = SACIMemory()
    memory.set("example", 42)
    print("🧠 Memory ready:", memory.get("example"))

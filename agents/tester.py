class Tester:
    def execute(self, data):
        code = data.get("code", [])
        data["tests"] = [f"Тест пройден для: {c}" for c in code]
        return data

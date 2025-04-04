class Strategist:
    def execute(self, data):
        goal = data.get("goal", "нет цели")
        data["strategy"] = f"Разработка стратегии для цели: {goal}"
        return data

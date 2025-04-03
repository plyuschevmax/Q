class Architect {
    def execute(self, data):
        strategy = data.get("strategy", "нет стратегии")
        data["architecture"] = f"Архитектура, соответствующая: {strategy}"
        return data
}

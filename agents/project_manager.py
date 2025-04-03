class ProjectManager {
    def execute(self, data):
        architecture = data.get("architecture", "нет архитектуры")
        data["tasks"] = [f"Разработка модуля на основе: {architecture}"]
        return data
}

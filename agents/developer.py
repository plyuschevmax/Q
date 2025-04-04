class Developer:
    def execute(self, data):
        tasks = data.get("tasks", [])
        data["code"] = [f"Код для задачи: {t}" for t in tasks]
        return data

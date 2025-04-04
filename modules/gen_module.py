patch_agent_task.py — интеграция классов Task и Agent в проект SACI

import os from pathlib import Path

CORE_FILE = Path("core/tasks.py") AGENT_FILE = Path("agents/strategist.py")

TASK_CLASS = '''class Task: """ Класс Task представляет собой задание, которое должно быть передано дальше по цепочке. """ def init(self, task_name, task_description): self.task_name = task_name self.task_description = task_description self.task_status = "Not started" self.task_start_time = None self.task_end_time = None

def start_task(self):
    self.task_status = "In progress"
        from datetime import datetime
            self.task_start_time = datetime.now()

            def end_task(self):
                self.task_status = "Completed"
                    from datetime import datetime
                        self.task_end_time = datetime.now()

                        '''

                        AGENT_CLASS = '''class Agent: """ Агент, который выполняет и передаёт задание следующему агенту. """ def init(self, name): self.name = name

                        def assign_task(self, task):
                            task.start_task()
                                print(f"Task '{task.task_name}' is assigned to agent '{self.name}'.")

                                def complete_task(self, task):
                                    task.end_task()
                                        print(f"Task '{task.task_name}' is completed by agent '{self.name}'.")

                                        def pass_task(self, task, next_agent):
                                            self.complete_task(task)
                                                next_agent.assign_task(task)

                                                '''

                                                def patch_file(path: Path, class_code: str, class_name: str): if not path.exists(): path.parent.mkdir(parents=True, exist_ok=True) path.write_text(f"{class_code}\n", encoding="utf-8") print(f"✅ Создан файл {path} с классом {class_name}") else: content = path.read_text(encoding="utf-8") if class_name in content: print(f"⚠️ Класс {class_name} уже есть в {path}, пропускаем") else: with open(path, "a", encoding="utf-8") as f: f.write(f"\n\n{class_code}\n") print(f"✅ Добавлен класс {class_name} в {path}")

                                                def main(): patch_file(CORE_FILE, TASK_CLASS, "Task") patch_file(AGENT_FILE, AGENT_CLASS, "Agent")

                                                if name == "main": main()

                                                
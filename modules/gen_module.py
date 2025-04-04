import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Python модуль для агента-стратега, который согласовывает передачу задания дальше по цепочке

# Импорт необходимых библиотек
from datetime import datetime

class Task:
    """
    Класс Task представляет собой задание, которое должно быть передано дальше по цепочке.
    """
    def __init__(self, task_name, task_description):
        """
        Инициализация задания с именем и описанием.
        """
        self.task_name = task_name
        self.task_description = task_description
        self.task_status = "Not started"
        self.task_start_time = None
        self.task_end_time = None

    def start_task(self):
        """
        Метод для начала выполнения задания.
        """
        self.task_status = "In progress"
        self.task_start_time = datetime.now()

    def end_task(self):
        """
        Метод для завершения задания.
        """
        self.task_status = "Completed"
        self.task_end_time = datetime.now()

class Agent:
    """
    Класс Agent представляет собой агента, который согласовывает передачу задания дальше по цепочке.
    """
    def __init__(self, name):
        """
        Инициализация агента с именем.
        """
        self.name = name

    def assign_task(self, task):
        """
        Метод для назначения задания агенту.
        """
        task.start_task()
        print(f"Task '{task.task_name}' is assigned to agent '{self.name}'.")

    def complete_task(self, task):
        """
        Метод для завершения задания агентом.
        """
        task.end_task()
        print(f"Task '{task.task_name}' is completed by agent '{self.name}'.")

    def pass_task(self, task, next_agent):
        """
        Метод для передачи задания следующему агенту.
        """
        self.complete_task(task)
        next_agent.assign_task(task)
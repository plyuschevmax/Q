from saci_orchestrator.orchestrator import SACIOrchestrator

orchestrator = SACIOrchestrator()
orchestrator.set_goal("Хочу создать SACI-протокол, который автоматически генерирует код и тесты.")
orchestrator.plan_tasks()
orchestrator.execute_tasks()

class TesterAgent:
    name="Tester"
    role="Testing"
    def run(self, task: str) -> str:
        return f"[Tester] LLM not connected. Task received: {task}"

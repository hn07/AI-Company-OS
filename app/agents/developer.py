class DeveloperAgent:
    name="Developer"
    role="Development"
    def run(self, task: str) -> str:
        return f"[Developer] LLM not connected. Task received: {task}"

class ResearcherAgent:
    name="Researcher"
    role="Research"
    def run(self, task: str) -> str:
        return f"[Researcher] LLM not connected. Task received: {task}"

class ReviewerAgent:
    name="Reviewer"
    role="Quality Review"
    def run(self, task: str) -> str:
        return f"[Reviewer] LLM not connected. Task received: {task}"

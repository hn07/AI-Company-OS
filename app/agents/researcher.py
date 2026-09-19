class ResearcherAgent:
    name = "Researcher"
    role = "Nghiên cứu"

    def run(self, task: str) -> str:
        return f"[Researcher] Chưa kết nối LLM. Task nhận được: {task}"

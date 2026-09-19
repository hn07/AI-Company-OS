class ReviewerAgent:
    name = "Reviewer"
    role = "Kiểm duyệt"

    def run(self, task: str) -> str:
        return f"[Reviewer] Chưa kết nối LLM. Task nhận được: {task}"

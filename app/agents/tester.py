class TesterAgent:
    name = "Tester"
    role = "Kiểm thử"

    def run(self, task: str) -> str:
        return f"[Tester] Chưa kết nối LLM. Task nhận được: {task}"

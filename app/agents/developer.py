class DeveloperAgent:
    name = "Developer"
    role = "Phát triển"

    def run(self, task: str) -> str:
        return f"[Developer] Chưa kết nối LLM. Task nhận được: {task}"

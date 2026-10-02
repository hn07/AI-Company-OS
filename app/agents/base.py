import json

from app.llm.client import LLMClient


class BaseAgent:
    name = "Agent"
    role = "General"

    def _local_result(self, task: str, context: str) -> str:
        return f"[{self.name}] Local execution complete.\nTask: {task}\nContext received: {len(context)} chars."

    def run(self, task: str, context: str = "") -> str:
        client = LLMClient()
        if client.provider != "ollama":
            return self._local_result(task, context)

        system = (
            f"You are the {self.name} agent in an AI Company OS. "
            f"Your role is {self.role}. Execute the assigned task using the provided context. "
            "Return JSON with keys: status, summary, output, issues. "
            "status must be COMPLETED or NEEDS_ATTENTION. Be concrete and concise."
        )
        user = f"ASSIGNED TASK:\n{task}\n\nPREVIOUS AGENT CONTEXT:\n{context or '(none)'}"
        try:
            result = client.generate_json(system, user)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as exc:
            return (
                f"[{self.name}] Ollama execution failed; local fallback used.\n"
                f"Error: {exc}\n{self._local_result(task, context)}"
            )

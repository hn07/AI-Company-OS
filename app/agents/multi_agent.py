import json

from app.llm.client import LLMClient


class Agent:
    def __init__(self, name, role):
        self.name = name
        self.role = role

    def run(self, task, context=""):
        client = LLMClient()
        if client.provider != "ollama":
            return (
                f"[{self.name}] Local execution complete.\n"
                f"Task: {task}\nPrevious context: {len(context)} chars."
            )

        system = (
            f"You are the {self.name} agent in AI Company OS. "
            f"Role: {self.role}. Execute the assigned task using previous agent outputs. "
            "Return JSON with keys status, summary, output, issues. "
            "status must be COMPLETED or NEEDS_ATTENTION."
        )
        user = f"ASSIGNED TASK:\n{task}\n\nPREVIOUS AGENT OUTPUTS:\n{context or '(none)'}"
        try:
            result = client.generate_json(system, user)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as exc:
            return (
                f"[{self.name}] Local fallback after Ollama error: {exc}\n"
                f"Task: {task}"
            )


AGENTS = {
    "Researcher": Agent("Researcher", "Research and requirements analysis"),
    "Developer": Agent("Developer", "Solution design and implementation"),
    "Tester": Agent("Tester", "Testing and defect detection"),
    "Reviewer": Agent("Reviewer", "Quality review and release readiness"),
}

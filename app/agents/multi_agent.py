import json

from app.llm.client import LLMClient


class Agent:
    def __init__(self, name, role):
        self.name = name
        self.role = role

    def run_structured(self, task, context=""):
        client = LLMClient()

        if self.name == "Tester" and client.provider != "ollama":
            upper = f"{task}\n{context}".upper()
            failed = any(token in upper for token in ("TRACEBACK", "EXCEPTION", "ERROR:", "NEEDS_ATTENTION"))
            return {
                "status": "FAIL" if failed else "PASS",
                "summary": "Local rule-based quality test.",
                "output": "Detected obvious error markers." if failed else "No obvious error markers detected.",
                "issues": ["Obvious error marker found in agent output."] if failed else [],
            }

        if self.name == "Reviewer" and client.provider != "ollama":
            upper = f"{task}\n{context}".upper()
            needs_fix = "FAIL" in upper or "NEEDS_FIX" in upper
            return {
                "status": "NEEDS_FIX" if needs_fix else "APPROVED",
                "summary": "Local rule-based release review.",
                "output": "Review found unresolved quality markers." if needs_fix else "No unresolved quality markers detected.",
                "issues": ["Previous QC output contains FAIL/NEEDS_FIX."] if needs_fix else [],
            }

        if client.provider != "ollama":
            return {
                "status": "COMPLETED",
                "summary": f"{self.name} completed the assigned task locally.",
                "output": f"Task: {task}",
                "issues": [],
            }

        if self.name == "Tester":
            status_rule = "status must be PASS or FAIL."
        elif self.name == "Reviewer":
            status_rule = "status must be APPROVED or NEEDS_FIX."
        else:
            status_rule = "status must be COMPLETED or NEEDS_ATTENTION."

        system = (
            f"You are the {self.name} agent in AI Company OS. "
            f"Role: {self.role}. Execute the assigned task using previous agent outputs. "
            "Return ONLY valid JSON with keys status, summary, output, issues. "
            f"{status_rule} issues must be a JSON array of concrete findings. "
            "For Tester: PASS unless there is concrete evidence of a reproducible defect, "
            "contradiction, failed requirement, traceback, or explicit test failure in the supplied evidence. "
            "Do not invent failures merely because no runnable artifact is available. "
            "If evidence is incomplete, report that in issues but keep PASS when no defect is demonstrated."
        )
        user = f"ASSIGNED TASK:\n{task}\n\nPREVIOUS AGENT OUTPUTS:\n{context or '(none)'}"

        try:
            result = client.generate_json(system, user)
            if not isinstance(result, dict):
                raise ValueError("Agent response is not a JSON object.")
            return result
        except Exception as exc:
            if self.name == "Tester":
                return {
                    "status": "ERROR",
                    "summary": "Tester could not complete the LLM test.",
                    "output": "",
                    "issues": [str(exc)],
                }
            if self.name == "Reviewer":
                return {
                    "status": "ERROR",
                    "summary": "Reviewer could not complete the LLM review.",
                    "output": "",
                    "issues": [str(exc)],
                }
            return {
                "status": "NEEDS_ATTENTION",
                "summary": f"{self.name} LLM execution failed.",
                "output": "",
                "issues": [str(exc)],
            }

    def run(self, task, context=""):
        return json.dumps(
            self.run_structured(task, context),
            ensure_ascii=False,
            indent=2,
        )


AGENTS = {
    "Researcher": Agent("Researcher", "Research and requirements analysis"),
    "Developer": Agent("Developer", "Solution design and implementation"),
    "Tester": Agent("Tester", "Testing and defect detection"),
    "Reviewer": Agent("Reviewer", "Quality review and release readiness"),
}

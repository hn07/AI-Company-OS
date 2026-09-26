import json

from app.llm.client import LLMClient


SYSTEM_PROMPT = """You are the AI Company OS Project Manager.
Your job is to turn a CEO project request into a practical execution plan.

Return ONLY valid JSON with this exact top-level structure:
{
  "analysis": "short analysis",
  "objective": "clear objective",
  "risks": ["risk 1"],
  "tasks": [
    {
      "title": "task title",
      "description": "specific task description",
      "agent": "Researcher|Developer|Tester|Reviewer"
    }
  ]
}

Rules:
- Create 3 to 8 tasks.
- Use only the four agent names above.
- Tasks must be ordered by execution dependency.
- Include at least one Tester task and one Reviewer task.
- Keep descriptions concrete and actionable.
"""


def deterministic_plan(name: str, description: str) -> dict:
    return {
        "analysis": "V2 local fallback planner created a standard software-project execution plan.",
        "objective": description,
        "risks": [
            "Requirements may be incomplete.",
            "Implementation may need revision after testing.",
        ],
        "tasks": [
            {
                "title": "Research requirements",
                "description": f"Clarify requirements and constraints for: {description}",
                "agent": "Researcher",
            },
            {
                "title": "Design implementation",
                "description": "Create the technical approach and implementation steps.",
                "agent": "Developer",
            },
            {
                "title": "Implement solution",
                "description": f"Implement the approved solution for project: {name}.",
                "agent": "Developer",
            },
            {
                "title": "Test implementation",
                "description": "Run functional checks and identify defects or missing requirements.",
                "agent": "Tester",
            },
            {
                "title": "Review quality",
                "description": "Review implementation and test results, then prepare the final report.",
                "agent": "Reviewer",
            },
        ],
    }


def build_plan(name: str, description: str) -> tuple[dict, str]:
    client = LLMClient()

    if client.provider == "ollama":
        try:
            plan = client.generate_json(
                SYSTEM_PROMPT,
                f"Project name: {name}\nCEO request: {description}",
            )
            validate_plan(plan)
            return plan, "ollama"
        except Exception:
            pass

    return deterministic_plan(name, description), "local-fallback"


def validate_plan(plan: dict) -> None:
    if not isinstance(plan, dict):
        raise ValueError("Plan must be an object")

    tasks = plan.get("tasks")
    if not isinstance(tasks, list) or not 3 <= len(tasks) <= 8:
        raise ValueError("Plan must contain 3 to 8 tasks")

    allowed = {"Researcher", "Developer", "Tester", "Reviewer"}
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("Each task must be an object")
        if not task.get("title") or not task.get("description"):
            raise ValueError("Task title and description are required")
        if task.get("agent") not in allowed:
            raise ValueError("Unknown agent")

    agents = {task["agent"] for task in tasks}
    if "Tester" not in agents or "Reviewer" not in agents:
        raise ValueError("Plan must include Tester and Reviewer")


def plan_to_text(plan: dict, provider: str) -> str:
    lines = [
        f"Manager analysis: {plan.get('analysis', '')}",
        f"Objective: {plan.get('objective', '')}",
        f"Planning provider: {provider}",
        "",
        "Risks:",
    ]
    lines.extend(f"- {risk}" for risk in plan.get("risks", []))
    lines.append("")
    lines.append("Execution tasks:")
    for index, task in enumerate(plan.get("tasks", []), start=1):
        lines.append(
            f"{index}. [{task['agent']}] {task['title']} — {task['description']}"
        )
    return "\n".join(lines)

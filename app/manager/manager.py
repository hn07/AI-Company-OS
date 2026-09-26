import json

from app.agents.researcher import ResearcherAgent
from app.agents.developer import DeveloperAgent
from app.agents.tester import TesterAgent
from app.agents.reviewer import ReviewerAgent
from app.database.database import get_connection
from app.manager.planner import build_plan, plan_to_text


AGENTS = {
    "Researcher": ResearcherAgent(),
    "Developer": DeveloperAgent(),
    "Tester": TesterAgent(),
    "Reviewer": ReviewerAgent(),
}


def create_project_plan(project_id: int):
    db = get_connection()
    project = db.execute(
        "SELECT name,description FROM projects WHERE id=?", (project_id,)
    ).fetchone()
    if not project:
        db.close()
        return

    plan, provider = build_plan(project["name"], project["description"])
    plan_json = json.dumps(plan, ensure_ascii=False)
    plan_text = plan_to_text(plan, provider)

    db.execute(
        "UPDATE projects SET status='WAITING_APPROVAL', plan_json=?, "
        "plan_provider=?, manager_analysis=?, updated_at=CURRENT_TIMESTAMP "
        "WHERE id=?",
        (
            plan_json,
            provider,
            plan.get("analysis", ""),
            project_id,
        ),
    )
    db.execute(
        "INSERT INTO approvals(project_id,action,status,notes) VALUES(?,?,?,?)",
        (project_id, "START_PROJECT", "PENDING", plan_text),
    )
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (
            project_id,
            "MANAGER_PLAN",
            f"Provider={provider}\n{plan_text}",
        ),
    )
    db.commit()
    db.close()


def create_project_tasks(project_id: int):
    db = get_connection()
    existing = db.execute(
        "SELECT COUNT(*) AS total FROM tasks WHERE project_id=?", (project_id,)
    ).fetchone()["total"]

    if existing:
        db.close()
        return

    project = db.execute(
        "SELECT plan_json FROM projects WHERE id=?", (project_id,)
    ).fetchone()

    if not project or not project["plan_json"]:
        db.close()
        return

    plan = json.loads(project["plan_json"])

    for task in plan["tasks"]:
        db.execute(
            "INSERT INTO tasks(project_id,title,description,assigned_agent,status) "
            "VALUES(?,?,?,?,?)",
            (
                project_id,
                task["title"],
                task["description"],
                task["agent"],
                "PENDING",
            ),
        )

    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (
            project_id,
            "TASKS_CREATED",
            f"Manager created {len(plan['tasks'])} tasks from approved plan.",
        ),
    )
    db.commit()
    db.close()


def _run_task(task_id: int):
    db = get_connection()
    task = db.execute(
        "SELECT * FROM tasks WHERE id=?", (task_id,)
    ).fetchone()
    if not task:
        db.close()
        return

    db.execute("UPDATE tasks SET status='RUNNING' WHERE id=?", (task_id,))
    db.commit()
    db.close()

    agent = AGENTS.get(task["assigned_agent"])
    if agent:
        result = agent.run(task["description"])
    else:
        result = f"[System] Agent {task['assigned_agent']} is not available."

    db = get_connection()
    db.execute(
        "UPDATE tasks SET status='COMPLETED',result=? WHERE id=?",
        (result, task_id),
    )
    db.commit()
    db.close()


def execute_project(project_id: int):
    """Execute the approved Manager plan in dependency order."""
    db = get_connection()
    project = db.execute(
        "SELECT * FROM projects WHERE id=?", (project_id,)
    ).fetchone()

    if not project or project["status"] != "APPROVED":
        db.close()
        return

    db.execute(
        "UPDATE projects SET status='IN_PROGRESS',updated_at=CURRENT_TIMESTAMP "
        "WHERE id=?",
        (project_id,),
    )
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (
            project_id,
            "PROJECT_STARTED",
            "CEO approval accepted; Manager started the approved dynamic plan.",
        ),
    )
    db.commit()
    db.close()

    create_project_tasks(project_id)

    db = get_connection()
    tasks = db.execute(
        "SELECT id,assigned_agent FROM tasks WHERE project_id=? ORDER BY id",
        (project_id,),
    ).fetchall()
    db.close()

    test_started = False
    review_started = False

    for task in tasks:
        if task["assigned_agent"] == "Tester" and not test_started:
            db = get_connection()
            db.execute(
                "UPDATE projects SET status='TESTING',updated_at=CURRENT_TIMESTAMP "
                "WHERE id=?",
                (project_id,),
            )
            db.execute(
                "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
                (project_id, "TESTING_STARTED", "Tester stage started."),
            )
            db.commit()
            db.close()
            test_started = True

        if task["assigned_agent"] == "Reviewer" and not review_started:
            db = get_connection()
            db.execute(
                "UPDATE projects SET status='REVIEW',updated_at=CURRENT_TIMESTAMP "
                "WHERE id=?",
                (project_id,),
            )
            db.execute(
                "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
                (project_id, "REVIEW_STARTED", "Reviewer stage started."),
            )
            db.commit()
            db.close()
            review_started = True

        _run_task(task["id"])

    db = get_connection()
    summary = db.execute(
        "SELECT title,assigned_agent,status,result FROM tasks "
        "WHERE project_id=? ORDER BY id",
        (project_id,),
    ).fetchall()

    summary_text = "\n".join(
        f"- [{row['assigned_agent']}] {row['title']}: {row['status']}"
        for row in summary
    )

    db.execute(
        "UPDATE projects SET status='COMPLETED',updated_at=CURRENT_TIMESTAMP "
        "WHERE id=?",
        (project_id,),
    )
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (
            project_id,
            "PROJECT_COMPLETED",
            "Manager final report:\n" + summary_text,
        ),
    )
    db.commit()
    db.close()

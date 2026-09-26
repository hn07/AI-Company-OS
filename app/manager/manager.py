from app.database.database import get_connection
from app.agents.researcher import ResearcherAgent
from app.agents.developer import DeveloperAgent
from app.agents.tester import TesterAgent
from app.agents.reviewer import ReviewerAgent

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

    plan = (
        f"Project: {project['name']}\n\n"
        "Manager analysis:\n"
        f"- Objective: {project['description']}\n"
        "- Step 1: Research requirements and constraints.\n"
        "- Step 2: Design implementation approach.\n"
        "- Step 3: Implement solution.\n"
        "- Step 4: Test implementation.\n"
        "- Step 5: Review quality and report to CEO.\n"
    )

    db.execute(
        "UPDATE projects SET status='WAITING_APPROVAL',updated_at=CURRENT_TIMESTAMP "
        "WHERE id=?",
        (project_id,),
    )
    db.execute(
        "INSERT INTO approvals(project_id,action,status,notes) VALUES(?,?,?,?)",
        (project_id, "START_PROJECT", "PENDING", plan),
    )
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (project_id, "MANAGER_PLAN", plan),
    )
    db.commit()
    db.close()


def create_project_tasks(project_id: int):
    """Create the standard V1.1 execution pipeline once."""
    db = get_connection()
    existing = db.execute(
        "SELECT COUNT(*) AS total FROM tasks WHERE project_id=?", (project_id,)
    ).fetchone()["total"]

    if existing:
        db.close()
        return

    tasks = [
        (
            "Research requirements",
            "Collect and structure project requirements and constraints.",
            "Researcher",
        ),
        (
            "Design implementation",
            "Convert requirements into a practical implementation approach.",
            "Developer",
        ),
        (
            "Implement solution",
            "Execute the implementation stage using the approved plan.",
            "Developer",
        ),
        (
            "Test implementation",
            "Run functional checks and record test results.",
            "Tester",
        ),
        (
            "Review quality",
            "Review the work and prepare the final quality report.",
            "Reviewer",
        ),
    ]

    for title, description, agent in tasks:
        db.execute(
            "INSERT INTO tasks(project_id,title,description,assigned_agent,status) "
            "VALUES(?,?,?,?,?)",
            (project_id, title, description, agent, "PENDING"),
        )

    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (
            project_id,
            "TASKS_CREATED",
            "V1.1 execution pipeline created: Research → Design → Implement → Test → Review",
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

    db.execute(
        "UPDATE tasks SET status='RUNNING' WHERE id=?", (task_id,)
    )
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
    """Run the V1.1 deterministic agent pipeline after CEO approval."""
    db = get_connection()
    project = db.execute(
        "SELECT * FROM projects WHERE id=?", (project_id,)
    ).fetchone()

    if not project:
        db.close()
        return

    if project["status"] != "APPROVED":
        db.close()
        return

    db.execute(
        "UPDATE projects SET status='IN_PROGRESS',updated_at=CURRENT_TIMESTAMP "
        "WHERE id=?",
        (project_id,),
    )
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (project_id, "PROJECT_STARTED", "CEO approval accepted; Manager started execution."),
    )
    db.commit()
    db.close()

    create_project_tasks(project_id)

    db = get_connection()
    tasks = db.execute(
        "SELECT id FROM tasks WHERE project_id=? ORDER BY id", (project_id,)
    ).fetchall()
    db.close()

    # Research, design and implementation happen in the execution stage.
    for task in tasks[:3]:
        _run_task(task["id"])

    db = get_connection()
    db.execute(
        "UPDATE projects SET status='TESTING',updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (project_id,),
    )
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (project_id, "TESTING_STARTED", "Tester agent stage started."),
    )
    db.commit()
    db.close()

    if len(tasks) >= 4:
        _run_task(tasks[3]["id"])

    db = get_connection()
    db.execute(
        "UPDATE projects SET status='REVIEW',updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (project_id,),
    )
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (project_id, "REVIEW_STARTED", "Reviewer agent stage started."),
    )
    db.commit()
    db.close()

    if len(tasks) >= 5:
        _run_task(tasks[4]["id"])

    db = get_connection()
    summary = db.execute(
        "SELECT title,status,result FROM tasks WHERE project_id=? ORDER BY id",
        (project_id,),
    ).fetchall()
    summary_text = "\n".join(
        f"- {row['title']}: {row['status']}" for row in summary
    )

    db.execute(
        "UPDATE projects SET status='COMPLETED',updated_at=CURRENT_TIMESTAMP WHERE id=?",
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

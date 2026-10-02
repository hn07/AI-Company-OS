import json

from app.agents.multi_agent import AGENTS
from app.database.database import get_connection
from app.manager.planner import build_plan, plan_to_text
from app.memory.memory_manager import build_memory_context, remember_task_result

MAX_QC_RETRIES = 3


def create_project_plan(project_id):
    db = get_connection()
    p = db.execute("SELECT name,description FROM projects WHERE id=?", (project_id,)).fetchone()
    if not p:
        db.close()
        return

    plan, provider = build_plan(p["name"], p["description"])
    db.execute(
        """UPDATE projects
           SET status='WAITING_APPROVAL', plan_json=?, plan_provider=?,
               manager_analysis=?, updated_at=CURRENT_TIMESTAMP
           WHERE id=?""",
        (json.dumps(plan, ensure_ascii=False), provider, plan.get("analysis", ""), project_id),
    )
    db.execute(
        "INSERT INTO approvals(project_id,action,status,notes) VALUES(?,?,?,?)",
        (project_id, "START_PROJECT", "PENDING", plan_to_text(plan, provider)),
    )
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (project_id, "MANAGER_PLAN", f"Provider={provider}"),
    )
    db.commit()
    db.close()


def create_project_tasks(project_id):
    db = get_connection()
    if db.execute("SELECT COUNT(*) n FROM tasks WHERE project_id=?", (project_id,)).fetchone()["n"]:
        db.close()
        return

    p = db.execute("SELECT plan_json FROM projects WHERE id=?", (project_id,)).fetchone()
    if not p or not p["plan_json"]:
        db.close()
        return

    plan = json.loads(p["plan_json"])
    for task in plan["tasks"]:
        db.execute(
            """INSERT INTO tasks
               (project_id,title,description,assigned_agent,status,attempts,result_status,feedback)
               VALUES(?,?,?,?,?,?,?,?)""",
            (
                project_id,
                task["title"],
                task["description"],
                task["agent"],
                "PENDING",
                0,
                None,
                None,
            ),
        )
    db.commit()
    db.close()


def _task_context(db, project_id, exclude_task_id=None):
    query = """SELECT assigned_agent,title,result
               FROM tasks
               WHERE project_id=? AND status='COMPLETED'"""
    params = [project_id]
    if exclude_task_id is not None:
        query += " AND id<>?"
        params.append(exclude_task_id)
    query += " ORDER BY id"
    rows = db.execute(query, tuple(params)).fetchall()
    return "\n\n".join(
        f"[{r['assigned_agent']}] {r['title']}\n{r['result'] or ''}" for r in rows
    )


def _run_task(project_id, task_id, context):
    db = get_connection()
    task = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    if not task:
        db.close()
        return None

    attempts = (task["attempts"] or 0) + 1
    db.execute(
        "UPDATE tasks SET status='RUNNING',attempts=? WHERE id=?",
        (attempts, task_id),
    )
    db.commit()
    db.close()

    agent = AGENTS.get(task["assigned_agent"])
    memory_context = build_memory_context(project_id, task["title"] + " " + task["description"], limit=6)
    enriched_context = "\n\n".join(part for part in (memory_context, context) if part)
    result = agent.run_structured(task["description"], enriched_context) if agent else {
        "status": "NEEDS_ATTENTION",
        "summary": "Agent unavailable",
        "output": "",
        "issues": ["Assigned agent is unavailable."],
    }

    raw = json.dumps(result, ensure_ascii=False, indent=2)
    db = get_connection()
    db.execute(
        """UPDATE tasks
           SET status='COMPLETED',result=?,result_status=?,feedback=?
           WHERE id=?""",
        (
            raw,
            result.get("status", "COMPLETED"),
            json.dumps(result.get("issues", []), ensure_ascii=False),
            task_id,
        ),
    )
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (
            project_id,
            "AGENT_EXECUTED",
            f"{task['assigned_agent']} attempt {attempts}: {task['title']} [{result.get('status', 'COMPLETED')}]",
        ),
    )
    db.commit()
    db.close()
    return result


def _rework_developer(project_id, developer_task_id, feedback, cycle):
    db = get_connection()
    task = db.execute("SELECT * FROM tasks WHERE id=?", (developer_task_id,)).fetchone()
    if not task:
        db.close()
        return None

    context = _task_context(db, project_id, developer_task_id)
    db.close()

    rework_context = (
        f"{context}\n\nQUALITY FEEDBACK (cycle {cycle}):\n{feedback}"
    )
    result = _run_task(project_id, developer_task_id, rework_context)

    db = get_connection()
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (project_id, "DEVELOPER_REWORK", f"Developer rework cycle {cycle}: {task['title']}"),
    )
    db.commit()
    db.close()
    return result


def _find_previous_developer(db, project_id, before_id):
    row = db.execute(
        """SELECT * FROM tasks
           WHERE project_id=? AND assigned_agent='Developer' AND id<?
           ORDER BY id DESC LIMIT 1""",
        (project_id, before_id),
    ).fetchone()
    return row


def execute_project(project_id):
    db = get_connection()
    project = db.execute("SELECT status FROM projects WHERE id=?", (project_id,)).fetchone()
    if not project or project["status"] != "APPROVED":
        db.close()
        return

    db.execute(
        "UPDATE projects SET status='IN_PROGRESS',updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (project_id,),
    )
    db.commit()
    db.close()

    create_project_tasks(project_id)

    db = get_connection()
    tasks = db.execute(
        "SELECT * FROM tasks WHERE project_id=? ORDER BY id", (project_id,)
    ).fetchall()
    db.close()

    for task in tasks:
        db = get_connection()
        context = _task_context(db, project_id, task["id"])
        db.close()

        result = _run_task(project_id, task["id"], context)

        if result.get("status") == "ERROR":
            db = get_connection()
            db.execute(
                "UPDATE projects SET status='EXECUTION_ERROR',updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (project_id,),
            )
            db.execute(
                "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
                (project_id, "AGENT_ERROR", f"{task['assigned_agent']} could not execute: {result.get('issues', [])}"),
            )
            db.commit()
            db.close()
            return

        if task["assigned_agent"] == "Tester":
            retries = 0
            while result.get("status") == "FAIL" and retries < MAX_QC_RETRIES:
                retries += 1
                db = get_connection()
                developer = _find_previous_developer(db, project_id, task["id"])
                db.close()

                if not developer:
                    break

                feedback = json.dumps(result.get("issues", []), ensure_ascii=False)
                _rework_developer(project_id, developer["id"], feedback, retries)

                db = get_connection()
                retest_context = _task_context(db, project_id, task["id"])
                db.close()
                result = _run_task(project_id, task["id"], retest_context)
                if result.get("status") == "ERROR":
                    db = get_connection()
                    db.execute(
                        "UPDATE projects SET status='EXECUTION_ERROR',updated_at=CURRENT_TIMESTAMP WHERE id=?",
                        (project_id,),
                    )
                    db.execute(
                        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
                        (project_id, "AGENT_ERROR", f"Tester retest failed to execute: {result.get('issues', [])}"),
                    )
                    db.commit()
                    db.close()
                    return

            if result.get("status") == "FAIL":
                db = get_connection()
                db.execute(
                    "UPDATE projects SET status='QC_FAILED',updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    (project_id,),
                )
                db.execute(
                    "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
                    (project_id, "QC_LIMIT_REACHED", "Tester still reports FAIL after retry limit."),
                )
                db.commit()
                db.close()
                return

        if task["assigned_agent"] == "Reviewer":
            retries = 0
            while result.get("status") == "NEEDS_FIX" and retries < MAX_QC_RETRIES:
                retries += 1
                db = get_connection()
                developer = _find_previous_developer(db, project_id, task["id"])
                db.close()

                if not developer:
                    break

                feedback = json.dumps(result.get("issues", []), ensure_ascii=False)
                _rework_developer(project_id, developer["id"], feedback, retries)

                db = get_connection()
                review_context = _task_context(db, project_id, task["id"])
                db.close()
                result = _run_task(project_id, task["id"], review_context)
                if result.get("status") == "ERROR":
                    db = get_connection()
                    db.execute(
                        "UPDATE projects SET status='EXECUTION_ERROR',updated_at=CURRENT_TIMESTAMP WHERE id=?",
                        (project_id,),
                    )
                    db.execute(
                        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
                        (project_id, "AGENT_ERROR", f"Reviewer retry failed to execute: {result.get('issues', [])}"),
                    )
                    db.commit()
                    db.close()
                    return

            if result.get("status") == "NEEDS_FIX":
                db = get_connection()
                db.execute(
                    "UPDATE projects SET status='QC_FAILED',updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    (project_id,),
                )
                db.execute(
                    "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
                    (project_id, "QC_LIMIT_REACHED", "Reviewer still reports NEEDS_FIX after retry limit."),
                )
                db.commit()
                db.close()
                return

    db = get_connection()
    db.execute(
        "UPDATE projects SET status='COMPLETED',updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (project_id,),
    )
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (project_id, "PROJECT_COMPLETED", "Multi-Agent Quality Control passed."),
    )
    db.commit()
    db.close()

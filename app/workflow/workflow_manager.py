from app.database.database import get_connection


def ensure_workflow(project_id):
    db = get_connection()
    workflow = db.execute(
        "SELECT * FROM workflows WHERE project_id=?", (project_id,)
    ).fetchone()

    if not workflow:
        project = db.execute(
            "SELECT name FROM projects WHERE id=?", (project_id,)
        ).fetchone()
        cur = db.execute(
            "INSERT INTO workflows(project_id,name,status) VALUES(?,?,?)",
            (project_id, f"{project['name']} — Automated Workflow", "PENDING"),
        )
        workflow_id = cur.lastrowid
    else:
        workflow_id = workflow["id"]

    count = db.execute(
        "SELECT COUNT(*) n FROM workflow_steps WHERE workflow_id=?",
        (workflow_id,),
    ).fetchone()["n"]

    if not count:
        tasks = db.execute(
            "SELECT id,title FROM tasks WHERE project_id=? ORDER BY id",
            (project_id,),
        ).fetchall()
        previous = None
        for index, task in enumerate(tasks, start=1):
            db.execute(
                """INSERT INTO workflow_steps
                   (workflow_id,task_id,step_order,depends_on)
                   VALUES(?,?,?,?)""",
                (workflow_id, task["id"], index, previous),
            )
            previous = task["id"]

    db.commit()
    row = db.execute(
        "SELECT * FROM workflows WHERE id=?", (workflow_id,)
    ).fetchone()
    db.close()
    return dict(row)


def set_workflow_status(project_id, status, current_step=None):
    db = get_connection()
    if current_step is None:
        db.execute(
            "UPDATE workflows SET status=?,updated_at=CURRENT_TIMESTAMP WHERE project_id=?",
            (status, project_id),
        )
    else:
        db.execute(
            """UPDATE workflows
               SET status=?,current_step=?,updated_at=CURRENT_TIMESTAMP
               WHERE project_id=?""",
            (status, current_step, project_id),
        )
    db.commit()
    db.close()


def mark_step_running(project_id, task_id):
    db = get_connection()
    db.execute(
        """UPDATE workflow_steps
           SET status='RUNNING',started_at=COALESCE(started_at,CURRENT_TIMESTAMP)
           WHERE workflow_id=(SELECT id FROM workflows WHERE project_id=?)
             AND task_id=?""",
        (project_id, task_id),
    )
    db.execute(
        """UPDATE workflows
           SET current_step=COALESCE(
             (SELECT step_order FROM workflow_steps
              WHERE workflow_id=workflows.id AND task_id=?), current_step),
             updated_at=CURRENT_TIMESTAMP
           WHERE project_id=?""",
        (task_id, project_id),
    )
    db.commit()
    db.close()


def mark_step_result(project_id, task_id, success=True):
    status = "COMPLETED" if success else "FAILED"
    db = get_connection()
    db.execute(
        """UPDATE workflow_steps
           SET status=?,completed_at=CASE WHEN ?='COMPLETED' THEN CURRENT_TIMESTAMP ELSE completed_at END
           WHERE workflow_id=(SELECT id FROM workflows WHERE project_id=?)
             AND task_id=?""",
        (status, status, project_id, task_id),
    )
    db.commit()
    db.close()


def is_paused(project_id):
    db = get_connection()
    row = db.execute(
        "SELECT status FROM workflows WHERE project_id=?", (project_id,)
    ).fetchone()
    db.close()
    return bool(row and row["status"] == "PAUSED")


def workflow_snapshot(project_id):
    db = get_connection()
    workflow = db.execute(
        "SELECT * FROM workflows WHERE project_id=?", (project_id,)
    ).fetchone()
    steps = db.execute(
        """SELECT ws.*,t.title,t.assigned_agent,t.status task_status,t.result_status
           FROM workflow_steps ws
           JOIN tasks t ON t.id=ws.task_id
           WHERE ws.workflow_id=(SELECT id FROM workflows WHERE project_id=?)
           ORDER BY ws.step_order""",
        (project_id,),
    ).fetchall()
    db.close()

    if not workflow:
        return {"status": "NOT_CREATED", "steps": []}

    return {
        "id": workflow["id"],
        "name": workflow["name"],
        "status": workflow["status"],
        "current_step": workflow["current_step"],
        "steps": [dict(s) for s in steps],
    }


def pause_workflow(project_id):
    ensure_workflow(project_id)
    set_workflow_status(project_id, "PAUSED")
    db = get_connection()
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (project_id, "WORKFLOW_PAUSED", "CEO paused automated workflow."),
    )
    db.execute(
        "UPDATE projects SET status='PAUSED',updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (project_id,),
    )
    db.commit()
    db.close()


def resume_workflow(project_id):
    ensure_workflow(project_id)
    set_workflow_status(project_id, "RUNNING")
    db = get_connection()
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (project_id, "WORKFLOW_RESUMED", "CEO resumed automated workflow."),
    )
    db.execute(
        "UPDATE projects SET status='APPROVED',updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (project_id,),
    )
    db.commit()
    db.close()

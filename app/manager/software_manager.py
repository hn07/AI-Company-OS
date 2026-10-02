import json
from datetime import datetime

from app.database.database import get_connection
from app.manager.qc_manager import create_project_plan, execute_project


def _extract_results(db, project_id):
    rows = db.execute(
        """SELECT assigned_agent,title,result,result_status
           FROM tasks WHERE project_id=? ORDER BY id""",
        (project_id,),
    ).fetchall()
    grouped = {}
    for row in rows:
        try:
            data = json.loads(row["result"] or "{}")
        except json.JSONDecodeError:
            data = {"output": row["result"] or "", "issues": []}
        grouped.setdefault(row["assigned_agent"], []).append(
            {
                "title": row["title"],
                "status": row["result_status"],
                "summary": data.get("summary", ""),
                "output": data.get("output", ""),
                "issues": data.get("issues", []),
            }
        )
    return grouped


def _section(items):
    lines = []
    for item in items:
        lines.append(f"## {item['title']}")
        if item["summary"]:
            lines.append(item["summary"])
        if item["output"]:
            lines.append(item["output"])
        if item["issues"]:
            lines.append("Issues: " + "; ".join(map(str, item["issues"])))
        lines.append("")
    return "\n".join(lines).strip()


def build_release(project_id):
    db = get_connection()
    project = db.execute(
        "SELECT * FROM projects WHERE id=?", (project_id,)
    ).fetchone()
    if not project:
        db.close()
        return None
    if project["status"] != "COMPLETED":
        db.close()
        return None

    grouped = _extract_results(db, project_id)
    release_version = "0.1.0"
    requirements = _section(grouped.get("Researcher", []))
    architecture = _section(
        grouped.get("Developer", [])[:1]
    )
    implementation = _section(grouped.get("Developer", []))
    test_report = _section(grouped.get("Tester", []))
    review_report = _section(grouped.get("Reviewer", []))

    notes = (
        f"Software Company release candidate {release_version}. "
        "Quality gates passed. Deployment is intentionally not automatic in V5."
    )

    cur = db.execute(
        """INSERT INTO releases
           (project_id,version,status,release_notes,requirements,architecture,
            implementation,test_report,review_report)
           VALUES(?,?,?,?,?,?,?,?,?)""",
        (
            project_id,
            release_version,
            "READY",
            notes,
            requirements,
            architecture,
            implementation,
            test_report,
            review_report,
        ),
    )
    release_id = cur.lastrowid
    db.execute(
        "UPDATE projects SET project_type='SOFTWARE',release_status='READY',updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (project_id,),
    )
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (project_id, "RELEASE_CREATED", f"Release {release_version} prepared as release #{release_id}."),
    )
    db.commit()
    db.close()
    return release_id


def execute_software_project(project_id):
    execute_project(project_id)
    db = get_connection()
    status = db.execute("SELECT status FROM projects WHERE id=?", (project_id,)).fetchone()
    db.close()
    if status and status["status"] == "COMPLETED":
        return build_release(project_id)
    return None

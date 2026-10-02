import json
from pathlib import Path
from threading import Thread

from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.database.database import init_db, get_connection
from app.llm.client import LLMClient
from app.manager.software_manager import create_project_plan, execute_software_project
from app.manager.meeting_manager import create_meeting, get_meeting, run_meeting, decide_meeting
from app.memory.memory_manager import save_memory, search_memories
from app.workflow.workflow_manager import workflow_snapshot, pause_workflow, resume_workflow
from app.routes.projects import router


BASE_DIR = Path(__file__).resolve().parent
APP_VERSION = "8.0.0"

app = FastAPI(title="AI Company OS", version=APP_VERSION)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

init_db()
app.include_router(router)


def _run_project_background(project_id: int):
    try:
        execute_software_project(project_id)
    except Exception as exc:
        db = get_connection()
        db.execute(
            "UPDATE projects SET status='EXECUTION_ERROR',updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (project_id,),
        )
        db.execute(
            "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
            (project_id, "EXECUTION_ERROR", str(exc)),
        )
        db.commit()
        db.close()


@app.get("/")
def dashboard(request: Request):
    db = get_connection()
    projects = db.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
    db.close()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "projects": projects,
            "version": APP_VERSION,
            "llm_status": LLMClient().status(),
        },
    )


@app.get("/api/llm/status")
def llm_status():
    return JSONResponse(LLMClient().status())


@app.get("/api/llm/test")
def llm_test():
    client = LLMClient()
    try:
        return JSONResponse(client.test_connection())
    except Exception as exc:
        return JSONResponse(
            {
                "ok": False,
                "provider": client.provider,
                "model": client.model,
                "message": str(exc),
            },
            status_code=503,
        )


@app.get("/api/projects/{project_id}/memories")
def project_memories(project_id: int):
    memories = search_memories(project_id, limit=30)
    return JSONResponse({"project_id": project_id, "memories": memories})


@app.post("/api/projects/{project_id}/memories")
def add_project_memory(project_id: int, content: str = Form(...), memory_key: str = Form("CEO Note"), importance: int = Form(8)):
    memory_id = save_memory(
        project_id,
        "CEO",
        "CEO_NOTE",
        memory_key.strip() or "CEO Note",
        content.strip(),
        importance,
    )
    return RedirectResponse(f"/projects/{project_id}", status_code=303)


@app.get("/api/projects/{project_id}/meeting")
def project_meeting(project_id: int):
    return JSONResponse(get_meeting(project_id) or {"status": "NOT_CREATED"})


@app.post("/api/projects/{project_id}/meeting/create")
def create_project_meeting(project_id: int):
    create_meeting(project_id)
    return RedirectResponse(f"/projects/{project_id}", status_code=303)


@app.post("/api/projects/{project_id}/meeting/run")
def run_project_meeting(project_id: int):
    Thread(
        target=run_meeting,
        args=(project_id,),
        name=f"AICompany-Meeting-{project_id}",
        daemon=True,
    ).start()
    return RedirectResponse(f"/projects/{project_id}", status_code=303)


@app.post("/api/projects/{project_id}/meeting/decision")
def meeting_decision(project_id: int, decision: str = Form(...), note: str = Form("")):
    decide_meeting(project_id, decision == "APPROVE", note.strip())
    return RedirectResponse(f"/projects/{project_id}", status_code=303)


@app.get("/api/projects/{project_id}/workflow")
def project_workflow(project_id: int):
    return JSONResponse(workflow_snapshot(project_id))


@app.post("/api/projects/{project_id}/workflow/pause")
def pause_project_workflow(project_id: int):
    pause_workflow(project_id)
    return RedirectResponse(f"/projects/{project_id}", status_code=303)


@app.post("/api/projects/{project_id}/workflow/resume")
def resume_project_workflow(project_id: int):
    resume_workflow(project_id)
    Thread(
        target=_run_project_background,
        args=(project_id,),
        name=f"AICompany-Resume-{project_id}",
        daemon=True,
    ).start()
    return RedirectResponse(f"/projects/{project_id}", status_code=303)


@app.get("/api/projects/{project_id}/progress")
def project_progress(project_id: int):
    db = get_connection()
    project = db.execute(
        "SELECT id,name,status,release_status,updated_at FROM projects WHERE id=?",
        (project_id,),
    ).fetchone()

    if not project:
        db.close()
        return JSONResponse({"error": "Project not found"}, status_code=404)

    tasks = db.execute(
        """SELECT id,title,assigned_agent,status,attempts,result_status
           FROM tasks WHERE project_id=? ORDER BY id""",
        (project_id,),
    ).fetchall()

    running = next((dict(t) for t in tasks if t["status"] == "RUNNING"), None)
    completed = sum(1 for t in tasks if t["status"] == "COMPLETED")
    total = len(tasks)

    if project["status"] == "COMPLETED":
        progress = 100
    else:
        progress = int(completed / total * 100) if total else 0

    workflow = db.execute(
        "SELECT status,current_step FROM workflows WHERE project_id=?",
        (project_id,),
    ).fetchone()

    latest = db.execute(
        """SELECT action,details,created_at FROM audit_logs
           WHERE project_id=? ORDER BY id DESC LIMIT 1""",
        (project_id,),
    ).fetchone()

    db.close()

    terminal = project["status"] in {
        "COMPLETED",
        "QC_FAILED",
        "EXECUTION_ERROR",
    }

    return JSONResponse(
        {
            "project_id": project_id,
            "status": project["status"],
            "release_status": project["release_status"],
            "progress": progress,
            "completed": completed,
            "total": total,
            "current_task": running,
            "latest_event": dict(latest) if latest else None,
            "terminal": terminal,
            "workflow": dict(workflow) if workflow else None,
        }
    )


@app.post("/projects/create")
def create_project(name: str = Form(...), description: str = Form(...)):
    db = get_connection()
    cur = db.execute(
        "INSERT INTO projects(name,description,status) VALUES(?,?,?)",
        (name.strip(), description.strip(), "DRAFT"),
    )
    project_id = cur.lastrowid
    db.commit()
    db.close()

    create_project_plan(project_id)
    return RedirectResponse(f"/projects/{project_id}", status_code=303)


@app.get("/projects/{project_id}")
def project_detail(request: Request, project_id: int):
    db = get_connection()
    project = db.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    approval = db.execute(
        "SELECT * FROM approvals WHERE project_id=? ORDER BY id DESC LIMIT 1",
        (project_id,),
    ).fetchone()
    tasks = db.execute(
        "SELECT * FROM tasks WHERE project_id=? ORDER BY id", (project_id,)
    ).fetchall()
    logs = db.execute(
        "SELECT * FROM audit_logs WHERE project_id=? ORDER BY id DESC",
        (project_id,),
    ).fetchall()
    release = db.execute(
        "SELECT * FROM releases WHERE project_id=? ORDER BY id DESC LIMIT 1",
        (project_id,),
    ).fetchone()
    workflow = workflow_snapshot(project_id)
    meeting = get_meeting(project_id)
    memories = db.execute(
        """SELECT * FROM memories
           WHERE project_id=? OR project_id IS NULL
           ORDER BY importance DESC, id DESC LIMIT 20""",
        (project_id,),
    ).fetchall()
    db.close()

    if not project:
        return {"error": "Project not found"}

    plan = None
    if project["plan_json"]:
        try:
            plan = json.loads(project["plan_json"])
        except json.JSONDecodeError:
            plan = None

    return templates.TemplateResponse(
        "project.html",
        {
            "request": request,
            "project": project,
            "approval": approval,
            "tasks": tasks,
            "audit_logs": logs,
            "plan": plan,
            "release": release,
            "memories": memories,
            "meeting": meeting,
            "workflow": workflow,
            "version": APP_VERSION,
        },
    )


@app.post("/approvals/{approval_id}/approve")
def approve(approval_id: int):
    db = get_connection()
    approval = db.execute(
        "SELECT project_id,status FROM approvals WHERE id=?", (approval_id,)
    ).fetchone()

    if not approval or approval["status"] != "PENDING":
        db.close()
        return RedirectResponse("/", status_code=303)

    project_id = approval["project_id"]

    db.execute(
        "UPDATE approvals SET status='APPROVED' WHERE id=?",
        (approval_id,),
    )
    db.execute(
        "UPDATE projects SET status='APPROVED',updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (project_id,),
    )
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (project_id, "CEO_APPROVED", f"Approval {approval_id} approved"),
    )
    db.commit()
    db.close()

    Thread(
        target=_run_project_background,
        args=(project_id,),
        name=f"AICompany-Project-{project_id}",
        daemon=True,
    ).start()

    return RedirectResponse(f"/projects/{project_id}", status_code=303)


@app.post("/approvals/{approval_id}/reject")
def reject(approval_id: int, reason: str = Form("")):
    db = get_connection()
    approval = db.execute(
        "SELECT project_id,status FROM approvals WHERE id=?", (approval_id,)
    ).fetchone()

    if not approval or approval["status"] != "PENDING":
        db.close()
        return RedirectResponse("/", status_code=303)

    project_id = approval["project_id"]
    reason = reason.strip() or "CEO requested revision"

    db.execute(
        "UPDATE approvals SET status='REJECTED',notes=? WHERE id=?",
        (reason, approval_id),
    )
    db.execute(
        "UPDATE projects SET status='REVISION',updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (project_id,),
    )
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (project_id, "CEO_REJECTED", reason),
    )
    db.commit()
    db.close()

    return RedirectResponse(f"/projects/{project_id}", status_code=303)

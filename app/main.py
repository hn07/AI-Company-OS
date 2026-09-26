import json
from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.database.database import init_db, get_connection
from app.llm.client import LLMClient
from app.manager.manager import create_project_plan, execute_project
from app.routes.projects import router


BASE_DIR = Path(__file__).resolve().parent
APP_VERSION = "2.0.0"

app = FastAPI(title="AI Company OS", version=APP_VERSION)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

init_db()
app.include_router(router)


@app.get("/")
def dashboard(request: Request):
    db = get_connection()
    projects = db.execute(
        "SELECT * FROM projects ORDER BY id DESC"
    ).fetchall()
    db.close()

    llm_status = LLMClient().status()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "projects": projects,
            "version": APP_VERSION,
            "llm_status": llm_status,
        },
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
    project = db.execute(
        "SELECT * FROM projects WHERE id=?", (project_id,)
    ).fetchone()
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
        "UPDATE approvals SET status='APPROVED' WHERE id=?", (approval_id,)
    )
    db.execute(
        "UPDATE projects SET status='APPROVED',updated_at=CURRENT_TIMESTAMP "
        "WHERE id=?",
        (project_id,),
    )
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (project_id, "CEO_APPROVED", f"Approval {approval_id} approved"),
    )
    db.commit()
    db.close()

    execute_project(project_id)
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
        "UPDATE projects SET status='REVISION',updated_at=CURRENT_TIMESTAMP "
        "WHERE id=?",
        (project_id,),
    )
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (project_id, "CEO_REJECTED", reason),
    )
    db.commit()
    db.close()

    return RedirectResponse(f"/projects/{project_id}", status_code=303)

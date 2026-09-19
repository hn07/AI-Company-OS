from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.database.database import init_db, get_db
from app.manager.manager import create_project_plan, activate_project_tasks
from app.routes.projects import router as project_router

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="AI Company", version="2.0.0")

init_db()
app.include_router(project_router)


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    db = get_db()
    projects = db.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
    approvals = db.execute(
        """SELECT approvals.*, projects.name AS project_name
           FROM approvals JOIN projects ON approvals.project_id = projects.id
           WHERE approvals.status = 'PENDING' ORDER BY approvals.id DESC"""
    ).fetchall()
    stats = {
        "projects": db.execute("SELECT COUNT(*) FROM projects").fetchone()[0],
        "tasks": db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0],
        "ready": db.execute("SELECT COUNT(*) FROM tasks WHERE status='READY'").fetchone()[0],
        "blocked": db.execute("SELECT COUNT(*) FROM tasks WHERE status='BLOCKED'").fetchone()[0],
    }
    db.close()
    return templates.TemplateResponse("index.html", {"request": request, "projects": projects, "approvals": approvals, "stats": stats})


@app.post("/projects/create")
def create_project(name: str = Form(...), description: str = Form(...)):
    db = get_db()
    cur = db.execute("INSERT INTO projects (name, description, status) VALUES (?, ?, ?)", (name.strip(), description.strip(), "DRAFT"))
    project_id = cur.lastrowid
    db.commit()
    db.close()
    create_project_plan(project_id)
    return RedirectResponse(f"/projects/{project_id}", status_code=303)


@app.get("/projects/{project_id}", response_class=HTMLResponse)
def project_detail(request: Request, project_id: int):
    db = get_db()
    project = db.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    tasks = db.execute("SELECT * FROM tasks WHERE project_id=? ORDER BY id", (project_id,)).fetchall()
    approval = db.execute("SELECT * FROM approvals WHERE project_id=? ORDER BY id DESC LIMIT 1", (project_id,)).fetchone()
    db.close()
    if not project:
        return HTMLResponse("Project not found", status_code=404)
    return templates.TemplateResponse("project.html", {"request": request, "project": project, "tasks": tasks, "approval": approval})


@app.post("/approvals/{approval_id}/approve")
def approve(approval_id: int):
    db = get_db()
    approval = db.execute("SELECT * FROM approvals WHERE id=?", (approval_id,)).fetchone()
    if approval and approval["status"] == "PENDING":
        db.execute("UPDATE approvals SET status='APPROVED', comment='CEO approved' WHERE id=?", (approval_id,))
        db.execute("UPDATE projects SET status='APPROVED', updated_at=CURRENT_TIMESTAMP WHERE id=?", (approval["project_id"],))
        db.execute("INSERT INTO audit_logs (action, details) VALUES (?, ?)", ("CEO_APPROVAL", f"Project #{approval['project_id']} approved"))
        db.commit()
        db.close()
        activate_project_tasks(approval["project_id"])
        return RedirectResponse(f"/projects/{approval['project_id']}", status_code=303)
    db.close()
    return RedirectResponse("/", status_code=303)


@app.post("/approvals/{approval_id}/reject")
def reject(approval_id: int, comment: str = Form("")):
    db = get_db()
    approval = db.execute("SELECT * FROM approvals WHERE id=?", (approval_id,)).fetchone()
    if approval and approval["status"] == "PENDING":
        db.execute("UPDATE approvals SET status='REJECTED', comment=? WHERE id=?", (comment.strip() or "CEO requested revision", approval_id))
        db.execute("UPDATE projects SET status='REVISION', updated_at=CURRENT_TIMESTAMP WHERE id=?", (approval["project_id"],))
        db.execute("INSERT INTO audit_logs (action, details) VALUES (?, ?)", ("CEO_REVISION", f"Project #{approval['project_id']}: {comment.strip()}"))
        db.commit()
    db.close()
    return RedirectResponse(f"/projects/{approval['project_id']}" if approval else "/", status_code=303)

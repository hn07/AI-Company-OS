from pathlib import Path
from fastapi import FastAPI,Request,Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.database.database import init_db,get_connection
from app.manager.manager import create_project_plan
from app.routes.projects import router

BASE_DIR=Path(__file__).resolve().parent
app=FastAPI(title="AI Company OS",version="1.0.0")
app.mount("/static",StaticFiles(directory=str(BASE_DIR/"static")),name="static")
templates=Jinja2Templates(directory=str(BASE_DIR/"templates"))
init_db()
app.include_router(router)

@app.get("/")
def dashboard(request:Request):
    db=get_connection()
    projects=db.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
    db.close()
    return templates.TemplateResponse("index.html",{"request":request,"projects":projects,"version":"1.0.0"})

@app.post("/projects/create")
def create_project(name:str=Form(...),description:str=Form(...)):
    db=get_connection()
    cur=db.execute("INSERT INTO projects(name,description,status) VALUES(?,?,?)",(name.strip(),description.strip(),"DRAFT"))
    project_id=cur.lastrowid
    db.commit(); db.close()
    create_project_plan(project_id)
    return RedirectResponse(f"/projects/{project_id}",status_code=303)

@app.get("/projects/{project_id}")
def project_detail(request:Request,project_id:int):
    db=get_connection()
    project=db.execute("SELECT * FROM projects WHERE id=?",(project_id,)).fetchone()
    approval=db.execute("SELECT * FROM approvals WHERE project_id=? ORDER BY id DESC LIMIT 1",(project_id,)).fetchone()
    tasks=db.execute("SELECT * FROM tasks WHERE project_id=? ORDER BY id",(project_id,)).fetchall()
    logs=db.execute("SELECT * FROM audit_logs WHERE project_id=? ORDER BY id DESC",(project_id,)).fetchall()
    db.close()
    if not project: return {"error":"Project not found"}
    return templates.TemplateResponse("project.html",{"request":request,"project":project,"approval":approval,"tasks":tasks,"audit_logs":logs,"version":"1.0.0"})

@app.post("/approvals/{approval_id}/approve")
def approve(approval_id:int):
    db=get_connection()
    a=db.execute("SELECT project_id FROM approvals WHERE id=?",(approval_id,)).fetchone()
    if a:
        pid=a["project_id"]
        db.execute("UPDATE approvals SET status='APPROVED' WHERE id=?",(approval_id,))
        db.execute("UPDATE projects SET status='APPROVED',updated_at=CURRENT_TIMESTAMP WHERE id=?",(pid,))
        db.execute("INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",(pid,"CEO_APPROVED",f"Approval {approval_id} approved"))
        db.commit(); db.close()
        return RedirectResponse(f"/projects/{pid}",status_code=303)
    db.close()
    return RedirectResponse("/",status_code=303)

@app.post("/approvals/{approval_id}/reject")
def reject(approval_id:int,reason:str=Form("")):
    db=get_connection()
    a=db.execute("SELECT project_id FROM approvals WHERE id=?",(approval_id,)).fetchone()
    if a:
        pid=a["project_id"]; reason=reason.strip() or "CEO requested revision"
        db.execute("UPDATE approvals SET status='REJECTED',notes=? WHERE id=?",(reason,approval_id))
        db.execute("UPDATE projects SET status='REVISION',updated_at=CURRENT_TIMESTAMP WHERE id=?",(pid,))
        db.execute("INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",(pid,"CEO_REJECTED",reason))
        db.commit(); db.close()
        return RedirectResponse(f"/projects/{pid}",status_code=303)
    db.close()
    return RedirectResponse("/",status_code=303)

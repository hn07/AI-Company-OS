from fastapi import APIRouter
from app.database.database import get_connection

router=APIRouter(prefix="/api",tags=["projects"])

@router.get("/projects")
def list_projects():
    db=get_connection()
    rows=db.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
    db.close()
    return [dict(r) for r in rows]

@router.get("/projects/{project_id}")
def get_project(project_id:int):
    db=get_connection()
    row=db.execute("SELECT * FROM projects WHERE id=?",(project_id,)).fetchone()
    db.close()
    return dict(row) if row else {"error":"Project not found"}

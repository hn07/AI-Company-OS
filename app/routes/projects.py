from fastapi import APIRouter
from app.database.database import get_db

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


@router.get("/{project_id}/tasks")
def project_tasks(project_id: int):
    db = get_db()
    tasks = db.execute("SELECT * FROM tasks WHERE project_id=? ORDER BY id", (project_id,)).fetchall()
    db.close()
    return {"project_id": project_id, "tasks": [dict(t) for t in tasks]}

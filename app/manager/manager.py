from app.database.database import get_connection

def create_project_plan(project_id: int):
    db = get_connection()
    project = db.execute("SELECT name,description FROM projects WHERE id=?",(project_id,)).fetchone()
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
    db.execute("UPDATE projects SET status='WAITING_APPROVAL',updated_at=CURRENT_TIMESTAMP WHERE id=?",(project_id,))
    db.execute("INSERT INTO approvals(project_id,action,status,notes) VALUES(?,?,?,?)",
               (project_id,"START_PROJECT","PENDING",plan))
    db.execute("INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
               (project_id,"MANAGER_PLAN",plan))
    db.commit()
    db.close()

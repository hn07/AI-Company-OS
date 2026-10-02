import json
from app.agents.multi_agent import AGENTS
from app.database.database import get_connection
from app.manager.planner import build_plan, plan_to_text

def create_project_plan(project_id):
    db=get_connection()
    p=db.execute("SELECT name,description FROM projects WHERE id=?",(project_id,)).fetchone()
    if not p: db.close(); return
    plan,provider=build_plan(p["name"],p["description"])
    db.execute("UPDATE projects SET status='WAITING_APPROVAL',plan_json=?,plan_provider=?,manager_analysis=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
               (json.dumps(plan,ensure_ascii=False),provider,plan.get("analysis",""),project_id))
    db.execute("INSERT INTO approvals(project_id,action,status,notes) VALUES(?,?,?,?)",
               (project_id,"START_PROJECT","PENDING",plan_to_text(plan,provider)))
    db.execute("INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
               (project_id,"MANAGER_PLAN",f"Provider={provider}"))
    db.commit(); db.close()

def create_project_tasks(project_id):
    db=get_connection()
    if db.execute("SELECT COUNT(*) n FROM tasks WHERE project_id=?",(project_id,)).fetchone()["n"]:
        db.close(); return
    p=db.execute("SELECT plan_json FROM projects WHERE id=?",(project_id,)).fetchone()
    if not p or not p["plan_json"]: db.close(); return
    plan=json.loads(p["plan_json"])
    for t in plan["tasks"]:
        db.execute("INSERT INTO tasks(project_id,title,description,assigned_agent,status) VALUES(?,?,?,?,?)",
                   (project_id,t["title"],t["description"],t["agent"],"PENDING"))
    db.commit(); db.close()

def execute_project(project_id):
    db=get_connection()
    p=db.execute("SELECT status FROM projects WHERE id=?",(project_id,)).fetchone()
    if not p or p["status"]!="APPROVED": db.close(); return
    db.execute("UPDATE projects SET status='IN_PROGRESS' WHERE id=?",(project_id,))
    db.commit(); db.close()
    create_project_tasks(project_id)

    db=get_connection()
    tasks=db.execute("SELECT * FROM tasks WHERE project_id=? ORDER BY id",(project_id,)).fetchall()
    db.close()
    for task in tasks:
        db=get_connection()
        prev=db.execute("SELECT assigned_agent,title,result FROM tasks WHERE project_id=? AND status='COMPLETED' ORDER BY id",(project_id,)).fetchall()
        context="\n\n".join(f"[{x['assigned_agent']}] {x['title']}\n{x['result']}" for x in prev)
        db.execute("UPDATE tasks SET status='RUNNING' WHERE id=?",(task["id"],)); db.commit(); db.close()
        agent=AGENTS.get(task["assigned_agent"])
        result=agent.run(task["description"],context) if agent else "Agent unavailable"
        db=get_connection()
        db.execute("UPDATE tasks SET status='COMPLETED',result=? WHERE id=?",(result,task["id"]))
        db.execute("INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
                   (project_id,"AGENT_EXECUTED",f"{task['assigned_agent']} completed {task['title']}"))
        db.commit(); db.close()

    db=get_connection()
    db.execute("UPDATE projects SET status='COMPLETED',updated_at=CURRENT_TIMESTAMP WHERE id=?",(project_id,))
    db.execute("INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
               (project_id,"PROJECT_COMPLETED","Multi-Agent chain completed."))
    db.commit(); db.close()

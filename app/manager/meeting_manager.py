import json

from app.agents.multi_agent import AGENTS
from app.database.database import get_connection
from app.llm.client import LLMClient


def create_meeting(project_id):
    db = get_connection()
    project = db.execute("SELECT name,description,plan_json FROM projects WHERE id=?", (project_id,)).fetchone()
    if not project:
        db.close()
        return None

    existing = db.execute(
        "SELECT * FROM meetings WHERE project_id=? ORDER BY id DESC LIMIT 1", (project_id,)
    ).fetchone()
    if existing:
        db.close()
        return dict(existing)

    objective = f"Thống nhất hướng triển khai cho project: {project['name']}."
    agenda = (
        "1. Xác nhận mục tiêu và yêu cầu.\n"
        "2. Researcher nêu yêu cầu/rủi ro.\n"
        "3. Developer đề xuất giải pháp.\n"
        "4. Tester nêu tiêu chí kiểm thử.\n"
        "5. Reviewer nêu tiêu chí chất lượng và điều kiện phát hành.\n"
        "6. Manager tổng hợp quyết định và action items."
    )
    cur = db.execute(
        "INSERT INTO meetings(project_id,title,objective,agenda,status) VALUES(?,?,?,?,?)",
        (project_id, f"AI Meeting — {project['name']}", objective, agenda, "DRAFT"),
    )
    meeting_id = cur.lastrowid
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (project_id, "MEETING_CREATED", f"AI Meeting #{meeting_id} created."),
    )
    db.commit()
    row = db.execute("SELECT * FROM meetings WHERE id=?", (meeting_id,)).fetchone()
    db.close()
    return dict(row)


def _project_context(project_id):
    db = get_connection()
    p = db.execute("SELECT name,description,plan_json FROM projects WHERE id=?", (project_id,)).fetchone()
    db.close()
    if not p:
        return ""
    return f"PROJECT: {p['name']}\nDESCRIPTION: {p['description']}\nPLAN: {p['plan_json'] or '(none)'}"


def run_meeting(project_id):
    meeting = create_meeting(project_id)
    if not meeting:
        return None

    db = get_connection()
    db.execute("UPDATE meetings SET status='RUNNING',updated_at=CURRENT_TIMESTAMP WHERE id=?", (meeting["id"],))
    db.commit()
    db.close()

    context = _project_context(project_id)
    outputs = []

    prompts = {
        "Researcher": "Hãy nêu yêu cầu quan trọng, giả định, rủi ro và thông tin còn thiếu cho project.",
        "Developer": "Hãy đề xuất kiến trúc/hướng triển khai thực tế, các phụ thuộc và điểm cần chốt.",
        "Tester": "Hãy đề xuất tiêu chí kiểm thử, các failure mode cần kiểm tra và điều kiện PASS.",
        "Reviewer": "Hãy nêu tiêu chí chất lượng, maintainability, security và điều kiện sẵn sàng phát hành.",
    }

    for name, task in prompts.items():
        agent = AGENTS[name]
        result = agent.run_structured(task, context)
        message = result.get("output") or result.get("summary") or ""
        recommendation = "; ".join(map(str, result.get("issues", [])))
        db = get_connection()
        db.execute(
            "INSERT INTO meeting_messages(meeting_id,agent_name,role,message,recommendation) VALUES(?,?,?,?,?)",
            (meeting["id"], name, agent.role, message, recommendation),
        )
        db.commit()
        db.close()
        outputs.append(f"[{name}]\n{message}\nIssues: {recommendation}")

    discussion = "\n\n".join(outputs)
    client = LLMClient()
    summary = ""
    action_items = []

    if client.provider == "ollama":
        system = (
            "You are the AI Company Project Manager chairing an internal meeting. "
            "Synthesize the agents' opinions into a neutral decision brief. "
            "Return ONLY JSON with keys summary and action_items. "
            "summary must explain agreed direction, unresolved questions and risks. "
            "action_items must be a JSON array of concrete actions."
        )
        try:
            result = client.generate_json(
                system,
                f"PROJECT CONTEXT:\n{context}\n\nAGENT DISCUSSION:\n{discussion}",
            )
            summary = str(result.get("summary", "")).strip()
            action_items = result.get("action_items", [])
        except Exception as exc:
            summary = f"Manager synthesis failed: {exc}"
            action_items = ["CEO review agent discussion manually."]
    else:
        summary = "Manager tổng hợp từ ý kiến Researcher, Developer, Tester và Reviewer. Không có LLM synthesis; CEO xem từng ý kiến trước khi quyết định."
        action_items = [
            "CEO xác nhận hướng triển khai.",
            "Chốt các rủi ro và yêu cầu còn thiếu.",
            "Chuyển action items thành task trong workflow nếu cần.",
        ]

    db = get_connection()
    db.execute(
        "INSERT INTO meeting_decisions(meeting_id,status,summary,action_items) VALUES(?,?,?,?)",
        (meeting["id"], "PENDING_CEO", summary, json.dumps(action_items, ensure_ascii=False)),
    )
    db.execute(
        "UPDATE meetings SET status='PENDING_CEO',decision=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (summary, meeting["id"]),
    )
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (project_id, "MEETING_READY", f"AI Meeting #{meeting['id']} synthesized; waiting for CEO decision."),
    )
    db.commit()
    db.close()
    return get_meeting(project_id)


def get_meeting(project_id):
    db = get_connection()
    meeting = db.execute(
        "SELECT * FROM meetings WHERE project_id=? ORDER BY id DESC LIMIT 1", (project_id,)
    ).fetchone()
    if not meeting:
        db.close()
        return None
    messages = db.execute(
        "SELECT * FROM meeting_messages WHERE meeting_id=? ORDER BY id", (meeting["id"],)
    ).fetchall()
    decision = db.execute(
        "SELECT * FROM meeting_decisions WHERE meeting_id=? ORDER BY id DESC LIMIT 1", (meeting["id"],)
    ).fetchone()
    db.close()
    data = dict(meeting)
    data["messages"] = [dict(x) for x in messages]
    data["decision"] = dict(decision) if decision else None
    if data["decision"]:
        try:
            data["decision"]["action_items"] = json.loads(data["decision"]["action_items"] or "[]")
        except json.JSONDecodeError:
            data["decision"]["action_items"] = []
    return data


def decide_meeting(project_id, approved: bool, note: str = ""):
    meeting = get_meeting(project_id)
    if not meeting or not meeting.get("decision"):
        return False

    status = "APPROVED" if approved else "REJECTED"
    db = get_connection()
    db.execute(
        "UPDATE meeting_decisions SET status=?,approved_at=CASE WHEN ?='APPROVED' THEN CURRENT_TIMESTAMP ELSE approved_at END WHERE id=?",
        (status, status, meeting["decision"]["id"]),
    )
    db.execute(
        "UPDATE meetings SET status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (status, meeting["id"]),
    )
    db.execute(
        "INSERT INTO audit_logs(project_id,action,details) VALUES(?,?,?)",
        (project_id, "MEETING_CEO_DECISION", f"{status}: {note or 'No additional note'}"),
    )
    db.commit()
    db.close()
    return True

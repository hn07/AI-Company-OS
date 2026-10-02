import re
from app.database.database import get_connection


def save_memory(project_id, agent_name, memory_type, key, content, importance=5):
    content = (content or "").strip()
    if not content:
        return None

    db = get_connection()
    cur = db.execute(
        """INSERT INTO memories
           (project_id,agent_name,memory_type,memory_key,content,importance)
           VALUES(?,?,?,?,?,?)""",
        (project_id, agent_name, memory_type, key, content, max(1, min(10, int(importance)))),
    )
    db.commit()
    memory_id = cur.lastrowid
    db.close()
    return memory_id


def _tokens(text):
    return set(re.findall(r"[a-zA-ZÀ-ỹ0-9_]{3,}", (text or "").lower()))


def search_memories(project_id, query="", limit=8):
    db = get_connection()
    rows = db.execute(
        """SELECT id,project_id,agent_name,memory_type,memory_key,content,importance,created_at
           FROM memories
           WHERE project_id=? OR project_id IS NULL
           ORDER BY importance DESC, id DESC""",
        (project_id,),
    ).fetchall()
    db.close()

    query_tokens = _tokens(query)
    scored = []
    for row in rows:
        text = f"{row['memory_key'] or ''} {row['content']}"
        overlap = len(query_tokens & _tokens(text))
        score = overlap * 10 + (row["importance"] or 5)
        scored.append((score, dict(row)))

    scored.sort(key=lambda x: (x[0], x[1]["id"]), reverse=True)
    return [item for _, item in scored[:max(1, limit)]]


def build_memory_context(project_id, query="", limit=6):
    memories = search_memories(project_id, query, limit)
    if not memories:
        return ""

    lines = ["RELEVANT AI MEMORY:"]
    for memory in memories:
        owner = memory["agent_name"] or "Company"
        lines.append(
            f"- [{owner}] {memory['memory_type']} / {memory['memory_key'] or 'general'}: "
            f"{memory['content']}"
        )
    return "\n".join(lines)


def remember_task_result(project_id, agent_name, task_title, result):
    summary = result.get("summary", "")
    output = result.get("output", "")
    issues = result.get("issues", [])

    parts = []
    if summary:
        parts.append(summary)
    if output:
        parts.append(output[:3000])
    if issues:
        parts.append("Issues: " + "; ".join(map(str, issues)))

    content = "\n".join(parts).strip()
    if not content:
        return None

    importance = 8 if agent_name in {"Tester", "Reviewer"} else 6
    return save_memory(
        project_id,
        agent_name,
        "TASK_RESULT",
        task_title,
        content,
        importance,
    )

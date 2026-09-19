from app.database.database import get_db


DEFAULT_TASKS = [
    {
        "title": "Phân tích yêu cầu",
        "description": "Xác định phạm vi, yêu cầu chính và tiêu chí hoàn thành của dự án.",
        "agent": "Researcher",
        "priority": "HIGH",
        "dependency": "",
    },
    {
        "title": "Nghiên cứu giải pháp",
        "description": "Nghiên cứu công nghệ, phương án triển khai và các rủi ro kỹ thuật.",
        "agent": "Researcher",
        "priority": "HIGH",
        "dependency": "1",
    },
    {
        "title": "Thiết kế kiến trúc",
        "description": "Đề xuất kiến trúc hệ thống và cấu trúc triển khai dựa trên kết quả nghiên cứu.",
        "agent": "Developer",
        "priority": "HIGH",
        "dependency": "2",
    },
    {
        "title": "Thực hiện",
        "description": "Triển khai phần việc kỹ thuật theo kiến trúc đã được xác định.",
        "agent": "Developer",
        "priority": "MEDIUM",
        "dependency": "3",
    },
    {
        "title": "Kiểm thử",
        "description": "Kiểm tra chức năng và ghi nhận lỗi hoặc điểm chưa đạt.",
        "agent": "Tester",
        "priority": "MEDIUM",
        "dependency": "4",
    },
    {
        "title": "Kiểm duyệt",
        "description": "Đánh giá độc lập kết quả trước khi báo cáo Manager và CEO.",
        "agent": "Reviewer",
        "priority": "MEDIUM",
        "dependency": "5",
    },
    {
        "title": "Báo cáo CEO",
        "description": "Tổng hợp kết quả, trạng thái và các vấn đề cần CEO quyết định.",
        "agent": "Manager",
        "priority": "LOW",
        "dependency": "6",
    },
]


def _build_plan(description: str) -> str:
    return f"""MỤC TIÊU\n{description}\n\nKẾ HOẠCH V2\n1. Phân tích yêu cầu\n2. Nghiên cứu giải pháp\n3. Thiết kế kiến trúc\n4. Thực hiện\n5. Kiểm thử\n6. Kiểm duyệt\n7. Báo cáo CEO\n\nTASK ENGINE\n- Task/Subtask có trạng thái, priority và dependency.\n- Task chỉ được kích hoạt sau khi CEO phê duyệt kế hoạch.\n- Dependency phải hoàn thành trước khi task tiếp theo READY.\n\nAGENTS\n- Researcher: nghiên cứu và phân tích\n- Developer: thiết kế và thực hiện kỹ thuật\n- Tester: kiểm thử\n- Reviewer: kiểm duyệt\n- Manager: điều phối và báo cáo\n\nQUYỀN HẠN\nProject chỉ được triển khai sau khi CEO phê duyệt.\n"""


def create_project_plan(project_id: int):
    db = get_db()
    project = db.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    if not project:
        db.close()
        return

    plan = _build_plan(project["description"])
    db.execute(
        "UPDATE projects SET plan=?, status='WAITING_APPROVAL', updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (plan, project_id),
    )

    # Keep plan generation idempotent: do not duplicate approval requests/tasks.
    db.execute("DELETE FROM approvals WHERE project_id=? AND type='PROJECT_PLAN' AND status='PENDING'", (project_id,))
    db.execute(
        "INSERT INTO approvals (project_id, type, status) VALUES (?, ?, 'PENDING')",
        (project_id, "PROJECT_PLAN"),
    )

    # Replace only Manager-generated pending tasks. Tasks are inert until approval.
    db.execute("DELETE FROM tasks WHERE project_id=?", (project_id,))
    for index, item in enumerate(DEFAULT_TASKS, start=1):
        status = "READY" if not item["dependency"] else "BLOCKED"
        db.execute(
            """INSERT INTO tasks
            (project_id, parent_task_id, title, description, assigned_agent, priority, status, dependency)
            VALUES (?, NULL, ?, ?, ?, ?, ?, ?)""",
            (project_id, item["title"], item["description"], item["agent"], item["priority"], status, item["dependency"]),
        )

    db.execute(
        "INSERT INTO audit_logs (action, details) VALUES (?, ?)",
        ("MANAGER_PLAN", f"Created V2 task plan for Project #{project_id}"),
    )
    db.commit()
    db.close()


def activate_project_tasks(project_id: int):
    db = get_db()
    tasks = db.execute(
        "SELECT * FROM tasks WHERE project_id=? ORDER BY id", (project_id,)
    ).fetchall()
    for task in tasks:
        status = "READY" if not task["dependency"] else "BLOCKED"
        db.execute("UPDATE tasks SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (status, task["id"]))
    db.execute(
        "INSERT INTO audit_logs (action, details) VALUES (?, ?)",
        ("TASK_QUEUE_ACTIVATED", f"Activated task queue for Project #{project_id}"),
    )
    db.commit()
    db.close()

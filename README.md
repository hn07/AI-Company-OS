# AI Company OS

## V2.0.0 — AI Project Manager

V2 kế thừa Foundation Core V1 và bổ sung Project Management Engine:

- Task / Subtask model
- Priority
- Dependency
- Status: PENDING, BLOCKED, READY, RUNNING, WAITING_REVIEW, COMPLETED, FAILED, CANCELLED
- Agent assignment
- Task Queue
- CEO Approval Gate trước khi kích hoạt Task Queue
- V1 → V2 SQLite migration tự động
- Dashboard thống kê Projects / Tasks / READY / BLOCKED
- API `/api/projects/{project_id}/tasks`

### Luồng

CEO giao mục tiêu → Manager lập kế hoạch → tạo Task Queue → CEO Approval → kích hoạt Task Queue.

**V2.0.0 chưa kết nối LLM.** LLM Adapter sẽ được triển khai ở V2.1.0 sau khi lõi Project Manager ổn định.

## Chạy

```bat
install.bat
run.bat
```

Mở `http://127.0.0.1:8000`.

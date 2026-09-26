# AI Company OS

## V1.1.0 — AI Team Execution Foundation

Local-first foundation for an AI-managed company.

### Current workflow

CEO → Manager → Project Plan → CEO Approval → Researcher → Developer → Tester → Reviewer → Final Report

### V1.1.0 includes
- CEO project creation.
- Manager plan generation.
- CEO approval / revision.
- Automatic execution after CEO approval.
- Standard task pipeline.
- Researcher / Developer / Tester / Reviewer agent stubs.
- Project lifecycle tracking: DRAFT, WAITING_APPROVAL, APPROVED, IN_PROGRESS, TESTING, REVIEW, COMPLETED, REVISION.
- Task status and results.
- SQLite persistence.
- Audit Log.
- FastAPI web dashboard.

### Important

V1.1.0 is intentionally local and free. The agents currently simulate execution locally. There is no LLM API connection and therefore no API cost.

### Run on Windows

1. Install Python 3.12.
2. Open the repository folder.
3. Run `install.bat`.
4. Run `run.bat`.
5. Open `http://127.0.0.1:8000`.

### Test flow

Create a project such as **Test AI Company OS** with the objective **Build a small internal automation tool.** Then:

1. Manager generates the plan.
2. CEO clicks **CEO APPROVE & START**.
3. The system creates execution tasks.
4. Researcher executes research.
5. Developer executes design and implementation.
6. Tester executes testing.
7. Reviewer executes quality review.
8. Project becomes COMPLETED.
9. Audit Log records the lifecycle.

### Architecture

- Python
- FastAPI
- Jinja2
- SQLite
- Local deterministic agents

### Repository

https://github.com/hn07/AI-Company-OS

### Version roadmap

- V1.0.0: Foundation / CEO Approval Core
- V1.1.0: AI Team Execution Foundation
- V1.x: V1 improvements and hardening
- V2.0.0: AI Project Manager + real planning/orchestration
- V3.0.0: Multi-Agent
- V4.0.0: Quality Control
- V5.0.0: Software Company
- V6.0.0: AI Memory
- V7.0.0: Workflow Automation
- V8.0.0: AI Meeting
- V9.0.0: Self Healing
- V10.0.0: AI Company 1.0

### License

To be decided by the CEO.

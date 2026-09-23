# AI Company OS

## V1.0.0 — Foundation / CEO Approval Core

Local-first foundation for an AI-managed company.

### Workflow
CEO → Manager → Project Plan → CEO Approval → Agent foundation → Audit Log

### V1.0.0 includes
- CEO project creation
- Manager plan generation
- CEO approval / revision
- Project status tracking
- Agent registry
- SQLite persistence
- Audit logging
- FastAPI web dashboard

Agents are intentionally lightweight stubs. LLM integration and automatic orchestration are reserved for later versions.

### Status
DRAFT → WAITING_APPROVAL → APPROVED

Revision path: WAITING_APPROVAL → REVISION

### Run on Windows
1. Install Python 3.12.
2. Run `install.bat`.
3. Run `run.bat`.
4. Open `http://127.0.0.1:8000`.

### Repository
https://github.com/hn07/AI-Company-OS

### Versioning
- V1.0.0: Foundation / CEO Approval Core
- V1.0.x: bug fixes
- V1.1.x: additional V1 capabilities
- V2.0.0: AI Project Manager

## License
To be decided by the CEO.

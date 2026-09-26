# Changelog

## [1.1.0] - 2026-09-26

### Added
- Deterministic AI Team execution pipeline after CEO approval.
- Automatic task creation for Researcher, Developer, Tester and Reviewer.
- Project lifecycle: APPROVED → IN_PROGRESS → TESTING → REVIEW → COMPLETED.
- Task execution status and result display.
- Manager final execution report in Audit Log.
- Expanded CEO dashboard and project execution UI.

### Notes
- Agents are still local stubs in V1.1.0.
- No LLM/API cost is required.
- Real LLM orchestration is planned for V2.0.0.

## [1.0.0] - 2026-09-23

### Added
- CEO project creation.
- Manager plan generation.
- CEO approval / revision.
- Project status tracking.
- Agent registry.
- SQLite persistence.
- Audit logging.
- FastAPI web dashboard.

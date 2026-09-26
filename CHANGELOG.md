# Changelog

## [2.0.0] - 2026-09-26

### Added
- AI Project Manager planning layer.
- Structured project plans with analysis, objective, risks and dynamic tasks.
- Local deterministic planner that requires no API key or paid service.
- Optional Ollama provider for local LLM planning.
- V1.x database migration for V2 planning fields.
- Planning engine status on the CEO dashboard.
- Dynamic task creation from the approved Manager plan.

### Architecture
- `app/manager/planner.py` handles plan generation and validation.
- `app/llm/client.py` handles local LLM provider access.
- Default provider: `mock` / deterministic local planner.
- Optional provider: `ollama`.

## [1.1.0] - 2026-09-26

### Added
- Deterministic AI Team execution pipeline after CEO approval.
- Automatic task creation for Researcher, Developer, Tester and Reviewer.
- Project lifecycle: APPROVED → IN_PROGRESS → TESTING → REVIEW → COMPLETED.
- Task execution status and result display.
- Manager final execution report in Audit Log.

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

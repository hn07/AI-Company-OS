# Changelog

## [6.0.1] - 2026-10-02

### Fixed
- Tester uses evidence-based PASS/FAIL behavior and does not invent failures from missing runnable artifacts.
- LLM execution errors are separated from genuine QC failures.
- Tester/Reviewer retry execution errors now stop as EXECUTION_ERROR instead of consuming QC retries.

## [6.0.0] - 2026-10-02

### Added
- Project-scoped AI Memory storage in SQLite.
- Automatic memory creation from Researcher, Developer, Tester and Reviewer task results.
- Memory retrieval and injection into subsequent Agent context.
- CEO Note memory entry from the project UI.
- Project Memory API for listing and adding memories.

### Workflow
CEO → Manager → Approval → AI Team + Memory → QC → Release Candidate

## [5.1.1] - 2026-10-02

### Fixed
- Fixed invalid JavaScript escaping in the V5.1.0 project live monitor.
- Restored automatic polling of `/api/projects/{project_id}/progress` every 1.5 seconds.
- Live monitor now updates progress, task count, current agent/task and latest activity correctly.

# Changelog

## [5.1.0] - 2026-10-02

### Added
- Background execution for approved software projects.
- Live project progress API at `/api/projects/{project_id}/progress`.
- Project execution monitor with progress, current agent, current task and latest audit activity.
- Automatic polling every 1.5 seconds on the project page.
- Execution error state `EXECUTION_ERROR` with audit logging.
- CEO approval endpoint now returns immediately while the AI pipeline continues in a background thread.

### Workflow
CEO → Manager → Approval → Background AI Team → QC → Release Candidate

## [5.0.0] - 2026-10-02

### Added
- Software Company orchestration layer.
- Release Candidate generation after QC completion.
- Requirements, architecture, implementation, test and review artifacts.
- Software release registry in SQLite.
- Project release status tracking.
- Release creation is gated by COMPLETED quality status.
- Deployment remains manual; V5 does not auto-publish software.

### Workflow
CEO → Manager → Approval → Researcher → Developer → Tester/QC → Reviewer/QC → Release Candidate

## [4.0.0] - 2026-10-02
- Quality Control pipeline.
- Tester PASS/FAIL.
- Reviewer APPROVED/NEEDS_FIX.
- Developer rework and bounded QC retries.
- QC_FAILED state.

## [3.0.0] - 2026-09-30
- Multi-Agent execution chain.

## [2.1.0] - 2026-09-26
- Hardened local Ollama integration.

## [2.0.0] - 2026-09-26
- AI Project Manager planning layer.

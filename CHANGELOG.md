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

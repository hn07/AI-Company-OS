# Changelog

## [5.0.1] - 2026-10-02

### Fixed
- Corrected a malformed comment that prevented the V4 migration from adding the tasks.attempts column.
- Ensure attempts, result_status and feedback are migrated on existing SQLite databases.
- Preserves existing project and task data; no database reset is required.

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

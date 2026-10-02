# Changelog

## [4.0.0] - 2026-10-02

### Added
- Quality Control pipeline after Multi-Agent execution.
- Tester now returns PASS/FAIL.
- Reviewer now returns APPROVED/NEEDS_FIX.
- Developer rework loop when Tester or Reviewer reports a problem.
- Maximum 3 QC retry cycles to prevent infinite loops.
- Task attempts, result status and feedback fields.
- Audit events for agent execution, developer rework and QC limit reached.
- Project status QC_FAILED when quality gates remain unresolved.

### Workflow
CEO → Manager → CEO Approval → Researcher → Developer → Tester
→ FAIL? → Developer Rework → Tester Retest
→ PASS → Reviewer
→ NEEDS_FIX? → Developer Rework → Reviewer Retest
→ APPROVED → COMPLETED

## [3.0.0] - 2026-09-30
- Multi-Agent execution chain.
- Researcher, Developer, Tester and Reviewer agents.
- Agent outputs passed as context to subsequent agents.

## [2.1.0] - 2026-09-26
- Hardened local Ollama integration.
- Ollama model availability detection.
- CEO Dashboard AI status.
- Local AI connection test endpoint.

## [2.0.0] - 2026-09-26
- AI Project Manager planning layer.
- Structured plans, risks and dynamic tasks.
- Deterministic local planner and optional Ollama.

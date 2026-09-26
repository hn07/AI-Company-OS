# Changelog

## [2.1.0] - 2026-09-26

### Added
- Hardened local Ollama integration.
- Ollama model availability detection from /api/tags.
- CEO Dashboard AI status now shows Ollama online/offline and selected model availability.
- Local AI connection test endpoint.
- JSON API endpoints: /api/llm/status and /api/llm/test.
- No new Python dependency; Ollama access still uses Python standard library.
- Mock/deterministic planner remains the zero-cost default.

### Notes
- V2.1.0 does not require Ollama.
- When Ollama is enabled but unavailable, project planning still falls back to the deterministic local planner.

## [2.0.0] - 2026-09-26
- AI Project Manager planning layer.
- Structured plans, risks and dynamic tasks.
- Deterministic local planner and optional Ollama.
- V1.x database migration for planning fields.

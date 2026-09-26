# AI Company OS

## V2.0.0 — AI Project Manager

Local-first operating foundation for an AI-managed company.

### Current workflow

CEO → AI Project Manager → Dynamic Plan → CEO Approval → AI Team → Tester → Reviewer → Final Report

### V2.0.0 adds

- AI Project Manager planning layer.
- Structured plan:
  - Analysis
  - Objective
  - Risks
  - Dynamic execution tasks
- Task-to-agent assignment generated from the plan.
- Plan validation before CEO approval.
- Local deterministic planner by default.
- Optional local Ollama LLM.
- Automatic database migration from V1.x.
- Dynamic task execution based on the approved plan.
- Planning engine status on the CEO Dashboard.
- Full Audit Log.

### Zero-cost default

The default configuration is:

`LLM_PROVIDER=mock`

This does not call an external AI API.

To use a real local LLM, install Ollama separately, pull a model, then set:

`LLM_PROVIDER=ollama`

and configure `OLLAMA_MODEL` in `.env`.

### V2 architecture

```
CEO
 |
 v
AI Project Manager
 |
 +--> Analysis
 +--> Objective
 +--> Risks
 +--> Dynamic Task Plan
 |
 v
CEO Approval
 |
 v
+-------------+-------------+-------------+
| Researcher  | Developer   | Tester      |
+-------------+-------------+-------------+
                    |
                    v
                 Reviewer
                    |
                    v
              Final Report
```

### Windows

Use Python 3.12 for the current stable environment.

```bat
cd /d D:\MyWorkSpace\AI-Company-OS
git fetch origin
git checkout v2.0.0
install.bat
run.bat
```

Open:

`http://127.0.0.1:8000`

### Test V2

Create a project with a natural CEO request, for example:

**Project:** Internal Invoice Automation

**Request:** Build an internal tool that reads invoice data and prepares warehouse import information.

The Manager should create a structured plan and show the planning provider.

Then CEO approves the plan. The approved dynamic tasks are created and executed.

### Ollama configuration

Copy `.env.example` to `.env` and set:

```
LLM_PROVIDER=ollama
OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:7b
```

If Ollama is unavailable, V2 automatically falls back to the deterministic local planner.

### Version roadmap

- V1.0.0: Foundation / CEO Approval Core
- V1.1.0: AI Team Execution Foundation
- V2.0.0: AI Project Manager
- V3.0.0: Multi-Agent
- V4.0.0: Quality Control
- V5.0.0: Software Company
- V6.0.0: AI Memory
- V7.0.0: Workflow Automation
- V8.0.0: AI Meeting
- V9.0.0: Self Healing
- V10.0.0: AI Company 1.0
- V11.0.0+: Multi-project and Company expansion

### Repository

https://github.com/hn07/AI-Company-OS

### License

To be decided by the CEO.

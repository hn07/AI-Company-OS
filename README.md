# AI Company OS

## V8.0.1 — QC & Ollama Reliability

V8.0.1 prevents an Ollama/JSON execution problem from turning into a misleading repeated Tester FAIL. Agents validate structured status and use a deterministic local fallback when Ollama cannot return a valid result; the fallback reason is recorded in the task issues.

## V8.0.0 — AI Meeting

V8 adds an internal AI Meeting layer where Researcher, Developer, Tester and Reviewer submit structured opinions. The Manager synthesizes a decision brief and the CEO explicitly approves or requests a re-meeting.

### V8 workflow

CEO → Manager Plan → CEO Approval → AI Meeting → Agent Opinions → Manager Decision Brief → CEO Decision → Workflow → QC → Release

### V8.0.0 adds

- Persistent AI Meeting, messages and decision tables in SQLite.
- Meeting agenda generated from the project context.
- Researcher / Developer / Tester / Reviewer structured opinions.
- Manager synthesis using local Ollama when enabled; deterministic fallback without LLM.
- CEO approval or re-meeting decision with audit log.
- Meeting panel directly on the project page.

## V7.0.0 — Workflow Automation

AI Company OS is a local-first multi-agent company operating system.

### V7.0 workflow

CEO → AI Project Manager → Dynamic Plan → CEO Approval → Workflow Engine → AI Team → QC → Release Candidate

### V7.0.0 adds

- Persisted Workflow Engine and workflow steps.
- Automatic dependency-aware execution of Manager tasks.
- Pause/Resume workflow controls.
- Workflow status exposed in the live monitor.

### V6.0.0 adds

- SQLite AI Memory for project knowledge.
- Automatic memory from completed agent results.
- Memory retrieval is injected into later agent tasks.
- CEO can add explicit project notes as memory.

### V5.1.1 adds

- Fixes the project monitor JavaScript so polling actually starts.
- Keeps the V5.1.0 background execution workflow unchanged.

### V5.1.0 adds

- CEO approval no longer waits for the entire AI pipeline.
- AI execution runs in a background thread.
- Live progress monitor on the project page.
- Current agent and current task display.
- Completed task count and progress percentage.
- Latest audit activity display.
- Automatic page refresh after terminal status.
- `EXECUTION_ERROR` state and audit log when background execution fails.

### Local Ollama

```env
LLM_PROVIDER=ollama
OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_TIMEOUT=120
```

### Windows — pull V7.0.0

```bat
cd /d D:\MyWorkSpace\AI-Company-OS
git fetch origin
git checkout v7.0.0
git pull origin v7.0.0
install.bat
run.bat
```

Open `http://127.0.0.1:8000`.

### Test

Create:

**Name**
`Internal Invoice Automation`

**Description**
`Xây dựng phần mềm đọc dữ liệu hóa đơn và chuẩn bị thông tin nhập kho.`

After the CEO approves, the browser returns immediately. The project page shows the live execution monitor while Ollama/AI agents continue in the background.

### Roadmap

- V1.0.0: Foundation / CEO Approval Core
- V1.1.0: AI Team Execution Foundation
- V2.0.0: AI Project Manager
- V2.1.0: Local Ollama AI
- V3.0.0: Multi-Agent
- V4.0.0: Quality Control
- V5.0.0: Software Company
- **V6.0.0: AI Memory**
- V5.1.0: Background Execution + Live Monitor
- V6.0.0: AI Memory
- V7.0.0: Workflow Automation
- V8.0.0: AI Meeting
- V9.0.0: Self Healing
- V10.0.0: AI Company 1.0
- V11.0.0+: Multi-project and Company expansion

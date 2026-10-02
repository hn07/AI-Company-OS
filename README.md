# AI Company OS

## V5.1.0 — Background AI Execution + Live Monitor

AI Company OS is a local-first multi-agent company operating system.

### V5.1 workflow

CEO → AI Project Manager → Dynamic Plan → CEO Approval → Background AI Team → Tester/QC → Reviewer/QC → Release Candidate

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

### Windows — pull V5.1.0

```bat
cd /d D:\MyWorkSpace\AI-Company-OS
git fetch origin
git checkout v5.1.0
git pull origin v5.1.0
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
- **V5.1.0: Background Execution + Live Monitor**
- V6.0.0: AI Memory
- V7.0.0: Workflow Automation
- V8.0.0: AI Meeting
- V9.0.0: Self Healing
- V10.0.0: AI Company 1.0
- V11.0.0+: Multi-project and Company expansion

# AI Company OS

## V4.0.0 — Quality Control

Local-first operating foundation for an AI-managed company.

### Current workflow

CEO → AI Project Manager → Dynamic Plan → CEO Approval → Researcher → Developer → Tester → Reviewer → Final Report

### V4.0.0 adds

- Tester quality gate: PASS / FAIL.
- Reviewer quality gate: APPROVED / NEEDS_FIX.
- Automatic Developer rework when QC fails.
- Automatic Tester/Reviewer retest after rework.
- Maximum 3 retry cycles per quality gate.
- Task attempt counters and QC feedback.
- Audit Log for every QC decision.
- QC_FAILED status when the retry limit is reached.

### Zero-cost default

`LLM_PROVIDER=mock`

The local mode uses deterministic/rule-based agents and does not call an external AI API.

### Optional local AI

Set:

```env
LLM_PROVIDER=ollama
OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_TIMEOUT=120
```

### Windows

```bat
cd /d D:\MyWorkSpace\AI-Company-OS
git fetch origin
git checkout v4.0.0
git pull origin v4.0.0
install.bat
run.bat
```

Open `http://127.0.0.1:8000`.

### Test V4

Create a project such as:

**Name:** Internal Invoice Automation

**Description:** Xây dựng phần mềm đọc dữ liệu hóa đơn và chuẩn bị thông tin nhập kho.

1. CEO creates the project.
2. Manager creates the dynamic plan.
3. CEO approves the plan.
4. Researcher and Developer execute.
5. Tester checks the result.
6. If Tester returns FAIL, Developer receives feedback and is run again.
7. Tester retests, up to 3 QC cycles.
8. Reviewer checks release quality.
9. If Reviewer returns NEEDS_FIX, Developer reworks and Reviewer retests.
10. Project becomes COMPLETED only after the quality gates pass.

### Roadmap

- V1.0.0: Foundation / CEO Approval Core
- V1.1.0: AI Team Execution Foundation
- V2.0.0: AI Project Manager
- V2.1.0: Local Ollama AI
- V3.0.0: Multi-Agent
- **V4.0.0: Quality Control**
- V5.0.0: Software Company
- V6.0.0: AI Memory
- V7.0.0: Workflow Automation
- V8.0.0: AI Meeting
- V9.0.0: Self Healing
- V10.0.0: AI Company 1.0
- V11.0.0+: Multi-project and Company expansion

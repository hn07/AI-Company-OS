# AI Company OS

## V5.0.0 — Software Company

AI Company OS is a local-first multi-agent company operating system.

### V5 workflow

CEO → AI Project Manager → Dynamic Plan → CEO Approval → Researcher → Developer → Tester → Reviewer → Release Candidate

### V5.0.0 adds

- Software project lifecycle.
- Requirements artifact.
- Architecture artifact.
- Implementation artifact.
- Test report.
- Review report.
- Release Candidate registry.
- Release version tracking.
- Release is created only after quality gates pass.
- Deployment is still manual and requires a future approval/deployment layer.

### Zero-cost default

`LLM_PROVIDER=mock`

No external AI API is required for the default local workflow.

### Optional local AI

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
git checkout v5.0.0
git pull origin v5.0.0
install.bat
run.bat
```

Open `http://127.0.0.1:8000`.

### Test V5

Create:

**Name**
`Internal Invoice Automation`

**Description**
`Xây dựng phần mềm đọc dữ liệu hóa đơn và chuẩn bị thông tin nhập kho.`

After CEO approval, the system runs the AI Team and QC. When the project reaches COMPLETED, V5 automatically creates a Release Candidate such as `v0.1.0`.

The project page shows:
- Requirements
- Architecture
- Implementation
- Test Report
- Review Report
- Release status
- Audit Log

### Roadmap

- V1.0.0: Foundation / CEO Approval Core
- V1.1.0: AI Team Execution Foundation
- V2.0.0: AI Project Manager
- V2.1.0: Local Ollama AI
- V3.0.0: Multi-Agent
- V4.0.0: Quality Control
- **V5.0.0: Software Company**
- V6.0.0: AI Memory
- V7.0.0: Workflow Automation
- V8.0.0: AI Meeting
- V9.0.0: Self Healing
- V10.0.0: AI Company 1.0
- V11.0.0+: Multi-project and Company expansion

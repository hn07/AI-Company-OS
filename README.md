# AI Company OS

## V2.1.0 — Local AI / Ollama hardening

Local-first operating foundation for an AI-managed company.

### Current workflow

CEO → AI Project Manager → Dynamic Plan → CEO Approval → AI Team → Tester → Reviewer → Final Report

### V2.1.0 adds

- Stronger Ollama integration.
- Detection of whether the configured Ollama model is installed.
- CEO Dashboard AI status.
- One-click Test AI endpoint.
- /api/llm/status for provider/model status.
- /api/llm/test for a real local-model JSON test.
- Zero additional Python dependencies.

### Zero-cost default

LLM_PROVIDER=mock

This uses the deterministic local planner and does not call an external AI API.

### Enable local AI

1. Install Ollama on Windows.
2. Start Ollama.
3. Run ollama_setup.bat.
4. Create .env from .env.example.
5. Set LLM_PROVIDER=ollama.
6. Run run.bat.
7. On the CEO Dashboard confirm Ollama ONLINE and Model READY.
8. Click Test AI.
9. Create a project and verify the plan provider becomes ollama.

If Ollama or the selected model is unavailable, the system keeps using the deterministic local planner.

### Windows

cd /d D:\MyWorkSpace\AI-Company-OS
git fetch origin
git checkout v2.1.0
git pull origin v2.1.0
install.bat
run.bat

Open: http://127.0.0.1:8000

### Roadmap

- V1.0.0: Foundation / CEO Approval Core
- V1.1.0: AI Team Execution Foundation
- V2.0.0: AI Project Manager
- V2.1.0: Local Ollama AI
- V3.0.0: Multi-Agent
- V4.0.0: Quality Control
- V5.0.0: Software Company
- V6.0.0: AI Memory
- V7.0.0: Workflow Automation
- V8.0.0: AI Meeting
- V9.0.0: Self Healing
- V10.0.0: AI Company 1.0
- V11.0.0+: Multi-project and Company expansion

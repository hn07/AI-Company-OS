import json
import os
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen


def _load_dotenv():
    env_file = Path(__file__).resolve().parents[2] / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_dotenv()


class LLMClient:
    """Provider wrapper for the local planner and optional local Ollama."""

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "mock").lower()
        self.base_url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "120"))

    def status(self) -> dict:
        if self.provider != "ollama":
            return {
                "provider": self.provider,
                "available": True,
                "model": "deterministic-local-planner",
                "model_available": True,
            }

        try:
            request = Request(
                f"{self.base_url}/api/tags",
                headers={"Accept": "application/json"},
                method="GET",
            )
            with urlopen(request, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))

            models = [m.get("name", "") for m in data.get("models", [])]
            model_available = self.model in models or any(
                name.split(":")[0] == self.model.split(":")[0] for name in models
            )

            return {
                "provider": "ollama",
                "available": True,
                "model": self.model,
                "model_available": model_available,
                "models": models,
            }
        except Exception as exc:
            return {
                "provider": "ollama",
                "available": False,
                "model": self.model,
                "model_available": False,
                "models": [],
                "error": str(exc),
            }

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict:
        if self.provider != "ollama":
            raise RuntimeError("LLM provider is not Ollama")

        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        body = json.dumps(payload).encode("utf-8")
        request = Request(
            f"{self.base_url}/api/chat",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc

        data = json.loads(raw)
        content = data.get("message", {}).get("content", "")
        if not content:
            raise RuntimeError("Ollama returned an empty response")

        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Ollama returned invalid JSON") from exc

    def test_connection(self) -> dict:
        if self.provider != "ollama":
            return {
                "ok": True,
                "provider": self.provider,
                "message": "Local deterministic planner is active; no external AI call is used.",
            }

        result = self.generate_json(
            'Return JSON only with exactly one key: "message".',
            'Set "message" to "AI Company OS local AI test OK".',
        )
        if result.get("message") != "AI Company OS local AI test OK":
            raise RuntimeError("Ollama responded, but the test response was unexpected.")

        return {
            "ok": True,
            "provider": "ollama",
            "model": self.model,
            "message": "Ollama local model test OK.",
        }

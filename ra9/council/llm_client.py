from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Optional
import os


@dataclass
class LLMConfig:
    provider: str = "gemini"  # "gemini" | "mock"
    model: str = "gemini-2.5-flash"
    temperature: float = 0.2
    max_tokens: int = 512
    top_p: float = 1.0
    timeout_s: float = 20.0
    retries: int = 2


class LLMClient:
    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        self.config = config or load_llm_config_from_env()

    def complete(self, prompt: str, **kwargs: Any) -> str:
        cfg = self.config
        provider = (cfg.provider or os.getenv("RA9_LLM_PROVIDER", "gemini")).lower()
        if provider == "ollama":
            try:
                return self._complete_ollama(prompt)
            except Exception:
                provider = "mock"
        if provider == "gemini":
            # Fallback to mock if no keys are configured
            if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")):
                provider = "mock"
            else:
                try:
                    return self._complete_gemini(prompt)
                except Exception:
                    provider = "mock"
        # Mock fallback implementation to keep MVP running
        last_err: Optional[Exception] = None
        for _ in range(max(1, cfg.retries + 1)):
            try:
                time.sleep(0.01)
                return prompt[:200] + " ..."
            except Exception as e:  # pragma: no cover (placeholder)
                last_err = e
                time.sleep(0.05)
        raise RuntimeError(f"LLMClient failed: {last_err}")

    def _complete_gemini(self, prompt: str) -> str:
        # Lazy import to avoid hard dependency at import time
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except Exception as e:  # pragma: no cover
            raise RuntimeError("Gemini provider requested but langchain-google-genai not installed") from e

        cfg = self.config
        # Expect GOOGLE_API_KEY in env; langchain client will pick it up
        model = ChatGoogleGenerativeAI(
            model=cfg.model,
            temperature=cfg.temperature,
            max_output_tokens=cfg.max_tokens,
            convert_system_message_to_human=True,
        )
        # Simple single-turn call
        result = model.invoke(prompt)
        # langchain chat model returns a BaseMessage; extract content
        text = getattr(result, "content", None) or str(result)
        return text

    def _complete_ollama(self, prompt: str) -> str:
        try:
            import requests
        except Exception as e:  # pragma: no cover
            raise RuntimeError("Ollama provider requested but requests not installed") from e

        host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
        url = os.getenv("OLLAMA_API_URL", f"{host}/api/generate")
        model = os.getenv("RA9_LLM_MODEL", self.config.model or "llama3:latest")
        payload = {"model": model, "prompt": prompt, "stream": False}
        r = requests.post(url, json=payload, timeout=self.config.timeout_s or 60.0)
        r.raise_for_status()
        data = r.json()
        return data.get("response", "")


def load_llm_config_from_env() -> LLMConfig:
    provider = os.getenv("RA9_LLM_PROVIDER", "gemini").lower()
    model = os.getenv("RA9_LLM_MODEL", "gemini-2.5-flash")
    try:
        temperature = float(os.getenv("RA9_LLM_TEMPERATURE", "0.2"))
    except ValueError:
        temperature = 0.2
    try:
        max_tokens = int(os.getenv("RA9_LLM_MAX_TOKENS", "512"))
    except ValueError:
        max_tokens = 512
    try:
        top_p = float(os.getenv("RA9_LLM_TOP_P", "1.0"))
    except ValueError:
        top_p = 1.0
    try:
        timeout_s = float(os.getenv("RA9_LLM_TIMEOUT_S", "20"))
    except ValueError:
        timeout_s = 20.0
    try:
        retries = int(os.getenv("RA9_LLM_RETRIES", "2"))
    except ValueError:
        retries = 2
    return LLMConfig(
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        timeout_s=timeout_s,
        retries=retries,
    )



import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIClient:
    """Thin wrapper over an OpenAI-compatible /chat/completions endpoint.

    Deliberately depends only on httpx + the wire format, not any provider
    SDK, so swapping AI providers never touches the callers. Every other
    service talks to this class, never to httpx or a provider directly."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        *,
        http_client: httpx.Client | None = None,
        timeout: float = 10.0,
    ):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._client = http_client or httpx.Client(timeout=timeout)

    def generate(self, *, system: str, user: str) -> str | None:
        """Returns the model's reply text, or None on any failure (bad
        response shape, HTTP error, network error, timeout). Callers must
        always have a non-AI fallback ready - AI_AGENT_RULES.md 실패 처리:
        원인은 서버 로그에만 남기고, 실패를 다른 결과로 둔갑시키지 않는다."""
        try:
            response = self._client.post(
                f"{self._base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self._model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            logger.exception("AI provider call failed")
            return None


def get_client() -> AIClient | None:
    """None when the AI provider isn't configured (missing env vars) or
    during local/test runs without one - callers fall back to Mock/template
    answers, they must never break because the AI provider is absent."""
    if not (settings.ai_api_base_url and settings.ai_api_key and settings.ai_model):
        return None
    return AIClient(settings.ai_api_base_url, settings.ai_api_key, settings.ai_model)

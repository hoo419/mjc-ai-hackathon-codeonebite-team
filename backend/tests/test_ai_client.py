import httpx

from app.services.ai_client import AIClient, get_client


def _client_with_transport(handler) -> AIClient:
    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    return AIClient(
        "https://api.example.com/v1", "test-key", "test-model", http_client=http_client
    )


def test_generate_returns_model_reply_on_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer test-key"
        assert request.url == "https://api.example.com/v1/chat/completions"
        return httpx.Response(200, json={"choices": [{"message": {"content": "안녕하세요!"}}]})

    client = _client_with_transport(handler)

    assert client.generate(system="시스템 프롬프트", user="사용자 메시지") == "안녕하세요!"


def test_generate_returns_none_on_http_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "boom"})

    client = _client_with_transport(handler)

    assert client.generate(system="s", user="u") is None


def test_generate_returns_none_on_malformed_response():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": "shape"})

    client = _client_with_transport(handler)

    assert client.generate(system="s", user="u") is None


def test_generate_returns_none_on_network_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client = _client_with_transport(handler)

    assert client.generate(system="s", user="u") is None


def test_get_client_returns_none_when_not_fully_configured(monkeypatch):
    from app.services import ai_client as ai_client_module

    monkeypatch.setattr(ai_client_module.settings, "ai_api_base_url", None)
    monkeypatch.setattr(ai_client_module.settings, "ai_api_key", "key")
    monkeypatch.setattr(ai_client_module.settings, "ai_model", "model")

    assert get_client() is None


def test_get_client_returns_client_when_fully_configured(monkeypatch):
    from app.services import ai_client as ai_client_module

    monkeypatch.setattr(ai_client_module.settings, "ai_api_base_url", "https://api.example.com/v1")
    monkeypatch.setattr(ai_client_module.settings, "ai_api_key", "key")
    monkeypatch.setattr(ai_client_module.settings, "ai_model", "gpt-test")

    assert get_client() is not None

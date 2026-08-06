from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_notices_returns_mock_notices():
    response = client.get("/api/notices")

    assert response.status_code == 200
    notices = response.json()["notices"]
    assert len(notices) >= 3
    first = notices[0]
    assert set(first.keys()) == {"id", "title", "category", "publishedAt", "url"}

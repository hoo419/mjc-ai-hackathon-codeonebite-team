from fastapi.testclient import TestClient

from app.main import app
from app.repositories import notice_repository
from app.schemas.notice import Notice

client = TestClient(app)

_FAKE_NOTICES = [
    Notice(
        id="BD0050388085",
        title="[교양과정] 2026학년도 2학기 군 e-러닝 학점교류 운영 안내",
        category="ACADEMIC",
        publishedAt="2026-08-06T00:00:00+09:00",
        url="https://www.mjc.ac.kr/bbs/data/view.do?menu_idx=169&bbs_mst_idx=BM0000000025&data_idx=BD0050388085",
    ),
]


def test_list_notices_returns_real_shaped_notices(monkeypatch):
    monkeypatch.setattr(notice_repository.mjc_notices, "fetch_recent_notices", lambda limit=4: _FAKE_NOTICES)

    response = client.get("/api/notices")

    assert response.status_code == 200
    notices = response.json()["notices"]
    assert len(notices) == 1
    first = notices[0]
    assert set(first.keys()) == {"id", "title", "category", "publishedAt", "url"}
    assert first["category"] == "ACADEMIC"
    assert first["url"].startswith("https://www.mjc.ac.kr/bbs/data/view.do")


def test_list_notices_returns_empty_list_when_school_site_unreachable(monkeypatch):
    monkeypatch.setattr(notice_repository.mjc_notices, "fetch_recent_notices", lambda limit=4: [])

    response = client.get("/api/notices")

    assert response.status_code == 200
    assert response.json()["notices"] == []

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_counseling_summary_returns_404_when_no_real_summary_exists():
    # 진로적성검사 요약은 학생이 mpu.mjc.ac.kr(SMART CARE)에 직접 로그인해서
    # 확인한 뒤 붙여넣어야만 나오는 데이터라, 아직 아무도 그렇게 한 적 없는
    # mock-student-001은 진짜로 요약이 없다 - data/counseling.json이
    # 비어있으므로 정직하게 404. 프론트는 이 경우 상담센터 연락처를 보여준다.
    response = client.get("/api/counseling/me")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "COUNSELING_SUMMARY_NOT_FOUND"


def test_request_counseling_returns_requested_status():
    response = client.post(
        "/api/counseling/request",
        json={"targetType": "ADVISOR", "message": "진로 상담을 받고 싶습니다."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["status"] == "REQUESTED"
    assert body["requestId"]


def test_request_counseling_generates_unique_request_ids():
    first = client.post(
        "/api/counseling/request",
        json={"targetType": "CAREER_COUNSELOR", "message": "첫 번째 요청"},
    ).json()
    second = client.post(
        "/api/counseling/request",
        json={"targetType": "DEPARTMENT_OFFICE", "message": "두 번째 요청"},
    ).json()

    assert first["requestId"] != second["requestId"]


def test_request_counseling_rejects_invalid_target_type():
    response = client.post(
        "/api/counseling/request",
        json={"targetType": "NOT_A_REAL_TYPE", "message": "..."},
    )

    assert response.status_code == 422


def test_analyze_aptitude_returns_ai_generated_summary_and_insights(monkeypatch):
    import json

    from app.services import counseling_service

    class FakeClient:
        def generate(self, *, system, user):
            assert "학생 A" in user
            return json.dumps(
                {
                    "summary": "학생 A는 문제해결 역량이 높게 나타났습니다.",
                    "insights": ["논리적 사고력이 뛰어남", "협업 역량 보완 필요"],
                }
            )

    monkeypatch.setattr(counseling_service.ai_client, "get_client", lambda: FakeClient())

    response = client.post(
        "/api/counseling/analyze-aptitude",
        json={"rawText": "학생 A 진로적성검사 결과: 문제해결 92점, 협업 61점"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == "학생 A는 문제해결 역량이 높게 나타났습니다."
    assert body["insights"] == ["논리적 사고력이 뛰어남", "협업 역량 보완 필요"]


def test_analyze_aptitude_falls_back_to_raw_text_when_ai_response_is_not_json(monkeypatch):
    from app.services import counseling_service

    class FakeClient:
        def generate(self, *, system, user):
            return "이 학생은 문제해결 역량이 높습니다."

    monkeypatch.setattr(counseling_service.ai_client, "get_client", lambda: FakeClient())

    response = client.post(
        "/api/counseling/analyze-aptitude", json={"rawText": "아무 검사 결과 원문"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == "이 학생은 문제해결 역량이 높습니다."
    assert body["insights"] == []


def test_analyze_aptitude_returns_503_when_ai_unavailable(monkeypatch):
    from app.services import counseling_service

    monkeypatch.setattr(counseling_service.ai_client, "get_client", lambda: None)

    response = client.post(
        "/api/counseling/analyze-aptitude", json={"rawText": "아무 검사 결과 원문"}
    )

    assert response.status_code == 503
    body = response.json()
    assert body["error"]["code"] == "ANALYSIS_UNAVAILABLE"


def test_analyze_aptitude_rejects_empty_raw_text():
    response = client.post("/api/counseling/analyze-aptitude", json={"rawText": "   "})

    assert response.status_code == 503

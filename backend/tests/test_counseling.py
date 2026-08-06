from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_counseling_summary_returns_mock_summary():
    response = client.get("/api/counseling/me")

    assert response.status_code == 200
    assert response.json() == {
        "careerSummary": "소프트웨어 개발 직무에 높은 관심을 보입니다.",
        "personalitySummary": "Mock 데이터입니다.",
        "lastCounselingAt": "2026-07-01T15:00:00+09:00",
    }


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

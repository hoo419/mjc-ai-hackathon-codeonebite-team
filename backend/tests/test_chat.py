from datetime import datetime

from fastapi.testclient import TestClient

from app.core.time import KST
from app.main import app
from app.services import chat_service

client = TestClient(app)

# 2024-01-01 is a known Monday, 2024-01-04 a known Thursday. Using fixed
# reference dates keeps the schedule/next-class tests independent of
# whatever day the suite actually runs on.
A_MONDAY = datetime(2024, 1, 1, 9, 0, tzinfo=KST)
A_THURSDAY_MORNING = datetime(2024, 1, 4, 10, 0, tzinfo=KST)
A_THURSDAY_AFTERNOON = datetime(2024, 1, 4, 16, 0, tzinfo=KST)


def test_chat_finds_available_online_general_elective_courses():
    response = client.post(
        "/api/chat", json={"message": "지금 신청 가능한 온라인 교양 과목 알려줘."}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    course_ids = {c["id"] for c in body["courses"]}
    assert course_ids == {"GE101-01", "GE104-01"}
    assert all(c["status"] == "OPEN" for c in body["courses"])
    assert {a["targetId"] for a in body["actions"]} == course_ids
    assert all(a["type"] == "VIEW_COURSE" for a in body["actions"])


def test_chat_searches_major_required_courses_regardless_of_status():
    response = client.post("/api/chat", json={"message": "전공필수 과목 알려줘"})

    assert response.status_code == 200
    courses = response.json()["courses"]
    assert {c["id"] for c in courses} == {
        "CS301-01",
        "CS301-02",
        "CS210-01",
        "CS350-01",
        "CS360-01",
        "CS370-01",
    }
    assert all(c["category"] == "MAJOR_REQUIRED" for c in courses)


def test_chat_today_schedule_returns_only_todays_courses():
    result = chat_service.handle_message("오늘 수업 뭐 있어?", now=A_THURSDAY_MORNING)

    assert {c.id for c in result.courses} == {"CS301-01"}
    assert "인공지능" in result.answer


def test_chat_today_schedule_on_monday():
    result = chat_service.handle_message("오늘 수업 뭐 있어?", now=A_MONDAY)

    assert {c.id for c in result.courses} == {"GE101-01"}


def test_chat_next_class_before_todays_class():
    result = chat_service.handle_message("다음 수업 뭐야?", now=A_THURSDAY_MORNING)

    assert {c.id for c in result.courses} == {"CS301-01"}


def test_chat_next_class_wraps_to_following_week():
    # After CS301-01 (THU 13:00-15:50) has ended, the next class is
    # GE101-01 the following MON.
    result = chat_service.handle_message("다음 수업 뭐야?", now=A_THURSDAY_AFTERNOON)

    assert {c.id for c in result.courses} == {"GE101-01"}


def test_chat_school_info_question_returns_safe_fallback():
    response = client.post("/api/chat", json={"message": "휴학 신청은 어떻게 해?"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "현재 연결된 데이터에서 확인할 수 없습니다."
    assert body["sources"] == []
    assert body["courses"] == []
    assert body["actions"] == []


def test_chat_endpoint_never_returns_500_on_unexpected_error(monkeypatch):
    def boom(message, now=None):
        raise RuntimeError("ai provider exploded")

    monkeypatch.setattr(chat_service, "handle_message", boom)

    response = client.post("/api/chat", json={"message": "아무 질문"})

    assert response.status_code == 200
    assert response.json()["answer"]

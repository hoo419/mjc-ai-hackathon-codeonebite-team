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


def test_chat_school_info_question_returns_safe_fallback_when_nothing_found(monkeypatch):
    monkeypatch.setattr(chat_service.school_info, "answer", lambda question: None)

    response = client.post("/api/chat", json={"message": "휴학 신청은 어떻게 해?"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "현재 연결된 데이터에서 확인할 수 없습니다."
    assert body["sources"] == []
    assert body["courses"] == []
    assert body["actions"] == []


def test_chat_school_info_returns_rag_answer_when_found(monkeypatch):
    from app.schemas.chat import ChatResponse, ChatSource

    fake_response = ChatResponse(
        answer="공지에 따르면 학기별로 휴학 신청 기간이 다릅니다.",
        sources=[ChatSource(title="휴학 안내", url="https://www.mjc.ac.kr/bbs/data/view.do?data_idx=1")],
    )
    monkeypatch.setattr(chat_service.school_info, "answer", lambda question: fake_response)

    response = client.post("/api/chat", json={"message": "휴학 신청은 어떻게 해?"})

    body = response.json()
    assert body["answer"] == "공지에 따르면 학기별로 휴학 신청 기간이 다릅니다."
    assert body["sources"] == [
        {"title": "휴학 안내", "url": "https://www.mjc.ac.kr/bbs/data/view.do?data_idx=1"}
    ]


def test_chat_endpoint_never_returns_500_on_unexpected_error(monkeypatch):
    def boom(message, now=None):
        raise RuntimeError("ai provider exploded")

    monkeypatch.setattr(chat_service, "handle_message", boom)

    response = client.post("/api/chat", json={"message": "아무 질문"})

    assert response.status_code == 200
    assert response.json()["answer"]


class _FakeAIClient:
    def __init__(self, reply: str | None):
        self._reply = reply

    def generate(self, *, system: str, user: str) -> str | None:
        return self._reply


def test_chat_uses_ai_rephrased_answer_when_ai_client_available(monkeypatch):
    monkeypatch.setattr(
        chat_service.ai_client, "get_client", lambda: _FakeAIClient("다듬어진 답변입니다.")
    )

    result = chat_service.handle_message("전공필수 과목 알려줘")

    assert result.answer == "다듬어진 답변입니다."
    # Facts (which/how many courses) are untouched by the AI rephrase step.
    assert len(result.courses) == 6


def test_chat_falls_back_to_template_answer_when_ai_client_fails(monkeypatch):
    monkeypatch.setattr(chat_service.ai_client, "get_client", lambda: _FakeAIClient(None))

    result = chat_service.handle_message("전공필수 과목 알려줘")

    assert result.answer == "조건에 맞는 과목을 6건 찾았습니다."


def test_chat_school_info_fallback_is_never_rephrased_by_ai(monkeypatch):
    monkeypatch.setattr(chat_service.school_info, "answer", lambda question: None)
    monkeypatch.setattr(
        chat_service.ai_client, "get_client", lambda: _FakeAIClient("이렇게 저렇게 도와드릴게요.")
    )

    result = chat_service.handle_message("휴학 신청은 어떻게 해?")

    assert result.answer == "현재 연결된 데이터에서 확인할 수 없습니다."

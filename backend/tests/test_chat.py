from datetime import datetime

from fastapi.testclient import TestClient

from app.core.time import KST
from app.main import app
from app.services import chat_service

client = TestClient(app)

# 2024-01-01이 월요일이라는 가정 하에, 2024-01-02는 화요일, 2024-01-05는
# 금요일 (date +%A 등으로 실제 확인 완료). 고정 기준 날짜를 쓰면 테스트가
# 실행되는 요일과 무관하게 동작한다.
A_TUESDAY_MORNING = datetime(2024, 1, 2, 9, 0, tzinfo=KST)  # 2024-01-02는 화요일
A_FRIDAY_MORNING = datetime(2024, 1, 5, 9, 0, tzinfo=KST)  # 2024-01-05는 금요일
A_FRIDAY_AFTERNOON = datetime(2024, 1, 5, 12, 0, tzinfo=KST)


def test_chat_finds_available_online_general_courses():
    response = client.post(
        "/api/chat", json={"message": "지금 신청 가능한 온라인 교양 과목 알려줘."}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    assert len(body["courses"]) >= 1
    assert all(c["classType"] is None for c in body["courses"])
    assert all(
        c["category"] in {"GENERAL_COURSE", "GENERAL_REQUIRED", "GENERAL_ELECTIVE"}
        for c in body["courses"]
    )
    assert all(c["status"] == "OPEN" for c in body["courses"])
    assert {a["targetId"] for a in body["actions"]} == {c["id"] for c in body["courses"]}
    assert all(a["type"] == "VIEW_COURSE" for a in body["actions"])


def test_chat_searches_major_courses_regardless_of_status():
    response = client.post("/api/chat", json={"message": "전공 과목 알려줘"})

    assert response.status_code == 200
    courses = response.json()["courses"]
    assert len(courses) >= 1
    assert all(c["category"] == "MAJOR_COURSE" for c in courses)


def test_chat_today_schedule_returns_only_todays_courses():
    result = chat_service.handle_message("오늘 수업 뭐 있어?", now=A_FRIDAY_MORNING)

    assert {c.id for c in result.courses} == {"T00138-101"}
    assert "AI활용웹개발" in result.answer


def test_chat_today_schedule_on_tuesday():
    result = chat_service.handle_message("오늘 수업 뭐 있어?", now=A_TUESDAY_MORNING)

    assert {c.id for c in result.courses} == {"J01683-101"}


def test_chat_next_class_before_todays_class():
    result = chat_service.handle_message("다음 수업 뭐야?", now=A_FRIDAY_MORNING)

    assert {c.id for c in result.courses} == {"T00138-101"}


def test_chat_next_class_wraps_to_following_week():
    # FRI 11:00-11:50(T00138-101)이 끝난 뒤엔 다음 주 TUE 09:25(J01683-101)가 다음 수업.
    result = chat_service.handle_message("다음 수업 뭐야?", now=A_FRIDAY_AFTERNOON)

    assert {c.id for c in result.courses} == {"J01683-101"}


def test_chat_school_info_question_returns_safe_fallback_when_nothing_found(monkeypatch):
    monkeypatch.setattr(chat_service.school_info, "answer", lambda question, now=None: None)

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
    monkeypatch.setattr(chat_service.school_info, "answer", lambda question, now=None: fake_response)

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

    result = chat_service.handle_message("전공 과목 알려줘")

    assert result.answer == "다듬어진 답변입니다."
    # Facts (which/how many courses) are untouched by the AI rephrase step.
    assert len(result.courses) == 35


def test_chat_falls_back_to_template_answer_when_ai_client_fails(monkeypatch):
    monkeypatch.setattr(chat_service.ai_client, "get_client", lambda: _FakeAIClient(None))

    result = chat_service.handle_message("전공 과목 알려줘")

    assert result.answer == "조건에 맞는 과목을 35건 찾았습니다."


def test_chat_school_info_fallback_is_never_rephrased_by_ai(monkeypatch):
    monkeypatch.setattr(chat_service.school_info, "answer", lambda question, now=None: None)
    monkeypatch.setattr(
        chat_service.ai_client, "get_client", lambda: _FakeAIClient("이렇게 저렇게 도와드릴게요.")
    )

    result = chat_service.handle_message("휴학 신청은 어떻게 해?")

    assert result.answer == "현재 연결된 데이터에서 확인할 수 없습니다."

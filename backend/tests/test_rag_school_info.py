from app.rag import school_info
from app.rag.mjc_detail import NoticeDetail
from app.schemas.chat import ChatSource


def _fake_detail(n: int) -> NoticeDetail:
    return NoticeDetail(
        title=f"공지 {n}",
        body=f"공지 {n}의 본문 내용입니다.",
        published_at=f"2026-01-0{n}",
        url=f"https://www.mjc.ac.kr/bbs/data/view.do?data_idx={n}",
    )


def test_answer_returns_none_when_no_search_results(monkeypatch):
    monkeypatch.setattr(school_info.mjc_search, "search_school_site", lambda q: [])

    assert school_info.answer("아무 질문") is None


def test_answer_returns_none_when_all_candidates_fail_to_parse(monkeypatch):
    monkeypatch.setattr(school_info.mjc_search, "search_school_site", lambda q: ["u1", "u2"])
    monkeypatch.setattr(school_info.mjc_detail, "fetch_detail", lambda url: None)

    assert school_info.answer("아무 질문") is None


def test_answer_stops_after_three_successful_documents(monkeypatch):
    urls = [f"u{i}" for i in range(5)]
    monkeypatch.setattr(school_info.mjc_search, "search_school_site", lambda q: urls)

    calls = []

    def fake_fetch(url):
        calls.append(url)
        return _fake_detail(len(calls))

    monkeypatch.setattr(school_info.mjc_detail, "fetch_detail", fake_fetch)
    monkeypatch.setattr(school_info.ai_client, "get_client", lambda: None)

    result = school_info.answer("질문")

    assert len(calls) == 3
    assert result is not None
    assert len(result.sources) == 3


def test_answer_uses_template_when_ai_client_unavailable(monkeypatch):
    monkeypatch.setattr(school_info.mjc_search, "search_school_site", lambda q: ["u1"])
    monkeypatch.setattr(school_info.mjc_detail, "fetch_detail", lambda url: _fake_detail(1))
    monkeypatch.setattr(school_info.ai_client, "get_client", lambda: None)

    result = school_info.answer("질문")

    assert result is not None
    assert "공지 1" in result.answer
    assert result.sources == [
        ChatSource(title="공지 1", url="https://www.mjc.ac.kr/bbs/data/view.do?data_idx=1")
    ]


def test_answer_uses_ai_generated_text_when_available(monkeypatch):
    monkeypatch.setattr(school_info.mjc_search, "search_school_site", lambda q: ["u1"])
    monkeypatch.setattr(school_info.mjc_detail, "fetch_detail", lambda url: _fake_detail(1))

    class FakeClient:
        def generate(self, *, system, user):
            assert "공지 1" in user
            return "AI가 다듬은 답변입니다."

    monkeypatch.setattr(school_info.ai_client, "get_client", lambda: FakeClient())

    result = school_info.answer("질문")

    assert result.answer == "AI가 다듬은 답변입니다."


def test_answer_falls_back_to_template_when_ai_generate_returns_none(monkeypatch):
    monkeypatch.setattr(school_info.mjc_search, "search_school_site", lambda q: ["u1"])
    monkeypatch.setattr(school_info.mjc_detail, "fetch_detail", lambda url: _fake_detail(1))

    class FailingClient:
        def generate(self, *, system, user):
            return None

    monkeypatch.setattr(school_info.ai_client, "get_client", lambda: FailingClient())

    result = school_info.answer("질문")

    assert "공지 1" in result.answer

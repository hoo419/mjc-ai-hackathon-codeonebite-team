from datetime import datetime

from app.core.time import KST
from app.rag import school_info
from app.rag.mjc_detail import NoticeDetail
from app.schemas.chat import ChatSource

NOW_2026 = datetime(2026, 8, 6, tzinfo=KST)


def _fake_detail(n: int, date: str = "2026-01-01") -> NoticeDetail:
    return NoticeDetail(
        title=f"공지 {n}",
        body=f"공지 {n}의 본문 내용입니다.",
        published_at=date,
        url=f"https://www.mjc.ac.kr/bbs/data/view.do?data_idx={n}",
    )


def test_clean_query_strips_trailing_particles_and_request_phrases():
    assert school_info._clean_query("분납신청에대해") == "분납신청"
    assert school_info._clean_query("분납신청에 대해") == "분납신청"
    assert school_info._clean_query("분납신청 알려줘") == "분납신청"
    assert school_info._clean_query("분납신청 어떻게 해") == "분납신청"


def test_clean_query_falls_back_to_original_message_if_nothing_left():
    assert school_info._clean_query("어떻게 해") == "어떻게 해"


def test_answer_cleans_conversational_suffixes_before_searching(monkeypatch):
    captured = {}

    def fake_search(query):
        captured["query"] = query
        return []

    monkeypatch.setattr(school_info.mjc_search, "search_school_site", fake_search)

    school_info.answer("분납신청에대해 알려줘")

    assert captured["query"] == "분납신청"


def test_answer_returns_none_when_no_search_results(monkeypatch):
    monkeypatch.setattr(school_info.mjc_search, "search_school_site", lambda q: [])

    assert school_info.answer("아무 질문") is None


def test_answer_returns_none_when_all_candidates_fail_to_parse(monkeypatch):
    monkeypatch.setattr(school_info.mjc_search, "search_school_site", lambda q: ["u1", "u2"])
    monkeypatch.setattr(school_info.mjc_detail, "fetch_detail", lambda url: None)

    assert school_info.answer("아무 질문") is None


def test_answer_recommends_link_when_no_document_has_extractable_body(monkeypatch):
    """검색은 됐고 게시글도 존재하지만(예: HWP 첨부라 본문 텍스트를 못
    뽑는 경우) 본문 요약 대신 최소한 링크는 추천해준다 - 아예 못 찾았다고
    하지 않는다."""
    monkeypatch.setattr(school_info.mjc_search, "search_school_site", lambda q: ["u1"])
    link_only = NoticeDetail(
        title="첨부파일 공지",
        body="",
        published_at="2026-05-20",
        url="https://www.mjc.ac.kr/bbs/data/view.do?data_idx=9",
    )
    monkeypatch.setattr(school_info.mjc_detail, "fetch_detail", lambda url: link_only)

    result = school_info.answer("질문")

    assert result is not None
    assert "첨부파일 공지" in result.answer
    assert result.sources == [
        ChatSource(title="첨부파일 공지", url="https://www.mjc.ac.kr/bbs/data/view.do?data_idx=9")
    ]


def test_answer_picks_the_most_recently_published_document(monkeypatch):
    monkeypatch.setattr(school_info.mjc_search, "search_school_site", lambda q: ["u1", "u2", "u3"])

    fakes = {
        "u1": _fake_detail(1, "2025-01-01"),
        "u2": _fake_detail(2, "2026-03-15"),  # latest
        "u3": _fake_detail(3, "2024-06-01"),
    }
    monkeypatch.setattr(school_info.mjc_detail, "fetch_detail", lambda url: fakes[url])
    monkeypatch.setattr(school_info.ai_client, "get_client", lambda: None)

    result = school_info.answer("질문")

    assert result is not None
    assert result.sources == [
        ChatSource(title="공지 2", url="https://www.mjc.ac.kr/bbs/data/view.do?data_idx=2")
    ]
    assert "공지 2" in result.answer


def test_current_term_maps_month_to_semester():
    # 3~8월 = 1학기, 9~12월 = 2학기, 1~2월 = 전년도 2학기
    assert school_info._current_term(datetime(2026, 8, 6, tzinfo=KST)) == (2026, 1)
    assert school_info._current_term(datetime(2026, 3, 1, tzinfo=KST)) == (2026, 1)
    assert school_info._current_term(datetime(2026, 9, 1, tzinfo=KST)) == (2026, 2)
    assert school_info._current_term(datetime(2026, 12, 31, tzinfo=KST)) == (2026, 2)
    assert school_info._current_term(datetime(2026, 1, 15, tzinfo=KST)) == (2025, 2)


def test_extract_term_from_title_parses_explicit_academic_term():
    assert school_info._extract_term_from_title("2025학년도 2학기 분할납부일정 안내") == (2025, 2)
    assert school_info._extract_term_from_title("2026학년도 1학기 수강신청 안내") == (2026, 1)
    assert school_info._extract_term_from_title("보건실 하계방학 운영시간 안내") is None


def test_is_stale_uses_title_term_when_present():
    # 지금은 2026학년도 1학기. 제목이 그보다 과거 학기면 stale.
    old = _fake_detail(1, date="2025-08-11")
    old.title = "2025학년도 2학기 분할납부일정 안내"
    assert school_info._is_stale(old, NOW_2026) is True

    # 제목이 미래(다음) 학기를 가리키면 - 다가올 학기 사전 안내이므로 stale 아님
    upcoming = _fake_detail(1, date="2026-07-01")
    upcoming.title = "2026학년도 2학기 수강신청 안내"
    assert school_info._is_stale(upcoming, NOW_2026) is False

    # 제목이 지금 학기와 같으면 stale 아님
    current = _fake_detail(1, date="2026-04-01")
    current.title = "2026학년도 1학기 중간고사 안내"
    assert school_info._is_stale(current, NOW_2026) is False


def test_is_stale_falls_back_to_posting_year_when_title_has_no_term():
    old_no_term = _fake_detail(1, date="2025-08-11")  # title = "공지 1", 학기 표기 없음
    assert school_info._is_stale(old_no_term, NOW_2026) is True

    current_no_term = _fake_detail(1, date="2026-07-01")
    assert school_info._is_stale(current_no_term, NOW_2026) is False


def test_answer_flags_outdated_document_instead_of_presenting_it_as_current(monkeypatch):
    """작년(또는 이전 학기) 자료가 검색된 최선의 결과라면, 마치 최신인 것처럼
    답하지 않고 "지금 학기 자료는 아직 안 올라왔다 + 실제 게시연도와 그
    공지가 다루는 학년도/학기가 다를 수 있다"를 구분해서 정직하게 알려준다
    - 이 판단은 LLM이 아니라 코드가 실제 현재 날짜/학기와 비교해서 한다."""
    monkeypatch.setattr(school_info.mjc_search, "search_school_site", lambda q: ["u1"])
    old_doc = _fake_detail(1, date="2025-08-11")
    old_doc.title = "2025학년도 2학기 분할납부일정 안내"
    monkeypatch.setattr(school_info.mjc_detail, "fetch_detail", lambda url: old_doc)

    result = school_info.answer("분납신청", now=NOW_2026)

    assert result is not None
    assert "2026년도 1학기" in result.answer  # 지금 학기 - 아직 못 찾았다는 기준
    assert "2025년도에 올라온" in result.answer  # 실제 게시연도
    assert "2025년도 2학기" in result.answer  # 그 공지가 다루는 학년도/학기
    assert "분할납부일정" in result.answer
    assert result.sources == [
        ChatSource(
            title="2025학년도 2학기 분할납부일정 안내",
            url="https://www.mjc.ac.kr/bbs/data/view.do?data_idx=1",
        )
    ]


def test_answer_flags_outdated_document_even_when_body_could_not_be_extracted(monkeypatch):
    monkeypatch.setattr(school_info.mjc_search, "search_school_site", lambda q: ["u1"])
    old_link_only = NoticeDetail(
        title="2025학년도 2학기 분할납부일정 안내",
        body="",
        published_at="2025-08-11",
        url="https://www.mjc.ac.kr/bbs/data/view.do?data_idx=9",
    )
    monkeypatch.setattr(school_info.mjc_detail, "fetch_detail", lambda url: old_link_only)

    result = school_info.answer("분납신청", now=NOW_2026)

    assert result is not None
    assert "2026년도 1학기" in result.answer
    assert "2025년도에 올라온" in result.answer
    assert "2025년도 2학기" in result.answer
    assert "분할납부일정" in result.answer


def test_answer_flags_outdated_document_without_title_term_using_posting_year_only(monkeypatch):
    """제목에 '학년도 N학기' 표기가 없으면 게시연도만으로 근사 판단하고,
    문구도 그에 맞게 학기 정보 없이 표현한다."""
    monkeypatch.setattr(school_info.mjc_search, "search_school_site", lambda q: ["u1"])
    old_doc = _fake_detail(1, date="2025-08-11")  # title = "공지 1", 학기 표기 없음
    monkeypatch.setattr(school_info.mjc_detail, "fetch_detail", lambda url: old_doc)

    result = school_info.answer("질문", now=NOW_2026)

    assert result is not None
    assert "2026년도 1학기" in result.answer
    assert "공지 1" in result.answer


def test_answer_does_not_flag_upcoming_semester_notice_as_outdated(monkeypatch):
    monkeypatch.setattr(school_info.mjc_search, "search_school_site", lambda q: ["u1"])
    upcoming_doc = _fake_detail(1, date="2026-07-01")
    upcoming_doc.title = "2026학년도 2학기 수강신청 안내"
    monkeypatch.setattr(school_info.mjc_detail, "fetch_detail", lambda url: upcoming_doc)
    monkeypatch.setattr(school_info.ai_client, "get_client", lambda: None)

    result = school_info.answer("질문", now=NOW_2026)

    assert "찾지 못했습니다" not in result.answer
    assert "2026학년도 2학기 수강신청 안내" in result.answer


def test_answer_prefers_title_matching_query_over_more_recent_unrelated_document(monkeypatch):
    """학교 통합검색이 항상 관련도 순은 아니라서, 검색어와 무관한 최신
    글보다 제목에 검색어가 실제로 들어간 문서를 우선한다."""
    monkeypatch.setattr(school_info.mjc_search, "search_school_site", lambda q: ["u1", "u2"])

    on_topic = _fake_detail(1, date="2025-08-01")
    on_topic.title = "2025학년도 2학기 분납신청 안내"
    off_topic_but_newer = _fake_detail(2, date="2026-07-01")
    off_topic_but_newer.title = "2026학년도 1학기 휴학 신청 안내"

    fakes = {"u1": on_topic, "u2": off_topic_but_newer}
    monkeypatch.setattr(school_info.mjc_detail, "fetch_detail", lambda url: fakes[url])
    monkeypatch.setattr(school_info.ai_client, "get_client", lambda: None)

    result = school_info.answer("분납신청", now=NOW_2026)

    assert result.sources == [
        ChatSource(
            title="2025학년도 2학기 분납신청 안내",
            url="https://www.mjc.ac.kr/bbs/data/view.do?data_idx=1",
        )
    ]


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

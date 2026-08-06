from pathlib import Path

import httpx

from app.rag.mjc_notices import NoticeRow, fetch_recent_notices, parse_notice_list_html, select_recent

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_notice_list_html_extracts_every_row_pinned_and_regular():
    html = (FIXTURES / "mjc_notice_list.html").read_text(encoding="utf-8")

    rows = parse_notice_list_html(html)

    assert rows == [
        NoticeRow(
            title="[교양과정] 2026학년도 2학기 교양과정 시간표 안내",
            bbs_mst_idx="BM0000000025",
            data_idx="BD0050388084",
            date="2026-08-04",
        ),
        NoticeRow(
            title="국가장학금 전액우선감면(고지서 0원)대상자 등록처리 안내",
            bbs_mst_idx="BM0000000025",
            data_idx="BD0050388082",
            date="2026-08-03",
        ),
        NoticeRow(
            title="[교양과정] 2026학년도 2학기 군 e-러닝 학점교류 운영 안내",
            bbs_mst_idx="BM0000000025",
            data_idx="BD0050388085",
            date="2026-08-06",
        ),
        NoticeRow(
            title="[전공심화] 2026학년도 2학기 재(복)학생 수강신청 안내",
            bbs_mst_idx="BM0000000025",
            data_idx="BD0050388077",
            date="2026-08-02",
        ),
        NoticeRow(
            title="[전과] 2026학년도 2학기 전과 시행 안내",
            bbs_mst_idx="BM0000000025",
            data_idx="BD0050388068",
            date="2026-08-01",
        ),
    ]


def test_parse_notice_list_html_returns_empty_list_when_no_rows_match():
    assert parse_notice_list_html("<html><body>no table here</body></html>") == []


def test_select_recent_sorts_by_date_descending_and_limits():
    html = (FIXTURES / "mjc_notice_list.html").read_text(encoding="utf-8")
    rows = parse_notice_list_html(html)

    top = select_recent(rows, limit=4)

    assert [r.data_idx for r in top] == ["BD0050388085", "BD0050388084", "BD0050388082", "BD0050388077"]
    assert [r.date for r in top] == ["2026-08-06", "2026-08-04", "2026-08-03", "2026-08-02"]


def test_select_recent_keeps_document_order_among_same_date_rows():
    rows = [
        NoticeRow(title="A", bbs_mst_idx="B", data_idx="1", date="2026-08-03"),
        NoticeRow(title="B", bbs_mst_idx="B", data_idx="2", date="2026-08-03"),
    ]

    top = select_recent(rows, limit=2)

    assert [r.data_idx for r in top] == ["1", "2"]


def test_fetch_recent_notices_returns_real_shaped_notice_objects():
    html = (FIXTURES / "mjc_notice_list.html").read_text(encoding="utf-8")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=html)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    notices = fetch_recent_notices(limit=4, http_client=client)

    assert len(notices) == 4
    first = notices[0]
    assert first.id == "BD0050388085"
    assert first.title == "[교양과정] 2026학년도 2학기 군 e-러닝 학점교류 운영 안내"
    assert first.category == "ACADEMIC"
    assert first.publishedAt == "2026-08-06T00:00:00+09:00"
    assert first.url == (
        "https://www.mjc.ac.kr/bbs/data/view.do?menu_idx=169"
        "&bbs_mst_idx=BM0000000025&data_idx=BD0050388085"
    )


def test_fetch_recent_notices_returns_empty_list_on_http_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    assert fetch_recent_notices(http_client=client) == []


def test_fetch_recent_notices_returns_empty_list_on_network_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom", request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    assert fetch_recent_notices(http_client=client) == []


def test_fetch_recent_notices_warns_when_page_parses_to_zero_rows(caplog):
    # 200 OK인데 0행이면 "공지 없음"이 아니라 셀렉터가 깨졌을 가능성이 높다 -
    # 조용히 넘어가지 않고 로그로 남겨야 한다.
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<html><body>no matching rows</body></html>")

    client = httpx.Client(transport=httpx.MockTransport(handler))

    with caplog.at_level("WARNING"):
        notices = fetch_recent_notices(http_client=client)

    assert notices == []
    assert any("0 rows" in record.message for record in caplog.records)


def test_fetch_recent_notices_replaces_truncated_list_title_with_full_detail_title():
    # 제목 뒤쪽이 "..."로 잘려 나오는 글이 실제로 있다(목록 페이지 자체가
    # 긴 제목을 잘라서 보여줌 - 검증 중 실사이트에서 발견). 상세페이지에서
    # 진짜 제목을 가져와 덮어써야 한다.
    list_html = (FIXTURES / "mjc_notice_list.html").read_text(encoding="utf-8")
    detail_html = (FIXTURES / "mjc_detail_plain.html").read_text(encoding="utf-8")

    def handler(request: httpx.Request) -> httpx.Response:
        if "list.do" in str(request.url):
            return httpx.Response(200, text=list_html)
        return httpx.Response(200, text=detail_html)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    notices = fetch_recent_notices(limit=1, http_client=client)

    assert len(notices) == 1
    # mjc_detail_plain.html 픽스처의 실제 제목으로 교체됐는지 확인 (목록의
    # "[교양과정] 2026학년도 2학기 군 e-러닝 학점교류 운영 안내"가 아니어야 함).
    from app.rag.mjc_detail import parse_detail_html

    expected_title = parse_detail_html(detail_html, "https://example.invalid").title
    assert notices[0].title == expected_title


def test_fetch_recent_notices_keeps_list_title_when_detail_fetch_fails():
    list_html = (FIXTURES / "mjc_notice_list.html").read_text(encoding="utf-8")

    def handler(request: httpx.Request) -> httpx.Response:
        if "list.do" in str(request.url):
            return httpx.Response(200, text=list_html)
        return httpx.Response(500)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    notices = fetch_recent_notices(limit=1, http_client=client)

    assert len(notices) == 1
    assert notices[0].title == "[교양과정] 2026학년도 2학기 군 e-러닝 학점교류 운영 안내"

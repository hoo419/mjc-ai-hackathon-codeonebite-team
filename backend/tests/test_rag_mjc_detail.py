from pathlib import Path

import httpx

from app.rag.mjc_detail import fetch_detail, parse_detail_html

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_URL = (
    "https://www.mjc.ac.kr/bbs/data/view.do"
    "?menu_idx=66&bbs_mst_idx=BM0000000026&data_idx=BD0050390024"
)


def test_parse_detail_html_extracts_title_date_and_body_for_plain_html_post():
    html = (FIXTURES / "mjc_detail_plain.html").read_text(encoding="utf-8")

    detail = parse_detail_html(html, url=SAMPLE_URL)

    assert detail is not None
    assert detail.title == "2026학년도 보건실 하계방학 운영시간 안내"
    assert detail.published_at == "2026-06-15"
    assert "보건실" in detail.body
    assert "운영 기간" in detail.body
    assert detail.url == SAMPLE_URL


def test_parse_detail_html_returns_none_for_hwp_embedded_post():
    html = (FIXTURES / "mjc_detail_hwp.html").read_text(encoding="utf-8")

    detail = parse_detail_html(html, url="https://example.com/hwp-post")

    assert detail is None


def test_parse_detail_html_returns_none_when_no_title_found():
    detail = parse_detail_html(
        "<html><body>no board view here</body></html>", url="https://example.com"
    )

    assert detail is None


def test_fetch_detail_returns_parsed_detail_on_success():
    html = (FIXTURES / "mjc_detail_plain.html").read_text(encoding="utf-8")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=html)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    detail = fetch_detail(SAMPLE_URL, http_client=client)

    assert detail is not None
    assert detail.title == "2026학년도 보건실 하계방학 운영시간 안내"


def test_fetch_detail_returns_none_on_http_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    assert fetch_detail(SAMPLE_URL, http_client=client) is None


def test_fetch_detail_returns_none_on_network_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom", request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    assert fetch_detail(SAMPLE_URL, http_client=client) is None

from pathlib import Path

import httpx

from app.rag.mjc_search import _extract_result_urls, search_school_site

FIXTURES = Path(__file__).parent / "fixtures"


def test_extract_result_urls_finds_unique_urls_in_first_appearance_order():
    html = (FIXTURES / "mjc_search_results.html").read_text(encoding="utf-8")

    urls = _extract_result_urls(html)

    assert urls == [
        "http://www.mjc.ac.kr/bbs/data/view.do?menu_idx=66&bbs_mst_idx=BM0000000026&data_idx=BD0050389913",
        "http://www.mjc.ac.kr/bbs/data/view.do?menu_idx=66&bbs_mst_idx=BM0000000026&data_idx=BD0050389879",
        "http://www.mjc.ac.kr/bbs/data/view.do?menu_idx=66&bbs_mst_idx=BM0000000026&data_idx=BD0050389872",
    ]


def test_extract_result_urls_returns_empty_list_when_no_matches():
    assert _extract_result_urls("<html><body>no results</body></html>") == []


def test_search_school_site_sends_euc_kr_encoded_query():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = request.content
        captured["content_type"] = request.headers["content-type"]
        html = (FIXTURES / "mjc_search_results.html").read_text(encoding="utf-8")
        return httpx.Response(200, text=html)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    urls = search_school_site("수강신청", http_client=client)

    assert captured["body"] == b"qt=%BC%F6%B0%AD%BD%C5%C3%BB"
    assert "EUC-KR" in captured["content_type"]
    assert len(urls) == 3


def test_search_school_site_returns_empty_list_on_http_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    assert search_school_site("아무거나", http_client=client) == []


def test_search_school_site_returns_empty_list_on_network_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom", request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    assert search_school_site("아무거나", http_client=client) == []

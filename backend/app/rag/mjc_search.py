import logging
import re
import urllib.parse

import httpx

logger = logging.getLogger(__name__)

SEARCH_URL = "https://www.mjc.ac.kr/RSA/front_new/Search.jsp"
USER_AGENT = "MJC-AI-Campus-Agent/1.0 (school-info RAG)"

_RESULT_URL_RE = re.compile(r"https?://www\.mjc\.ac\.kr/bbs/data/view\.do\?[^\"'\s]+")


def _extract_result_urls(html: str) -> list[str]:
    """Pure function. Pulls every notice-detail URL out of a unified-search
    results page, in first-appearance order, without duplicates. The
    search also covers other sub-sites (department pages, English/Japanese/
    Chinese sites, ...) that use different page structures we haven't
    validated, so only this one URL shape is picked up."""
    seen: set[str] = set()
    urls: list[str] = []
    for match in _RESULT_URL_RE.finditer(html):
        url = match.group(0)
        if url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def search_school_site(query: str, *, http_client: httpx.Client | None = None) -> list[str]:
    """Queries the school's own site search. Any failure (network error,
    HTTP error) returns an empty list - the caller falls back to
    NO_DATA_ANSWER, never fabricates a school-policy answer.

    Confirmed by hand: the search backend expects the query EUC-KR encoded
    even though its own response page is plain UTF-8 - sending the query as
    UTF-8 silently returns zero results instead of erroring."""
    client = http_client or httpx.Client(timeout=5.0, headers={"User-Agent": USER_AGENT})
    try:
        encoded_query = urllib.parse.quote(query.encode("euc-kr", errors="ignore"))
        response = client.post(
            SEARCH_URL,
            content=f"qt={encoded_query}".encode("ascii"),
            headers={"Content-Type": "application/x-www-form-urlencoded; charset=EUC-KR"},
        )
        response.raise_for_status()
        return _extract_result_urls(response.text)
    except Exception:
        logger.exception("school site search failed for query=%r", query)
        return []

import logging
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENT = "MJC-AI-Campus-Agent/1.0 (school-info RAG)"


@dataclass
class NoticeDetail:
    title: str
    body: str
    published_at: str | None
    url: str


def _extract_published_at(soup: BeautifulSoup) -> str | None:
    for th in soup.find_all("th"):
        if th.get_text(strip=True) == "날짜":
            td = th.find_next_sibling("td")
            if td:
                return td.get_text(strip=True)
    return None


def parse_detail_html(html: str, url: str) -> NoticeDetail | None:
    """Extracts (title, body, date) from a mjc.ac.kr bbs/data/view.do page.

    Returns None only when there's no title at all (an unexpected/broken
    page). If the body was authored as an embedded HWP document
    (`.hwp_editor_board_content`) instead of plain HTML (`#divMemo`), there
    is no supported way to pull clean text out of that proprietary JSON
    format - but the page is real and its title/url are still worth
    surfacing as a link recommendation, so this still returns a
    NoticeDetail with `body=""` rather than discarding it entirely."""
    soup = BeautifulSoup(html, "html.parser")

    title_el = soup.select_one(".board_view h2.tit")
    title = title_el.get_text(strip=True) if title_el else ""
    if not title:
        return None

    published_at = _extract_published_at(soup)

    if soup.select_one(".hwp_editor_board_content"):
        # Even when #divMemo also exists here, real examples show it filled
        # with U+FFFD replacement characters - the school's own HWP-to-text
        # conversion failing silently. Presence of the HWP embed itself is
        # the reliable signal, not whether #divMemo looks empty.
        return NoticeDetail(title=title, body="", published_at=published_at, url=url)

    body_el = soup.select_one("#divMemo")
    body = body_el.get_text("\n", strip=True) if body_el else ""

    return NoticeDetail(title=title, body=body, published_at=published_at, url=url)


def fetch_detail(url: str, *, http_client: httpx.Client | None = None) -> NoticeDetail | None:
    """Network fetch + parse. Any failure (timeout, HTTP error, parse
    failure) returns None - callers just skip that candidate and move on,
    never crashing the chat request over one bad page."""
    client = http_client or httpx.Client(timeout=5.0, headers={"User-Agent": USER_AGENT})
    try:
        response = client.get(url)
        response.raise_for_status()
        return parse_detail_html(response.text, url)
    except Exception:
        logger.exception("failed to fetch/parse notice detail: %s", url)
        return None

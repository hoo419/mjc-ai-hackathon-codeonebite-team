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


def parse_detail_html(html: str, url: str) -> NoticeDetail | None:
    """Extracts (title, body, date) from a mjc.ac.kr bbs/data/view.do page.

    Returns None if there's no title, or if the body was authored as an
    embedded HWP document (`.hwp_editor_board_content`) instead of plain
    HTML (`#divMemo`). There's no supported way to pull clean text out of
    that proprietary JSON format, and feeding its raw contents to the chat
    answer would be worse than finding nothing (AI_AGENT_RULES.md - never
    let unreliable data pass as fact)."""
    soup = BeautifulSoup(html, "html.parser")

    title_el = soup.select_one(".board_view h2.tit")
    title = title_el.get_text(strip=True) if title_el else ""
    if not title:
        return None

    if soup.select_one(".hwp_editor_board_content"):
        # Even when #divMemo also exists here, real examples show it filled
        # with U+FFFD replacement characters - the school's own HWP-to-text
        # conversion failing silently. Presence of the HWP embed itself is
        # the reliable signal, not whether #divMemo looks empty.
        return None

    body_el = soup.select_one("#divMemo")
    body = body_el.get_text("\n", strip=True) if body_el else ""
    if not body:
        return None

    published_at = None
    for th in soup.find_all("th"):
        if th.get_text(strip=True) == "날짜":
            td = th.find_next_sibling("td")
            if td:
                published_at = td.get_text(strip=True)
            break

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

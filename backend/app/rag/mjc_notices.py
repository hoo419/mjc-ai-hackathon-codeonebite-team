import logging
import re
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

from app.rag import mjc_detail
from app.schemas.notice import Notice

logger = logging.getLogger(__name__)

USER_AGENT = "MJC-AI-Campus-Agent/1.0 (school-info RAG)"

# 학사공지 게시판 (메뉴 idx 169로 확인됨).
LIST_URL = "https://www.mjc.ac.kr/bbs/data/list.do?menu_idx=169"
DETAIL_BASE_URL = "https://www.mjc.ac.kr/bbs/data/view.do"

_FN_VIEW_RE = re.compile(r"fn_view\('([^']+)','([^']+)'")
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


@dataclass
class NoticeRow:
    title: str
    bbs_mst_idx: str
    data_idx: str
    date: str  # "YYYY-MM-DD"


def parse_notice_list_html(html: str) -> list[NoticeRow]:
    """Pure function. 게시판 목록 페이지에서 상단 고정("공지") 글과 일반 번호글을
    가리지 않고 전부 뽑는다 - 실제로 "최신"인지는 select_recent()가 날짜로
    다시 정렬해서 판단한다 (고정글이 항상 최신은 아니므로)."""
    soup = BeautifulSoup(html, "html.parser")
    rows: list[NoticeRow] = []
    for tr in soup.find_all("tr"):
        link = tr.select_one("td.cell_type01 a")
        if link is None:
            continue
        href = link.get("href", "")
        match = _FN_VIEW_RE.search(href)
        title = link.get_text(strip=True)
        date_match = _DATE_RE.search(tr.get_text())
        if not match or not title or not date_match:
            continue
        rows.append(
            NoticeRow(
                title=title,
                bbs_mst_idx=match.group(1),
                data_idx=match.group(2),
                date=date_match.group(0),
            )
        )
    return rows


def select_recent(rows: list[NoticeRow], limit: int = 4) -> list[NoticeRow]:
    """날짜 내림차순 정렬 후 상위 limit개. 같은 날짜끼리는 원래(문서) 순서를
    유지한다 (Python sort는 stable이라 reverse=True로도 보장됨)."""
    return sorted(rows, key=lambda r: r.date, reverse=True)[:limit]


def _to_notice(row: NoticeRow) -> Notice:
    return Notice(
        id=row.data_idx,
        title=row.title,
        category="ACADEMIC",
        # 목록 페이지엔 날짜만 있고 시각은 없다 - 시각을 지어내지 않기 위해
        # 00:00:00으로 고정하고, 필드 자체는 계약이 요구하는 datetime 형식에
        # 맞추기 위한 표기일 뿐 "0시에 게시됐다"는 사실을 주장하는 게 아니다.
        publishedAt=f"{row.date}T00:00:00+09:00",
        url=f"{DETAIL_BASE_URL}?menu_idx=169&bbs_mst_idx={row.bbs_mst_idx}&data_idx={row.data_idx}",
    )


def fetch_recent_notices(limit: int = 4, *, http_client: httpx.Client | None = None) -> list[Notice]:
    """네트워크 조회 + 파싱 + 최신 limit개 선택. 실패(네트워크 오류, HTTP
    오류, 파싱 실패)는 전부 빈 리스트를 반환한다 - 호출자(notice_repository)가
    이전에 성공한 캐시를 계속 쓰거나, 캐시도 없으면 정직하게 빈 목록을
    보여준다. 가짜 공지를 지어내지 않는다."""
    # http_client가 안 넘어오면(스케줄러/실제 운영 경로) 우리가 직접 만든
    # httpx.Client를 함수 끝에서 반드시 닫는다 - 이 함수가 6시간마다 영원히
    # 반복 호출되므로, 안 닫으면 커넥션이 계속 쌓인다. 테스트가 주입한
    # client(MockTransport 등)는 호출자 소유라 우리가 닫지 않는다.
    owns_client = http_client is None
    client = http_client or httpx.Client(timeout=5.0, headers={"User-Agent": USER_AGENT})
    try:
        try:
            response = client.get(LIST_URL)
            response.raise_for_status()
            rows = parse_notice_list_html(response.text)
        except Exception:
            logger.exception("failed to fetch academic notices list")
            return []

        if not rows:
            # 200 OK인데 파싱된 행이 0개면, "학교가 공지를 안 올렸다"가 아니라
            # 게시판 HTML 구조가 바뀌어 셀렉터가 더 이상 안 맞을 가능성이 높다.
            # 그냥 조용히 빈 목록을 반환하면 이 문제를 아무도 못 알아챈다.
            logger.warning("academic notices list page returned 200 but parsed 0 rows - selector may be stale")

        notices = []
        for row in select_recent(rows, limit):
            notice = _to_notice(row)
            # 목록 페이지 자체가 긴 제목을 "..."로 잘라서 보여주는 경우가 실제로
            # 있다 - 상세페이지에서 진짜(안 잘린) 제목을 가져와 덮어쓴다. 상세
            # 조회가 실패하면 목록의 제목을 그대로 쓴다(지어내지 않고, 이미 가진
            # 정보를 버리지도 않는다).
            detail = mjc_detail.fetch_detail(notice.url, http_client=client)
            if detail is not None and detail.title:
                notice = notice.model_copy(update={"title": detail.title})
            notices.append(notice)
        return notices
    finally:
        if owns_client:
            client.close()

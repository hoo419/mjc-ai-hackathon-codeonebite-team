import re
from datetime import datetime

from app.core.time import KST
from app.rag import mjc_detail, mjc_search
from app.rag.mjc_detail import NoticeDetail
from app.schemas.chat import ChatResponse, ChatSource
from app.services import ai_client

MAX_CANDIDATES = 5
MAX_BODY_CHARS = 800

_SYSTEM_PROMPT = (
    "너는 명지전문대학교 AI 캠퍼스 비서다. 아래 '참고 자료'에 들어있는 내용만 "
    "사용해서 질문에 답하라. 자료에 없는 내용은 절대 추측하거나 지어내지 말고, "
    "자료에서 확인할 수 없으면 그렇다고 말해라. 자료에 나온 날짜/조건/절차 같은 "
    "사실은 바꾸지 말고 그대로 전달해라."
)

# 학교 통합검색은 거의 완전일치 검색이라, 자연어 질문을 그대로 보내면
# ("분납신청에대해", "분납신청 알려줘" 등) 0건이 나오는 걸 실측으로 확인했다
# ("분납신청"만 보내면 3건 나옴). 검색 전에 흔한 조사/요청 표현을 제거한다.
# 긴 표현을 먼저 걸러야 "에대해서"가 "에대해" 규칙에 걸려 "서"만 남는 일이
# 없다.
_FILLER_PHRASES = [
    "에 대해서",
    "에대해서",
    "에 대해",
    "에대해",
    "어떻게 해야 하나요",
    "어떻게 하나요",
    "어떻게 해",
    "언제 하나요",
    "언제인가요",
    "언제야",
    "알려주세요",
    "알려줘",
    "궁금합니다",
    "궁금해",
]

_TERM_RE = re.compile(r"(\d{4})학년도\s*(\d)학기")


def _clean_query(message: str) -> str:
    """순수함수. 자연어 질문에서 학교 사이트 검색에 방해되는 흔한 조사/요청
    표현을 제거한다. 다 지워서 아무것도 안 남으면 원문을 그대로 쓴다
    (검색이 빈 문자열보다는 원문으로 실패하는 게 낫다)."""
    cleaned = message
    for phrase in _FILLER_PHRASES:
        cleaned = cleaned.replace(phrase, "")
    cleaned = cleaned.strip(" ?!.")
    return cleaned or message


def _matches_query(document: NoticeDetail, query: str) -> bool:
    if query in document.title:
        return True
    tokens = [t for t in query.split() if len(t) >= 2]
    return any(token in document.title for token in tokens)


def _pick_best(documents: list[NoticeDetail], query: str) -> NoticeDetail:
    """학교 통합검색이 항상 관련도 순은 아니라서, 그냥 최신순으로만 고르면
    검색어와 무관한 최신 글이 뽑힐 수 있다 (실측으로 확인). 제목에 검색어
    (또는 그 일부 단어)가 실제로 들어있는 문서를 우선하고, 그런 문서가
    없으면 전체 중 최신순으로 고른다. 날짜가 없는 문서는 가장 오래된
    것으로 취급한다 (published_at은 'YYYY-MM-DD' 형식이라 문자열 비교로도
    날짜 순서가 유지된다)."""
    matching = [d for d in documents if _matches_query(d, query)]
    candidates = matching or documents
    return max(candidates, key=lambda d: d.published_at or "")


def _document_year(document: NoticeDetail) -> int | None:
    if not document.published_at:
        return None
    try:
        return int(document.published_at[:4])
    except ValueError:
        return None


def _extract_term_from_title(title: str) -> tuple[int, int] | None:
    """제목에 '2025학년도 2학기' 같은 명시적 학년도/학기 표기가 있으면
    (year, semester)로 뽑는다. 게시일과 공지가 다루는 학기가 다를 수 있어서
    (다음 학기 안내를 미리 올리는 경우 등) 게시일만으로는 부족하다."""
    match = _TERM_RE.search(title)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def _current_term(now: datetime) -> tuple[int, int]:
    """명지전문대 학사일정을 정확히 아는 API가 없어서 코드로 계산할 수 있는
    가장 단순하고 합리적인 근사치를 쓴다: 3~8월은 1학기, 9~12월은 2학기,
    1~2월은 전년도 2학기(겨울방학 연장)로 취급한다."""
    if now.month in (1, 2):
        return now.year - 1, 2
    if now.month <= 8:
        return now.year, 1
    return now.year, 2


def _term_order(term: tuple[int, int]) -> int:
    year, semester = term
    return year * 2 + (semester - 1)


def _is_stale(document: NoticeDetail, now: datetime) -> bool:
    """제목에 학기가 명시돼 있으면 그 학기가 지금 학기보다 과거인지로
    판단한다 (다음 학기 사전 공지는 미래 학기를 가리키므로 stale이
    아니다). 명시가 없으면 게시연도가 올해보다 이전인지로 근사한다."""
    term = _extract_term_from_title(document.title)
    if term is not None:
        return _term_order(term) < _term_order(_current_term(now))

    doc_year = _document_year(document)
    if doc_year is not None:
        return doc_year < now.year
    return False


def _build_answer_text(document: NoticeDetail) -> str:
    date_part = f" ({document.published_at})" if document.published_at else ""
    return f"가장 최근 관련 공지는 '{document.title}'{date_part}입니다. 자세한 내용은 출처를 확인해 주세요."


def _build_link_only_answer(document: NoticeDetail) -> str:
    date_part = f" ({document.published_at})" if document.published_at else ""
    return (
        f"'{document.title}'{date_part} 공지를 찾았지만, 첨부 문서 형식이라 "
        "내용을 직접 요약해드리기는 어렵습니다. 아래 출처에서 원문을 확인해 주세요."
    )


def _build_outdated_notice(document: NoticeDetail, now: datetime) -> str:
    """지금 학기 기준 정보는 아직 없다는 것과, 실제 게시연도(when)와 그
    공지가 다루는 학년도/학기(what it's about)를 구분해서 알려준다 - 이
    둘은 다를 수 있다 (다음 학기 안내를 그 전 해에 미리 올리는 경우 등)."""
    current_year, current_semester = _current_term(now)
    doc_term = _extract_term_from_title(document.title)
    posted_year = _document_year(document)
    posted_part = f"{posted_year}년도에 올라온 " if posted_year else ""

    if doc_term is not None:
        doc_year, doc_semester = doc_term
        return (
            f"{current_year}년도 {current_semester}학기 관련 공지는 아직 올라오지 않았고, "
            f"현재 확인되는 자료는 {posted_part}{doc_year}년도 {doc_semester}학기 "
            f"'{document.title}'입니다."
        )

    date_part = f" ({document.published_at})" if document.published_at else ""
    return (
        f"{current_year}년도 {current_semester}학기 관련 공지는 아직 올라오지 않았습니다. "
        f"참고로 확인된 가장 최근 자료는 '{document.title}'{date_part}입니다."
    )


def _build_context(document: NoticeDetail) -> str:
    date_part = f" ({document.published_at})" if document.published_at else ""
    return f"제목: {document.title}{date_part}\n내용: {document.body[:MAX_BODY_CHARS]}"


def answer(question: str, *, now: datetime | None = None) -> ChatResponse | None:
    """학교 사이트를 실시간으로 검색해서 가장 최근에 올라온 관련 공지 하나를
    찾아 링크와 함께 답한다. 아무것도 못 찾으면 None을 반환해 호출자
    (chat_service)가 NO_DATA_ANSWER로 폴백하게 한다 - 절대 학교 정책을
    지어내지 않는다 (AI_AGENT_RULES.md)."""
    now = now or datetime.now(KST)
    query = _clean_query(question)
    urls = mjc_search.search_school_site(query)

    documents: list[NoticeDetail] = []
    for url in urls[:MAX_CANDIDATES]:
        detail = mjc_detail.fetch_detail(url)
        if detail is not None:
            documents.append(detail)

    if not documents:
        return None

    documents_with_body = [d for d in documents if d.body]
    latest = _pick_best(documents_with_body or documents, query)
    sources = [ChatSource(title=latest.title, url=latest.url)]

    if _is_stale(latest, now):
        return ChatResponse(answer=_build_outdated_notice(latest, now), sources=sources)

    if not documents_with_body:
        # Found real matching pages but couldn't pull usable text out of
        # any of them (e.g. HWP-embedded posts) - still recommend the most
        # recent one as a link instead of claiming nothing was found.
        return ChatResponse(answer=_build_link_only_answer(latest), sources=sources)

    template_answer = _build_answer_text(latest)

    client = ai_client.get_client()
    if client is None:
        return ChatResponse(answer=template_answer, sources=sources)

    context = _build_context(latest)
    generated = client.generate(
        system=_SYSTEM_PROMPT, user=f"질문: {question}\n\n참고 자료:\n{context}"
    )
    return ChatResponse(answer=generated or template_answer, sources=sources)

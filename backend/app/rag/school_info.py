from app.rag import mjc_detail, mjc_search
from app.rag.mjc_detail import NoticeDetail
from app.schemas.chat import ChatResponse, ChatSource
from app.services import ai_client

MAX_CANDIDATES = 5
MAX_DOCUMENTS = 3
MAX_BODY_CHARS_PER_DOC = 800

_SYSTEM_PROMPT = (
    "너는 명지전문대학교 AI 캠퍼스 비서다. 아래 '참고 자료'에 들어있는 내용만 "
    "사용해서 질문에 답하라. 자료에 없는 내용은 절대 추측하거나 지어내지 말고, "
    "자료에서 확인할 수 없으면 그렇다고 말해라. 자료에 나온 날짜/조건/절차 같은 "
    "사실은 바꾸지 말고 그대로 전달해라."
)


def _build_template_answer(documents: list[NoticeDetail]) -> str:
    titles = ", ".join(f"'{d.title}'" for d in documents)
    return f"관련 공지를 찾았습니다: {titles} 등 {len(documents)}건. 자세한 내용은 출처를 확인해 주세요."


def _build_context(documents: list[NoticeDetail]) -> str:
    parts = []
    for d in documents:
        date_part = f" ({d.published_at})" if d.published_at else ""
        parts.append(f"제목: {d.title}{date_part}\n내용: {d.body[:MAX_BODY_CHARS_PER_DOC]}")
    return "\n\n".join(parts)


def answer(question: str) -> ChatResponse | None:
    """Searches the school site in real time, fetches up to MAX_DOCUMENTS
    parseable notices, and asks the AI to answer using only their content.
    Returns None if nothing usable was found, so the caller (chat_service)
    falls back to NO_DATA_ANSWER instead of fabricating a school-policy
    answer (AI_AGENT_RULES.md)."""
    urls = mjc_search.search_school_site(question)

    documents: list[NoticeDetail] = []
    for url in urls[:MAX_CANDIDATES]:
        detail = mjc_detail.fetch_detail(url)
        if detail is not None:
            documents.append(detail)
        if len(documents) >= MAX_DOCUMENTS:
            break

    if not documents:
        return None

    sources = [ChatSource(title=d.title, url=d.url) for d in documents]
    template_answer = _build_template_answer(documents)

    client = ai_client.get_client()
    if client is None:
        return ChatResponse(answer=template_answer, sources=sources)

    context = _build_context(documents)
    generated = client.generate(
        system=_SYSTEM_PROMPT, user=f"질문: {question}\n\n참고 자료:\n{context}"
    )
    return ChatResponse(answer=generated or template_answer, sources=sources)

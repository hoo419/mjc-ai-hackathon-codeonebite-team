# 학교정보 RAG (Phase 10) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chat API의 `SCHOOL_INFO` intent가 고정된 "확인할 수 없습니다" 대신, 명지전문대 공식 사이트를 실시간으로 검색해서 실제 공지 내용으로 답하게 만든다.

**Architecture:** 질문 → 학교 통합검색(실시간 HTTP POST) → 상위 후보 상세페이지 실시간 fetch+파싱(HWP 임베드 글은 스킵) → 문서 3개 모이면 AI가 "그 안의 내용만" 으로 답변 생성(AI 미설정 시 안전한 템플릿 답변) → `ChatResponse.sources`에 실제 URL. 아무것도 못 찾으면 기존 `NO_DATA_ANSWER` 그대로.

**Tech Stack:** 기존 FastAPI/httpx/pytest + 신규 `beautifulsoup4` (HTML 파싱). 로컬 임베딩/pgvector/사전 크롤링 없음.

## Global Constraints

- 새 프레임워크/대형 라이브러리를 임의로 추가하지 않는다 — 이번엔 `beautifulsoup4` 하나만 추가한다 (`TECH_STACK.md`)
- LLM은 제공된 자료 밖의 내용을 추측/생성하지 않는다 — 검색 결과가 없거나 파싱 실패하면 그대로 `NO_DATA_ANSWER`, 지어내지 않는다 (`AI_AGENT_RULES.md`)
- AI Provider 오류를 사용자에게 traceback으로 노출하지 않는다, 서버 로그에만 남긴다 (`AI_AGENT_RULES.md` 실패 처리)
- `frontend/`는 건드리지 않는다
- 기존 코드 스타일을 따른다: 함수/파일 상단에 "왜"를 설명하는 주석, `app/services`가 `app/rag`를 호출하는 계층 구조, `httpx.MockTransport`로 네트워크 코드 단위테스트 (`app/services/ai_client.py`가 이미 쓰는 패턴 그대로)
- 실제 학교 사이트/실제 AI로의 최종 확인은 자동화 테스트가 아니라 수동으로 한 번 진행한다 (기존 Phase 7/9와 동일한 방식)

---

### Task 1: `NoticeDetail` 파싱 (`app/rag/mjc_detail.py`)

**Files:**
- Create: `backend/app/rag/__init__.py` (빈 파일)
- Create: `backend/app/rag/mjc_detail.py`
- Test: `backend/tests/test_rag_mjc_detail.py`
- Fixtures (이미 존재함, 새로 만들 필요 없음): `backend/tests/fixtures/mjc_detail_plain.html`, `backend/tests/fixtures/mjc_detail_hwp.html`

**Interfaces:**
- Produces:
  - `NoticeDetail` dataclass: `title: str`, `body: str`, `published_at: str | None`, `url: str`
  - `parse_detail_html(html: str, url: str) -> NoticeDetail | None` (순수함수)
  - `fetch_detail(url: str, *, http_client: httpx.Client | None = None) -> NoticeDetail | None`

- [ ] **Step 1: 디렉터리와 빈 `__init__.py` 생성**

```bash
mkdir -p backend/app/rag
touch backend/app/rag/__init__.py
```

- [ ] **Step 2: 실패하는 테스트 작성**

`backend/tests/test_rag_mjc_detail.py`:

```python
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
    detail = parse_detail_html("<html><body>no board view here</body></html>", url="https://example.com")

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
```

- [ ] **Step 3: 테스트 실패 확인**

Run: `cd backend && ./.venv/Scripts/python.exe -m pytest tests/test_rag_mjc_detail.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.rag.mjc_detail'` (또는 `bs4` 미설치 에러)

- [ ] **Step 4: `beautifulsoup4` 설치 및 `requirements.txt` 반영**

```bash
cd backend
./.venv/Scripts/python.exe -m pip install "beautifulsoup4>=4.12"
```

`backend/requirements.txt`에 한 줄 추가:
```
beautifulsoup4>=4.12
```

- [ ] **Step 5: 최소 구현 작성**

`backend/app/rag/mjc_detail.py`:

```python
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

    body_el = soup.select_one("#divMemo")
    body = body_el.get_text("\n", strip=True) if body_el else ""
    if not body:
        return None  # covers both "no body container" and HWP-embedded posts

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
```

- [ ] **Step 6: 테스트 통과 확인**

Run: `cd backend && ./.venv/Scripts/python.exe -m pytest tests/test_rag_mjc_detail.py -v`
Expected: 6 passed

- [ ] **Step 7: 커밋**

```bash
git add backend/app/rag/__init__.py backend/app/rag/mjc_detail.py backend/tests/test_rag_mjc_detail.py backend/requirements.txt
git commit -m "feat: 학교 공지 상세페이지 파싱 (app/rag/mjc_detail.py)"
```

---

### Task 2: 학교 통합검색 (`app/rag/mjc_search.py`)

**Files:**
- Create: `backend/app/rag/mjc_search.py`
- Test: `backend/tests/test_rag_mjc_search.py`
- Fixture (이미 존재함): `backend/tests/fixtures/mjc_search_results.html`

**Interfaces:**
- Consumes: 없음 (독립적인 모듈)
- Produces:
  - `search_school_site(query: str, *, http_client: httpx.Client | None = None) -> list[str]`
  - `_extract_result_urls(html: str) -> list[str]` (순수함수, 테스트/디버깅용으로 공개)

- [ ] **Step 1: 실패하는 테스트 작성**

`backend/tests/test_rag_mjc_search.py`:

```python
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
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd backend && ./.venv/Scripts/python.exe -m pytest tests/test_rag_mjc_search.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.rag.mjc_search'`

- [ ] **Step 3: 최소 구현 작성**

`backend/app/rag/mjc_search.py`:

```python
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
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `cd backend && ./.venv/Scripts/python.exe -m pytest tests/test_rag_mjc_search.py -v`
Expected: 5 passed

- [ ] **Step 5: 커밋**

```bash
git add backend/app/rag/mjc_search.py backend/tests/test_rag_mjc_search.py
git commit -m "feat: 명지전문대 통합검색으로 관련 게시글 URL 찾기 (app/rag/mjc_search.py)"
```

---

### Task 3: 검색+요약 오케스트레이션 (`app/rag/school_info.py`)

**Files:**
- Create: `backend/app/rag/school_info.py`
- Test: `backend/tests/test_rag_school_info.py`

**Interfaces:**
- Consumes:
  - `mjc_search.search_school_site(query: str) -> list[str]` (Task 2)
  - `mjc_detail.fetch_detail(url: str) -> NoticeDetail | None`, `NoticeDetail(title, body, published_at, url)` (Task 1)
  - `ai_client.get_client() -> AIClient | None`, `AIClient.generate(*, system: str, user: str) -> str | None` (기존 `app/services/ai_client.py`)
  - `ChatResponse(answer: str, sources: list[ChatSource] = [], courses=[], actions=[])`, `ChatSource(title: str, url: str)` (기존 `app/schemas/chat.py`)
- Produces:
  - `answer(question: str) -> ChatResponse | None` — Task 4에서 `chat_service.py`가 이 함수를 호출한다

- [ ] **Step 1: 실패하는 테스트 작성**

`backend/tests/test_rag_school_info.py`:

```python
from app.rag import school_info
from app.rag.mjc_detail import NoticeDetail
from app.schemas.chat import ChatSource


def _fake_detail(n: int) -> NoticeDetail:
    return NoticeDetail(
        title=f"공지 {n}",
        body=f"공지 {n}의 본문 내용입니다.",
        published_at=f"2026-01-0{n}",
        url=f"https://www.mjc.ac.kr/bbs/data/view.do?data_idx={n}",
    )


def test_answer_returns_none_when_no_search_results(monkeypatch):
    monkeypatch.setattr(school_info.mjc_search, "search_school_site", lambda q: [])

    assert school_info.answer("아무 질문") is None


def test_answer_returns_none_when_all_candidates_fail_to_parse(monkeypatch):
    monkeypatch.setattr(school_info.mjc_search, "search_school_site", lambda q: ["u1", "u2"])
    monkeypatch.setattr(school_info.mjc_detail, "fetch_detail", lambda url: None)

    assert school_info.answer("아무 질문") is None


def test_answer_stops_after_three_successful_documents(monkeypatch):
    urls = [f"u{i}" for i in range(5)]
    monkeypatch.setattr(school_info.mjc_search, "search_school_site", lambda q: urls)

    calls = []

    def fake_fetch(url):
        calls.append(url)
        return _fake_detail(len(calls))

    monkeypatch.setattr(school_info.mjc_detail, "fetch_detail", fake_fetch)
    monkeypatch.setattr(school_info.ai_client, "get_client", lambda: None)

    result = school_info.answer("질문")

    assert len(calls) == 3
    assert result is not None
    assert len(result.sources) == 3


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
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd backend && ./.venv/Scripts/python.exe -m pytest tests/test_rag_school_info.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.rag.school_info'`

- [ ] **Step 3: 최소 구현 작성**

`backend/app/rag/school_info.py`:

```python
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
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `cd backend && ./.venv/Scripts/python.exe -m pytest tests/test_rag_school_info.py -v`
Expected: 6 passed

- [ ] **Step 5: 커밋**

```bash
git add backend/app/rag/school_info.py backend/tests/test_rag_school_info.py
git commit -m "feat: 검색결과+AI로 학교정보 답변 조합 (app/rag/school_info.py)"
```

---

### Task 4: `chat_service.py`에 연결

**Files:**
- Modify: `backend/app/services/chat_service.py`
- Modify: `backend/tests/test_chat.py`

**Interfaces:**
- Consumes: `school_info.answer(question: str) -> ChatResponse | None` (Task 3)

- [ ] **Step 1: 기존 테스트를 실패하도록 먼저 바꾼다 (RED)**

`backend/tests/test_chat.py`에서 학교정보 관련 테스트 3개를 다음으로 교체한다 (`test_chat_school_info_question_returns_safe_fallback`, `test_chat_school_info_fallback_is_never_rephrased_by_ai` 를 찾아 교체하고, 새 테스트 하나를 추가):

```python
def test_chat_school_info_question_returns_safe_fallback_when_nothing_found(monkeypatch):
    monkeypatch.setattr(chat_service.school_info, "answer", lambda question: None)

    response = client.post("/api/chat", json={"message": "휴학 신청은 어떻게 해?"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "현재 연결된 데이터에서 확인할 수 없습니다."
    assert body["sources"] == []
    assert body["courses"] == []
    assert body["actions"] == []


def test_chat_school_info_returns_rag_answer_when_found(monkeypatch):
    from app.schemas.chat import ChatResponse, ChatSource

    fake_response = ChatResponse(
        answer="공지에 따르면 학기별로 휴학 신청 기간이 다릅니다.",
        sources=[ChatSource(title="휴학 안내", url="https://www.mjc.ac.kr/bbs/data/view.do?data_idx=1")],
    )
    monkeypatch.setattr(chat_service.school_info, "answer", lambda question: fake_response)

    response = client.post("/api/chat", json={"message": "휴학 신청은 어떻게 해?"})

    body = response.json()
    assert body["answer"] == "공지에 따르면 학기별로 휴학 신청 기간이 다릅니다."
    assert body["sources"] == [
        {"title": "휴학 안내", "url": "https://www.mjc.ac.kr/bbs/data/view.do?data_idx=1"}
    ]


def test_chat_school_info_fallback_is_never_rephrased_by_ai(monkeypatch):
    monkeypatch.setattr(chat_service.school_info, "answer", lambda question: None)
    monkeypatch.setattr(
        chat_service.ai_client, "get_client", lambda: _FakeAIClient("이렇게 저렇게 도와드릴게요.")
    )

    result = chat_service.handle_message("휴학 신청은 어떻게 해?")

    assert result.answer == "현재 연결된 데이터에서 확인할 수 없습니다."
```

기존에 있던 `test_chat_school_info_question_returns_safe_fallback` 함수와 (이름이 겹치는) 예전 `test_chat_school_info_fallback_is_never_rephrased_by_ai`는 위 코드로 완전히 대체한다 (둘 다 지금은 실제 네트워크를 타게 되어 그대로 두면 안 된다).

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd backend && ./.venv/Scripts/python.exe -m pytest tests/test_chat.py -v -k school_info`
Expected: FAIL — `AttributeError: module 'app.services.chat_service' has no attribute 'school_info'`

- [ ] **Step 3: `chat_service.py` 수정**

`backend/app/services/chat_service.py` 상단 import에 추가:

```python
from app.rag import school_info
```

`handle_message` 함수의 마지막 `else` 분기를 찾아 교체한다. 현재:

```python
    else:
        # SCHOOL_INFO: no RAG/document search exists yet (Phase 9-10), so we
        # never fabricate a school-policy answer, and never let the AI
        # rephrase this fixed safety sentence either.
        return ChatResponse(answer=NO_DATA_ANSWER)
```

다음으로 교체:

```python
    else:
        # SCHOOL_INFO: search the school site in real time and answer only
        # from what's actually found there (app/rag/school_info.py). This
        # path already produces a fact-constrained answer on its own, so it
        # skips the generic _rephrase() step below - and if nothing useful
        # was found, we fall back to the fixed safety sentence, never
        # fabricating a school-policy answer, and never letting the AI
        # rephrase that fixed sentence either.
        return school_info.answer(message) or ChatResponse(answer=NO_DATA_ANSWER)
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `cd backend && ./.venv/Scripts/python.exe -m pytest tests/test_chat.py -v -k school_info`
Expected: 3 passed

- [ ] **Step 5: 전체 테스트 스위트 통과 확인 (회귀 없음)**

Run: `cd backend && ./.venv/Scripts/python.exe -m pytest -q`
Expected: 모두 passed (기존 58개 + 이번에 추가한 테스트 전부)

- [ ] **Step 6: 커밋**

```bash
git add backend/app/services/chat_service.py backend/tests/test_chat.py
git commit -m "feat: Chat API의 SCHOOL_INFO를 실시간 학교 검색 RAG로 연결"
```

---

### Task 5: 실제 환경 수동 검증

자동화 테스트는 전부 가짜 네트워크(fixture/mock)로 돌아간다. 실제로 동작하는지는 지금까지(Phase 7 AI 클라이언트, Phase 9 DB)와 같은 방식으로 직접 서버를 띄워 확인한다. 코드 변경 없음 — 검증만 한다.

**Interfaces:** 없음 (검증 전용 태스크)

- [ ] **Step 1: 서버 기동**

```bash
cd backend
./.venv/Scripts/python.exe -m uvicorn app.main:app --port 8000
```

- [ ] **Step 2: 실제로 학교 공지에 있는 질문으로 확인**

새 터미널에서:

```bash
printf '{"message":"수강신청 언제까지야"}' > /tmp/rag_test1.json
curl -s -X POST http://127.0.0.1:8000/api/chat -H "Content-Type: application/json; charset=utf-8" --data-binary @/tmp/rag_test1.json
```

확인할 것:
- `answer`가 `"현재 연결된 데이터에서 확인할 수 없습니다."`가 **아닌** 실제 내용을 담고 있는지
- `sources`에 실제 `https://www.mjc.ac.kr/bbs/data/view.do?...` URL이 최소 1개 이상 들어있는지
- 응답이 몇 초 안에 오는지 (5초 타임아웃 x 최대 5개 후보 = 최악의 경우 시간이 걸릴 수 있음 - 체감 속도 확인)

- [ ] **Step 3: 무관한 질문으로 안전한 폴백 확인**

```bash
printf '{"message":"오늘 점심 뭐 먹을까"}' > /tmp/rag_test2.json
curl -s -X POST http://127.0.0.1:8000/api/chat -H "Content-Type: application/json; charset=utf-8" --data-binary @/tmp/rag_test2.json
```

확인할 것: 검색 결과가 없거나 무관해서 `NO_DATA_ANSWER`로 안전하게 떨어지는지 (지어낸 답을 하지 않는지)

- [ ] **Step 4: 서버 로그 확인**

`fetch_detail`/`search_school_site`가 실패를 삼키고 있진 않은지 (의도적으로 존재하지 않는 URL로 시도했을 때 `logger.exception` 로그가 서버 콘솔에 남는지) uvicorn 콘솔 출력 확인

- [ ] **Step 5: 서버 종료, 결과를 사용자에게 보고**

실제 질문/답변/출처 예시, 걸린 시간, 발견된 문제(있다면)를 정리해서 보고한다. 이 단계는 커밋 없음 (코드 변경 없는 검증 태스크).

---

## Self-Review 체크리스트 (계획 작성자가 직접 확인함)

- [x] 스펙의 모든 섹션이 태스크로 커버됨: 통합검색(Task 2), 상세페이지 파싱+HWP 스킵(Task 1), 검색+요약 오케스트레이션(Task 3), chat_service 연결(Task 4), 수동 검증(Task 5)
- [x] TBD/TODO/"나중에" 없음
- [x] 각 태스크의 함수 시그니처가 다음 태스크에서 실제로 그대로 쓰임 (`NoticeDetail`, `search_school_site`, `fetch_detail`, `school_info.answer`)
- [x] 범위 제외 사항(HWP 파싱, 타 서브사이트, 캐싱)은 스펙과 동일하게 유지, 이번 계획에도 새로 추가하지 않음

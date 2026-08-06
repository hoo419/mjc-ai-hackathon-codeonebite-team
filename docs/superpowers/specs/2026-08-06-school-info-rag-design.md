# 학교정보 RAG 설계 (Phase 10)

## 배경

`AI_AGENT_RULES.md`와 `PROJECT_REQUIREMENTS.md` 3.1절은 "학교정보 AI"를 요구한다: 학생이 "수강신청 기간이 언제야?", "휴학 신청은 어떻게 해?", "장학금 신청 조건 알려줘." 같은 질문을 하면, 공식 학교 공지를 검색해서 답하고 출처를 표시해야 한다. 데이터가 없으면 지어내지 않고 "현재 연결된 데이터에서 확인할 수 없습니다."라고 말해야 한다 (이미 `chat_service.NO_DATA_ANSWER`로 구현되어 있음 — Chat API의 `SCHOOL_INFO` intent가 지금은 항상 이 문구만 반환한다).

이 스펙은 그 자리를 실제 RAG(검색 + 요약)로 채운다.

## 아키텍처: 사전 크롤링이 아니라 실시간 검색

처음엔 "미리 전체 게시판을 크롤링 → 로컬 임베딩 → pgvector 벡터검색"으로 설계했으나, 명지전문대학 사이트에 이미 동작하는 **통합검색 기능**이 있는 것을 확인하고 방향을 바꿨다:

```
질문 → 학교 통합검색(실시간 HTTP 요청) → 관련 게시글 URL 후보
     → 상위 몇 개 상세페이지 실시간으로 열어서 본문 추출
     → AI가 그 내용만으로 답변 생성 + 출처 URL
     → (검색 결과 없음/전부 파싱 실패) → 기존 "확인할 수 없습니다" 그대로
```

이 방식의 장점 (실측으로 확인):
- 로컬 임베딩 모델(sentence-transformers/torch, ~420MB)도, pgvector도, 사전 크롤링 배치도 **전부 필요 없다** — 새 의존성은 `beautifulsoup4` 하나뿐
- 학교 사이트가 이미 "질문에 맞는 페이지 찾기"를 해주므로, 자체 검색/색인 로직을 만들 필요가 없다
- 항상 최신 — 재크롤링 주기를 신경 쓸 필요 없음
- Mock/DB 모드 여부와 무관하게 동작 (DB 불필요)

## 실측으로 확인한 것 (2026-08-06)

### 통합검색
- `robots.txt`: `Allow: /` (전체 허용)
- 엔드포인트: `POST https://www.mjc.ac.kr/RSA/front_new/Search.jsp`
- 요청 본문: `qt=<검색어>` — **검색어는 EUC-KR로 퍼센트 인코딩해서 보내야 한다.** UTF-8 그대로 보내면 서버가 못 알아듣고 "검색결과가 없습니다"를 반환한다 (직접 재현해서 확인함). 예: `"수강신청"` → `qt=%BC%F6%B0%AD%BD%C5%C3%BB`
- **응답은 평범한 UTF-8 HTML이다** (요청과 응답의 인코딩이 다름 — 레거시 시스템 특성. `<meta charset="utf-8">` 표시가 응답에 한해서는 정확하다)
- 응답 HTML 안에 실제 게시글 상세 URL이 `https://www.mjc.ac.kr/bbs/data/view.do?menu_idx=..&bbs_mst_idx=..&data_idx=..` 형태 그대로 포함되어 있어, 정규식으로 바로 추출 가능함을 확인 (테스트 픽스처: `backend/tests/fixtures/mjc_search_results.html`, "수강신청" 검색 시 URL 3개 추출됨)
- 이 URL 패턴에 안 맞는 결과(타 서브사이트, 영문/일문/중문 사이트 등)는 무시한다 — 이번 스펙은 `www.mjc.ac.kr/bbs/data/view.do` 게시글만 다룬다

### 게시글 상세 페이지 (`bbs/data/view.do`)
UTF-8 HTML.
- 제목: `.board_view h2.tit`
- 날짜: `.board_view table.tbl_data` 안에서 텍스트가 정확히 "날짜"인 `<th>`의 다음 형제 `<td>`
- 본문: `#divMemo` (순수 HTML로 작성된 글의 경우)
- **본문 추출 불가 케이스**: 담당자가 한글(HWP) 파일을 그대로 업로드해 게시한 글은 본문이 `#divMemo`가 아니라 `.hwp_editor_board_content`에 HWP 문서 전체가 독점 JSON으로 임베드되어 있다 (테스트 픽스처: `mjc_detail_hwp.html`). 이 포맷에서 사람이 읽는 텍스트를 뽑으려면 별도 HWP 파서가 필요해 이번 스펙 범위 밖이다. **`#divMemo`에 실질 텍스트가 없고 `.hwp_editor_board_content`가 있으면 해당 게시글은 스킵**한다 (깨진 텍스트를 답변 근거로 쓰지 않기 위함).

## 컴포넌트

기존 구조(`app/services/`, `app/schemas/`)와 같은 패턴으로 `app/rag/` 하위에 둔다. (TECH_STACK.md는 최상위 `ai/` 디렉터리를 계획했으나, FastAPI 앱의 기존 모듈들과 같은 import 루트를 쓰는 게 단순해서 `backend/app/rag/`로 결정 — 이 문서에 편차를 명시해둔다.)

### `app/rag/mjc_search.py`
```python
def search_school_site(query: str) -> list[str]:
    """검색 실패(네트워크 오류 등) 시 빈 리스트 반환 - 절대 예외를 던지지 않는다."""

def _extract_result_urls(html: str) -> list[str]:
    """순수함수. 검색결과 HTML에서 www.mjc.ac.kr/bbs/data/view.do URL만
    등장 순서대로 중복 없이 추출."""
```

### `app/rag/mjc_detail.py`
```python
@dataclass
class NoticeDetail:
    title: str
    body: str
    published_at: str | None
    url: str

def parse_detail_html(html: str, url: str) -> NoticeDetail | None:
    """순수함수. 제목이 없거나 본문을 못 뽑으면(HWP 등) None."""

def fetch_detail(url: str) -> NoticeDetail | None:
    """네트워크 요청 + 파싱. 어떤 실패든 None."""
```

### `app/rag/school_info.py`
```python
def answer(question: str) -> ChatResponse | None:
    """검색 -> 상위 문서 몇 개 fetch -> AI 요약. 아무것도 못 찾으면 None
    (호출자가 NO_DATA_ANSWER로 폴백)."""
```
- 검색 결과 URL을 최대 5개까지 순서대로 시도, 성공적으로 파싱된 문서가 3개 모이거나 후보가 바닥나면 중단
- 문서를 하나도 못 얻으면 `None`
- AI 클라이언트가 설정되어 있으면: "아래 자료 안의 내용만 사용해서 답하라, 자료에 없으면 모른다고 말해라"는 시스템 프롬프트 + 문서 본문(각 최대 800자)을 넘겨 답변 생성
- AI 클라이언트가 없거나 응답 실패: "관련 공지를 찾았습니다: '{title}' 등 {n}건. 출처를 확인해 주세요." 같은 안전한 템플릿 답변으로 대체 (지어내지 않음)
- 두 경우 모두 `ChatResponse.sources`에 실제 문서 제목/URL을 채운다

### `chat_service.py` 수정
`SCHOOL_INFO` intent 분기에서 `NO_DATA_ANSWER` 고정 반환 대신 `school_info.answer(message)` 호출, 결과가 `None`이면 기존처럼 `NO_DATA_ANSWER`. 이 경로는 이미 자체적으로 사실 제약된 AI 답변이므로 기존 `_rephrase()`(범용 말투 다듬기)는 거치지 않는다.

## 에러 처리

- 검색 요청 실패, 상세 페이지 요청 실패, HWP라서 파싱 불가 — 전부 해당 항목만 조용히 건너뛰고 계속 진행. 서버 로그에는 남기되 사용자에게 traceback 노출 안 함 (`AI_AGENT_RULES.md` 실패 처리 원칙과 동일)
- 네트워크 타임아웃은 요청당 5초로 제한 (느린 후보 하나가 전체 Chat 응답을 오래 붙잡지 않도록)
- 학교 사이트 자체가 완전히 응답 없어도 Chat API는 죽지 않고 `NO_DATA_ANSWER`로 안전하게 종료

## 테스트 전략

- `_extract_result_urls`, `parse_detail_html`: 저장된 실제 HTML 픽스처로 순수함수 단위 테스트 (네트워크 불필요) — `mjc_search_results.html`, `mjc_detail_plain.html`, `mjc_detail_hwp.html`
- `school_info.answer()`: `mjc_search.search_school_site`/`mjc_detail.fetch_detail`/`ai_client.get_client`를 가짜 값으로 주입해 조합 로직(문서 3개 모이면 중단, AI 있음/없음 분기, 문서 0개면 None) 단위 테스트
- 실제 학교 사이트 + 실제 AI로의 end-to-end 확인은 지금까지(Phase 7/9)와 같은 방식으로 한 번 수동 검증

## 범위에서 제외한 것

- HWP 임베드 게시글의 본문 파싱
- 학사공지/공지사항 외 다른 서브사이트(부서 홈페이지, 영문/일문/중문 사이트 등) 결과
- 학과사무실 사례(department_cases), 상담/검사 데이터 RAG — Phase 11/12
- 검색 결과 캐싱 (매 질문마다 실시간 재검색 — 트래픽이 문제가 되면 나중에 고려)

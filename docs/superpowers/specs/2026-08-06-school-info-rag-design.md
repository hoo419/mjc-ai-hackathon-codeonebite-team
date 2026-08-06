# 학교정보 RAG 설계 (Phase 10)

## 배경

`AI_AGENT_RULES.md`와 `PROJECT_REQUIREMENTS.md` 3.1절은 "학교정보 AI"를 요구한다: 학생이 "수강신청 기간이 언제야?", "휴학 신청은 어떻게 해?", "장학금 신청 조건 알려줘." 같은 질문을 하면, 공식 학교 공지를 검색해서 답하고 출처를 표시해야 한다. 데이터가 없으면 지어내지 않고 "현재 연결된 데이터에서 확인할 수 없습니다."라고 말해야 한다 (이미 `chat_service.NO_DATA_ANSWER`로 구현되어 있음 — Chat API의 `SCHOOL_INFO` intent가 지금은 항상 이 문구만 반환한다).

이 스펙은 그 자리를 실제 RAG(문서 검색 + 요약)로 채운다.

## 크롤링 대상

명지전문대학 공식 사이트 `www.mjc.ac.kr` (robots.txt 전체 허용 확인됨, `Allow: /`).

| 게시판 | menu_idx | bbs_mst_idx (게시판 ID) |
|---|---|---|
| 학사공지 | 169 | BM0000000025 |
| 공지사항(일반) | 66 | BM0000000026 |

- 목록: `GET /bbs/data/list.do?menu_idx={menu_idx}`
- 상세: `GET /bbs/data/view.do?menu_idx={menu_idx}&bbs_mst_idx={board_id}&data_idx={post_id}`
- `post_id`는 목록 페이지의 `fn_view('{board_id}','{post_id}','')` 자바스크립트 호출에서 정규식/BeautifulSoup로 추출한다 (헤드리스 브라우저 불필요, `httpx` + `BeautifulSoup`만으로 충분함을 확인했다).
- 게시판당 최근 30개, 총 최대 60개 문서.

## 데이터 모델

기존 `app/models/`(Course/Student/Enrollment)와 같은 패턴으로 2개 테이블 추가:

```
documents
  id (str, PK)            "BM0000000025:BD0050388061" 형태
  board_name (str)        "학사공지" / "공지사항"
  title (str)
  url (str)
  published_at (str)      게시판에 표시된 날짜 (파싱 실패 시 null)
  crawled_at (str)        수집 시각 (ISO, AI_AGENT_RULES: 동적 정보엔 수집시간 기록)
  body (text)             정제된 본문 텍스트

document_chunks
  id (int, PK, autoincrement)
  document_id (str, FK -> documents.id)
  chunk_index (int)
  content (text)
  embedding (vector(384))  # pgvector, sentence-transformers 모델 차원과 일치
```

## 파이프라인

### 1. 수집 (`ai/crawler/mjc_notices.py`)
- 목록 페이지 → 게시글 (board_id, post_id, title) 목록 파싱 (순수 함수, 테스트 가능)
- 상세 페이지 → (title, body, published_at) 파싱 (순수 함수, 테스트 가능)
- 이미 `documents` 테이블에 있는 (board_id, post_id)는 재수집 생략 (중복 방지)
- 원문을 `documents`에 저장

이 모듈은 `ai/` 디렉터리에 둔다 (TECH_STACK.md 구조: `ai/`는 개발자 A 담당, 크롤러/RAG 전용). Backend API 서버와는 별도 스크립트로 실행하는 배치 작업이다 (`python -m ai.crawler.mjc_notices` 형태), 매 요청마다 크롤링하지 않는다.

### 2. 청크 분할 + 임베딩 (`ai/rag/indexer.py`)
- 본문이 500자를 넘으면 문단 경계 기준으로 분할 (짧은 공지는 통째로 1개 청크)
- `sentence-transformers`의 `paraphrase-multilingual-MiniLM-L12-v2`(384차원, 다국어/한국어 지원)로 임베딩 생성
- `document_chunks`에 저장 (기존 청크는 재계산 없이 skip)

### 3. 검색 + 답변 (`ai/rag/search.py`, `chat_service.py` 연동)
- 사용자 질문을 같은 모델로 임베딩
- pgvector 코사인 거리로 `document_chunks` top-3 검색
- 거리가 임계값보다 가까우면: 상위 청크 본문 + 출처(document.url, title)를 `ai_client.generate()`에 "이 내용 안에서만 답하라"는 시스템 프롬프트와 함께 전달해 자연어 답변 생성. `ChatResponse.sources`에 실제 URL/제목 채움
- 임계값 미달이거나 결과 자체가 없으면(DB 모드가 아니거나, 아직 색인이 없거나): 기존 `NO_DATA_ANSWER` 그대로 반환 — **여기서 지어내지 않는다는 원칙은 그대로 유지**
- 임계값 자체는 지금 숫자로 못박지 않는다. 실제 크롤링 데이터로 임베딩을 만든 뒤, "수강신청 기간 알려줘"처럼 명백히 관련 있는 질문과 "오늘 저녁 뭐 먹지" 같은 명백히 무관한 질문의 실제 거리값을 비교해서 구현 단계에서 경험적으로 정한다 (근거 없이 숫자를 추측하지 않는다는 원칙과 동일하게 적용)

### Mock 모드와의 관계
`DATABASE_URL`이 없으면 (Mock 모드) RAG 전체가 비활성화되고 `SCHOOL_INFO` intent는 지금처럼 `NO_DATA_ANSWER`만 반환한다. pgvector는 실제 Postgres가 있어야만 의미가 있어서, 이 기능은 DB 모드 전용이다.

## 새 의존성

- `beautifulsoup4` — HTML 파싱
- `sentence-transformers` (+ `torch`, CPU) — 로컬 임베딩. 최초 실행 시 모델(~420MB) 다운로드
- `pgvector` — SQLAlchemy용 `Vector` 컬럼 타입, Neon에 `CREATE EXTENSION IF NOT EXISTS vector` 필요

설치 용량/시간이 지금까지보다 훨씬 크다 (`torch` 포함) — 설치 후 실제로 문제없이 동작하는지 반드시 확인한다.

## 테스트 전략

- 목록/상세 HTML 파싱 함수: 실제 사이트에서 받은 HTML을 테스트 픽스처로 저장해두고, 네트워크 없이 순수함수로 단위 테스트
- 청크 분할 로직: 순수함수, 일반 단위 테스트
- 임베딩/벡터검색: 실제 모델 로딩·실제 Postgres가 필요해 일반 pytest로는 못 돌린다. 지금까지(Phase 7 AI 클라이언트, Phase 9 DB)와 같은 방식으로 **한 번 실제 환경에 대고 수동 검증**한다 (크롤링 실행 → 색인 → 실제 질문으로 chat API 호출 → 답변/출처 확인)
- `chat_service`의 임계값 판단/폴백 로직 자체는 검색 결과를 가짜 값으로 주입해 순수 단위 테스트 가능

## 에러 처리

- 크롤링 중 특정 게시글 파싱 실패 → 해당 게시글만 스킵하고 계속 진행 (전체 배치를 죽이지 않음), 로그에 남김
- 임베딩 모델 로딩 실패/pgvector 미설치 등 RAG 인프라 자체가 안 되면 → `SCHOOL_INFO`는 자동으로 기존 `NO_DATA_ANSWER` 폴백 (Chat API가 죽지 않음, AI_AGENT_RULES.md 실패 처리 원칙과 동일)

## 범위에서 제외한 것

- 정기 재크롤링 스케줄링(cron 등) — 이번엔 수동 1회 실행 스크립트만
- 학과사무실 사례(department_cases), 상담/검사 데이터 RAG — Phase 11/12, 이번 스펙 밖
- 첨부파일(PDF 등) 파싱 — 게시글 본문 텍스트만

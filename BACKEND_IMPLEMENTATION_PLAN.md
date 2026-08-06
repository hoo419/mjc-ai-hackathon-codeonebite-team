# Backend Implementation Plan

## 목적
개발자 A가 Claude Code를 이용해 Backend/AI를 순차적으로 구현하기 위한 계획이다.

## Phase 0 — 저장소 분석
코드를 작성하기 전에:
1. 현재 디렉터리 구조 확인
2. 기존 파일 확인
3. 문서 확인
4. 기존 구현을 삭제하거나 덮어쓰지 않음
5. 필요한 작업 목록 작성

## Phase 1 — FastAPI 골격
권장 구조:
```text
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── courses.py
│   │   ├── students.py
│   │   ├── enrollment.py
│   │   ├── chat.py
│   │   ├── notices.py
│   │   ├── counseling.py
│   │   └── campus.py
│   ├── schemas/
│   ├── services/
│   ├── repositories/
│   ├── core/
│   └── models/
├── tests/
├── requirements.txt
└── .env.example
```

처음에는 과도한 계층화를 피한다.

필수:
- FastAPI app
- `/api` router
- CORS
- 환경변수 설정
- health endpoint

예:
```text
GET /health
```

## Phase 2 — Mock Data
```text
data/
├── courses.json
├── students.json
├── enrollments.json
├── notices.json
├── counseling.json
├── buildings.json
└── rooms.json
```

Mock 데이터라도 현실적인 다양한 상태를 포함한다.

Course 예:
- OPEN
- FULL
- CANCELLED
- UPCOMING
- CLOSED
- OFFLINE
- ONLINE_LIVE
- ONLINE_RECORDED
- HYBRID
- 전공필수
- 전공선택
- 교양필수
- 교양선택

최소 15~20개 과목을 만들어 필터링/시간표 테스트가 가능하게 한다.

## Phase 3 — Course Service
기능:
- 전체 조회
- ID 조회
- 검색어 필터
- status 필터
- classType 필터
- category 필터

중요:
잔여석은 데이터에서 계산한다.
```text
remaining = capacity - enrolled
```

OPEN이라고 저장되어 있어도 정원이 찼다면 신청 로직에서 거절할 수 있도록 방어한다.

## Phase 4 — Student / Schedule
Mock 학생 1명을 기준으로 시작한다.

기능:
- 학생 기본정보
- 신청 과목
- 주간 시간표

시간표 데이터는 가능하면 별도 중복 저장보다 Enrollment + Course에서 생성한다.

## Phase 5 — Enrollment
수강신청 전 검증 순서:
1. Course 존재 여부
2. 이미 신청했는지
3. CANCELLED 여부
4. 신청기간/상태
5. 정원
6. 학생 자격
7. 시간 충돌
8. 신청 처리

오류 코드는 `API_CONTRACT.md`를 따른다.

시간 충돌은 LLM이 아닌 Python 코드로 검사한다.

## Phase 6 — Chat API
초기에는 AI API가 없어도 동작할 수 있는 fallback을 고려한다.

Chat 처리 구조:
```text
message
 ↓
intent / parameter extraction
 ↓
tool/service call
 ↓
structured result
 ↓
LLM response generation
 ↓
API_CONTRACT response
```

첫 지원 의도:
- 과목 검색
- 신청 가능 과목 검색
- 시간표 질문
- 다음 수업 질문
- 학교정보 질문

AI API 연결 실패 시 서버 전체가 죽지 않도록 오류 처리한다.

## Phase 7 — OpenAI-compatible API
환경변수 예:
```text
AI_API_BASE_URL=
AI_API_KEY=
AI_MODEL=
```

특정 공급자 SDK에 강하게 종속되지 않게 구성한다.

AI Client를 서비스 레이어로 분리한다.

## Phase 8 — PostgreSQL
Mock 기반 통합이 성공한 뒤 적용한다.

예상 테이블:
- students
- courses
- course_sections
- enrollments
- notices
- buildings
- rooms
- department_cases
- counseling_records
- career_tests
- personality_tests
- documents
- document_chunks

SQLAlchemy를 사용한다.

## Phase 9 — 학교 홈페이지 수집
```text
ai/
└── crawler/
```

기능:
- 허용된 공개 학교 페이지 수집
- 제목
- URL
- 본문
- 게시일
- 수집시간

동적/변경 가능 정보는 수집시간을 기록한다.

## Phase 10 — RAG
```text
공식 학교 문서
 ↓
정제
 ↓
Chunk
 ↓
Embedding
 ↓
pgvector
 ↓
Similarity Search
 ↓
LLM
```

답변에는 가능한 경우 출처 URL을 반환한다.

## Phase 11 — Department Cases
학과사무실 과거 사례를 별도 데이터로 관리한다.

AI는 사례를 '확정 행정결정'처럼 표현하지 않는다.

## Phase 12 — Counseling
상담/검사 결과는 Mock부터 구현한다.

Frontend에는 필요한 요약 정보만 전달한다.

## 개발 중 항상 확인할 것
- API_CONTRACT 준수
- Frontend 수정 금지
- API Key 노출 금지
- 사실 데이터를 LLM이 생성하지 않는지
- Mock → 실제 DB 교체가 가능한 구조인지

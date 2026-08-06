# 개발자 A 작업 가이드 — Backend / AI

## 역할
당신은 MJC AI Campus Agent 프로젝트의 개발자 A이다.

담당 영역:
- Backend
- AI Agent
- 학교정보 RAG
- 데이터 수집
- Mock 데이터
- Database
- REST API

개발자 B는 `frontend/`를 담당한다. 특별한 합의 없이 `frontend/`를 수정하지 않는다.

## 반드시 먼저 읽을 문서
프로젝트 루트에 아래 문서가 있으면 작업 전에 모두 읽는다.
1. `TECH_STACK.md`
2. `PROJECT_REQUIREMENTS.md`
3. `API_CONTRACT.md`
4. `DEVELOPER_A_BACKEND_TASKS.md`
5. `BACKEND_IMPLEMENTATION_PLAN.md`
6. `AI_AGENT_RULES.md`

문서 간 충돌 시 `API_CONTRACT.md`의 API 요청/응답 규격을 우선한다.

## 기술 스택
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL (2단계)
- pgvector (RAG 단계)
- httpx
- BeautifulSoup
- OpenAI-compatible AI API

## 담당 디렉터리
```text
backend/
ai/
data/
```

공동 작업 가능:
```text
shared/
docs/
```

가급적 수정 금지:
```text
frontend/
```

## 1차 개발 목표
처음부터 PostgreSQL, RAG, 크롤러를 모두 구현하지 않는다.

먼저 Mock JSON 기반으로 Frontend가 사용할 REST API를 완성한다.

최초 통합 성공 조건:
```text
Frontend
  ↓
POST /api/chat
  ↓
AI/Intent 처리
  ↓
Course Service
  ↓
Mock Course Data
  ↓
조건에 맞는 과목
  ↓
Chat Response
  ↓
Frontend
```

예제 질문:
> 지금 신청 가능한 온라인 교양 과목 알려줘.

## 구현할 API
`API_CONTRACT.md`를 정확히 따른다.

우선순위:
1. `GET /api/courses`
2. `GET /api/courses/{courseId}`
3. `GET /api/students/me`
4. `GET /api/students/me/courses`
5. `GET /api/students/me/schedule`
6. `POST /api/enrollment`
7. `DELETE /api/enrollment/{courseId}`
8. `POST /api/chat`
9. `GET /api/notices`
10. `GET /api/counseling/me`
11. `POST /api/counseling/request`
12. `GET /api/buildings`
13. `GET /api/rooms/{roomId}`

## 핵심 규칙
### LLM이 판단하면 안 되는 데이터
- 폐강 여부
- 정원
- 현재 수강인원
- 잔여석
- 수강신청 가능 여부
- 수업 시간
- 강의실
- 수업방식
- 실제 학생 수강 여부

이 정보는 코드/API/DB 결과를 사용한다.

### AI가 담당하는 것
- 사용자 의도 파악
- 필요한 Tool 선택
- 검색 조건 추출
- 여러 Tool 결과 종합
- 학생에게 자연스럽게 설명
- RAG 결과 요약

## 보안
- API Key 하드코딩 금지
- `.env` 사용
- `.env` Git 커밋 금지
- `.env.example`에는 변수명만 기록
- AI API Key는 Backend에서만 사용
- Frontend에 AI API Key 전달 금지

## Git
작업 브랜치 권장:
```text
feature/backend-ai
```

큰 작업을 한 번에 커밋하지 않는다.

예:
```text
feat: initialize FastAPI backend
feat: add mock course service
feat: implement course endpoints
feat: implement enrollment validation
feat: add chat endpoint
```

## 완료 기준
- FastAPI 서버 실행 가능
- `/docs` Swagger 정상 동작
- Mock 데이터 로드 가능
- Course API 동작
- Student/Schedule API 동작
- Enrollment 검증 동작
- Chat API 동작
- CORS 설정으로 Frontend 개발 서버 연결 가능
- API_CONTRACT.md와 응답 형식 일치
- 테스트 가능한 구조

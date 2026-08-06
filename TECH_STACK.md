# MJC AI Hackathon — 기술 스택

## 프로젝트
명지전문대학교 학생용 AI Campus Agent 웹앱

## 목표
학교 정보 질의응답, 수강정보/시간표, 강의실 안내, 학과사무실 사례, 상담 연결 기능을 하나의 AI 비서에서 제공한다.

## 확정 기술 스택

### Frontend — 개발자 B 담당
- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- REST API 기반 백엔드 연동

### Backend / AI — 개발자 A 담당
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- REST API

### Database
- 초기 MVP: Mock JSON 데이터
- 본 개발: PostgreSQL
- RAG Vector Search: pgvector

### AI
- OpenAI-compatible API
- 메인 Agent: 사용자 의도 파악, Tool Calling, 결과 설명
- 학교정보: RAG
- 폐강 여부, 잔여석, 수강 가능 여부 등 사실 정보는 LLM이 추측하지 않고 API/DB 결과를 사용한다.

### 데이터 수집
- httpx
- BeautifulSoup
- 학교 홈페이지/공지 수집 후 RAG 데이터로 가공

## 기본 구조
```text
frontend/          # 개발자 B
backend/           # 개발자 A
ai/                # 개발자 A
data/              # 개발자 A
shared/            # 공동 API 타입/규격
docs/              # 공동 문서
```

## 개발 순서
1. Next.js + FastAPI + Mock JSON으로 프론트/백엔드 연결
2. Course / Student / Schedule API 구현
3. AI Chat API 및 Tool Calling 연결
4. PostgreSQL 적용
5. 학교 홈페이지 크롤링
6. pgvector 기반 RAG
7. 실제 학교 시스템 연동 가능한 부분 교체

## 공통 개발 규칙
- API Key를 프론트엔드 코드에 넣지 않는다.
- 비밀값은 `.env`에만 저장한다.
- `.env`는 Git에 커밋하지 않는다.
- 새로운 프레임워크/대형 라이브러리를 임의로 추가하지 않는다.
- 프론트와 백엔드는 REST API 계약을 기준으로 독립적으로 개발한다.
- `main` 브랜치 직접 작업을 피하고 기능 브랜치를 사용한다.

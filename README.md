# MJC AI 해커톤 - 코드한입조

명지전문대 AI 해커톤 참가용 저장소입니다. 프로젝트명: **MJC AI Campus Agent**.

## 대회 정보

- 대회명: (2026 ai해커톤 경진대회)
- 주제: 명지전문대 학생용 AI 캠퍼스 비서
- 팀명: 코드한입조

## 팀원 / 역할 분담

| 이름 | 역할 | 담당 |
|---|---|---|
| 임채호 | Backend/AI/Frontend 전체 | `backend/`, `frontend/`, `data/`, DB, RAG |
| 조영남 | (초기 Frontend MVP 참여) | - |

2026-08-07부터는 임채호가 Backend/Frontend 전체를 직접 담당한다.

## 진행 상황

- [x] 저장소 생성 / 기술 스택 확정 (`TECH_STACK.md`)
- [x] Backend: Course/Student/Enrollment/Chat/Counseling/Buildings·Rooms API 전부 구현 (Mock JSON ↔ PostgreSQL 듀얼 모드)
- [x] Backend: OpenAI 호환 AI 클라이언트 연동 (Chat 답변 다듬기)
- [x] Backend: PostgreSQL(Neon) 연동 — `DATABASE_URL` 비우면 Mock으로 자동 폴백
- [x] 학교정보 RAG (`www.mjc.ac.kr` 실시간 검색+상세조회 기반)
- [x] Frontend: 6개 화면(대시보드/채팅/과목검색/시간표/강의실/상담) 구현
- [x] Frontend ↔ Backend 실연동 통합 테스트 (`integration/fullstack-demo` 브랜치)
- [x] sugang.mjc.ac.kr 개설강좌 실데이터 246개 반영 (Mock/가짜 강의 데이터 제거)
- [x] 실제 배포 (Backend: Railway, Frontend: Vercel)
- [x] 발표 자료 정리

## 실행 방법
| 서비스 | URL | 설명 |
|---|---|---|
| 웹앱 | [frontend-ten-alpha-5uxgevufyr.vercel.app](https://frontend-ten-alpha-5uxgevufyr.vercel.app/) | Vercel에 배포된 사용자 화면 |
| Backend API | [mjc-ai-campus-agent-backend-production.up.railway.app](https://mjc-ai-campus-agent-backend-production.up.railway.app/) | Railway에 배포된 FastAPI 서버 |
| 상태 확인 | [/health](https://mjc-ai-campus-agent-backend-production.up.railway.app/health) | Backend 정상 동작 확인 |
| Swagger | [/docs](https://mjc-ai-campus-agent-backend-production.up.railway.app/docs) | 대화형 REST API 문서 |

 ++++주요기능++++
- **통합 대시보드**: 학생 정보, 다음 수업, 오늘의 시간표와 공지 확인
- **AI 캠퍼스 비서**: 과목 데이터와 명지전문대 학교정보 검색을 활용한 질의응답
- **과목 검색·수강신청**: 2026학년도 2학기 실제 개설강좌 246개 검색, 잔여석·시간 충돌 확인, 신청과 취소
- **주간 시간표**: 신청한 과목을 요일·교시별로 시각화
- **강의실 조회**: 건물과 강의실 정보 검색
- **상담 지원**: 상담 내역 조회, 상담 신청과 적성 분석
- **듀얼 데이터 모드**: 환경변수 하나로 Mock JSON 또는 PostgreSQL(Neon) 사용
## 문서 목록

| 문서 | 내용 |
|---|---|
| `DEMO_SETUP.md` | 로컬 데모 실행 방법 (환경변수, 실행 순서, 트러블슈팅) |
| `PROJECT_REQUIREMENTS.md` | 전체 기능 요구사항 |
| `TECH_STACK.md` | 확정 기술 스택 |
| `API_CONTRACT.md` | Frontend/Backend REST API 계약 |
| `AI_AGENT_RULES.md` | AI가 추측하면 안 되는 데이터 및 처리 원칙 |

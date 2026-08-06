# MJC AI 해커톤 - 코드한입조

명지전문대 AI 해커톤 참가용 저장소입니다. 프로젝트명: **MJC AI Campus Agent**.

## 대회 정보

- 대회명: (미정 — 확정 시 업데이트)
- 주제: 명지전문대 학생용 AI 캠퍼스 비서
- 팀명: 코드한입조

## 팀원 / 역할 분담

| 이름 | 역할 | 담당 |
|---|---|---|
| 임채호 | 개발자 A (Backend/AI) | `backend/`, `ai/`, `data/`, DB, RAG |
| 조영남 | 개발자 B (Frontend) | `frontend/`, 학생용 UI/UX |

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
- [ ] 발표 자료 정리

## 실행 방법

로컬에서 전체 데모(Frontend + Backend + DB)를 띄우는 방법은 **[DEMO_SETUP.md](./DEMO_SETUP.md)** 참고.

## 문서 목록

| 문서 | 내용 |
|---|---|
| `DEMO_SETUP.md` | 로컬 데모 실행 방법 (환경변수, 실행 순서, 트러블슈팅) |
| `PROJECT_REQUIREMENTS.md` | 전체 기능 요구사항 |
| `TECH_STACK.md` | 확정 기술 스택 |
| `API_CONTRACT.md` | Frontend/Backend REST API 계약 |
| `AI_AGENT_RULES.md` | AI가 추측하면 안 되는 데이터 및 처리 원칙 |

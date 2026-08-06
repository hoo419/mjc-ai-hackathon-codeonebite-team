# CLAUDE.md

## Project
MJC AI Campus Agent — 명지전문대 AI 해커톤용 학생 캠퍼스 비서 (Backend: FastAPI, Frontend: Next.js).

2026-08-07부터 임채호가 `backend/`, `frontend/`, `data/` 전체를 직접 담당한다 (예전
"개발자 A/B" 역할 분담은 더 이상 유효하지 않음).

## Before Coding
Read these files first:
- `TECH_STACK.md`
- `PROJECT_REQUIREMENTS.md`
- `API_CONTRACT.md` — Frontend/Backend 계약, 필드/엔드포인트 임의 변경 금지
- `AI_AGENT_RULES.md` — AI가 추측하면 안 되는 데이터 및 처리 원칙

Inspect the existing repository before creating, deleting, moving, or rewriting files.

## 절대 원칙
- 학교 사실정보(과목/건물/전화번호 등)를 지어내지 않는다. 확인 안 되면 `null`/빈 값 +
  이유 주석, 또는 실제 학교 페이지로의 링크로 대체한다.
- 실제 학교 로그인 자격증명은 백엔드가 절대 다루지 않는다.
- 저장소가 public이므로 진짜 비밀값은 절대 커밋하지 않는다. `backend/.env`,
  `frontend/.env.local`은 gitignore 대상. 배포 환경변수는 Railway/Vercel에 직접 설정.
- 새 기능은 TDD(RED→GREEN→COMMIT)로 진행하고, `feature/*` 브랜치에서 작업 후 리뷰를
  거쳐 `integration/fullstack-demo`(배포 기준 브랜치)에 병합한다.

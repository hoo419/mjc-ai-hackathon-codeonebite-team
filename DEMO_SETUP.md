# 데모 실행 가이드

이 문서는 `integration/fullstack-demo` 브랜치를 로컬에서 띄워서, Frontend(개발자 B)와 Backend(개발자 A)가 실제로 연결된 상태를 테스트하는 방법을 정리한다.

## 이 브랜치가 뭔가

- `feature/backend-ai` (Backend/AI, 개발자 A) + `feature/frontend-b-mvp` (Frontend, 개발자 B)를 합친 뒤, Frontend의 `lib/api/*.ts`가 더 이상 로컬 Mock 배열이 아니라 **실제 Backend API(`http://localhost:8000/api`)를 호출**하도록 바꿔놓은 통합/데모용 브랜치다.
- 각자의 원래 브랜치(`feature/backend-ai`, `feature/frontend-b-mvp`)는 건드리지 않았다.
- Backend는 `DATABASE_URL` 설정 여부에 따라 PostgreSQL(Neon) 또는 Mock JSON(`data/*.json`)으로 동작한다. 둘 중 뭘 쓰든 API 응답 형식은 동일하다.

## 사전 준비물

| 도구 | 버전 | 확인 명령 |
|---|---|---|
| Python | 3.11 이상 | `python --version` |
| Node.js | 20 이상 | `node --version` |
| npm | Node에 포함 | `npm --version` |
| git | 아무거나 | `git --version` |

## 0. 브랜치 받기

```bash
git clone https://github.com/hoo419/mjc-ai-hackathon-codeonebite-team.git
cd mjc-ai-hackathon-codeonebite-team
git checkout integration/fullstack-demo
git pull
```

## 1. 환경변수 파일 만들기

**`.env`, `.env.local` 파일은 비밀값이 들어가서 git에 올리지 않는다 (`.gitignore` 처리됨).** 아래 두 파일을 직접 만들어야 하고, 실제 값(API 키, DB 연결 문자열)은 **임채호에게 별도로(카톡 등) 전달받는다** — 이 문서나 git에는 절대 적지 않는다.

### `backend/.env`

`backend/.env.example`을 복사해서 채운다:

```bash
cp backend/.env.example backend/.env
```

| 변수 | 필수? | 설명 |
|---|---|---|
| `AI_API_BASE_URL` | 선택 | OpenAI 호환 AI Gateway 주소. 비워두면 Chat API가 규칙 기반 답변으로 동작 (fallback, 정상 동작함) |
| `AI_API_KEY` | 선택 | 위 Gateway의 API 키 |
| `AI_MODEL` | 선택 | 사용할 모델명 (예: `gpt-5.4-mini`) |
| `DATABASE_URL` | 선택 | PostgreSQL(Neon) 연결 문자열. 비워두면 `data/*.json` Mock으로 동작 (정상 동작함) |

**전부 비워둬도 앱은 정상 동작한다** (Mock 데이터 기반). AI/DB 값을 채우면 실제 AI 응답 다듬기와 실제 DB 영속성까지 테스트할 수 있다.

### `frontend/.env.local`

`frontend/.env.local.example`을 복사한다 (기본값 그대로 쓰면 됨, 수정 불필요):

```bash
cp frontend/.env.local.example frontend/.env.local
```

## 2. Backend 실행

```bash
cd backend
python -m venv .venv

# Windows (PowerShell/Git Bash)
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000

# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

정상 기동 확인:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

Swagger 문서: http://localhost:8000/docs

## 3. Frontend 실행

새 터미널을 열고:

```bash
cd frontend
npm install
npm run dev
```

http://localhost:3000 접속.

## 4. 확인해볼 것

- **대시보드 (`/`)**: 학생정보/다음수업/오늘시간표/공지 — 전부 Backend에서 오는 실데이터
- **과목검색 (`/courses`)**: 상태/잔여석 필터링, 이미 신청한 과목은 "신청완료"로 비활성화
- **수강신청**: 아무 "수강신청" 버튼 클릭 → 성공하면 정원 숫자가 즉시 바뀜, 시간표와 겹치면 `TIME_CONFLICT` 메시지가 그대로 뜸
- **시간표 (`/schedule`)**: 신청한 과목이 주간표에 반영되는지
- **AI 비서 (`/chat`)**: "지금 신청 가능한 온라인 교양 알려줘" 같은 질문에 실제 과목 카드로 응답하는지
- **강의실 (`/rooms`)**, **상담 (`/counseling`)**: 나머지 화면도 정상 응답하는지

## 문제 해결

| 증상 | 원인/해결 |
|---|---|
| Frontend에서 데이터가 안 뜨고 콘솔에 CORS 에러 | Backend가 안 떠 있거나 포트가 다름. `curl http://localhost:8000/health`로 먼저 확인 |
| `ModuleNotFoundError` (Backend) | 가상환경(.venv) 활성화 안 하고 `pip install`/`uvicorn` 실행한 경우 |
| 포트 충돌 (`Address already in use`) | 이전에 띄워둔 프로세스가 남아있음. 포트 8000/3000 점유 프로세스 종료 후 재시도 |
| DB 관련 에러 | `DATABASE_URL`을 비워두면 Mock 모드로 동작하니, DB 설정 없이 먼저 확인해볼 것 |

## 참고 문서

- `API_CONTRACT.md` — Frontend/Backend REST API 계약
- `PROJECT_REQUIREMENTS.md` — 전체 기능 요구사항

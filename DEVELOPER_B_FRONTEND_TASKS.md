# 개발자 B 작업 가이드 — Frontend

## 담당
개발자 B는 **학생이 직접 사용하는 웹앱 Frontend/UI**를 담당한다.

개발자 A는 Backend / AI / 데이터 / RAG를 담당하므로, B는 가능하면 `backend/`, `ai/`, `data/`를 수정하지 않는다.

## 사용 기술
- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui

## 1차 목표
백엔드 완성을 기다리지 말고 Mock JSON으로 화면을 먼저 완성한다. 이후 개발자 A의 REST API로 데이터 소스만 교체한다.

## 담당 화면

### 1. 메인 대시보드
- 학생 기본 정보
- 다음 수업
- 오늘 시간표
- 주요 학교 공지
- 수강신청/상담/AI비서 바로가기
- 다음 강의실 안내 버튼

### 2. AI 비서 채팅
- ChatGPT 형태의 채팅 UI
- 메시지 입력/전송
- 로딩 표시
- AI 답변 표시
- 출처 링크/근거 표시가 가능하도록 컴포넌트 설계
- 추후 `POST /api/chat` 연결

### 3. 수강과목 검색
과목 카드에 다음 정보 표시:
- 과목명
- 교수
- 학점
- 전공/교양 구분
- 온라인/오프라인/혼합
- 요일 및 시간
- 건물/강의실
- 정원/현재 인원
- 신청 가능/마감/폐강 상태
- 마지막 정보 갱신 시간
- 시간표에 넣어보기
- 수강신청 버튼

### 4. 스마트 시간표
- 월~금 주간 시간표
- 신청한 과목 자동 배치
- 과목별 교수/시간/강의실 표시
- 온라인 수업 구분
- 과목 클릭 시 상세정보
- 시간 충돌 표시

### 5. 강의실 안내
- 시간표에서 강의실 선택
- 건물명/층/호수 표시
- MVP에서는 텍스트/지도 이미지 기반 경로 안내
- 예: 현재 위치 → 공학관 → 5층 → 503호

### 6. 상담 화면
- 진로상담/검사 결과 요약 UI
- 지도교수 연결
- 상담사 연결
- 상담 요청 버튼

## Mock Course 데이터 규격
```json
{
  "id": "CS301-01",
  "name": "인공지능 프로그래밍",
  "professor": "김OO",
  "credits": 3,
  "category": "MAJOR_REQUIRED",
  "classType": "OFFLINE",
  "day": "THU",
  "startTime": "13:00",
  "endTime": "15:50",
  "building": "공학관",
  "room": "503",
  "capacity": 30,
  "enrolled": 27,
  "status": "OPEN",
  "lastUpdated": "2026-08-06T14:00:00"
}
```

## 상태값
### classType
- `OFFLINE`
- `ONLINE_LIVE`
- `ONLINE_RECORDED`
- `HYBRID`

### status
- `OPEN`
- `FULL`
- `CANCELLED`
- `UPCOMING`
- `CLOSED`

## 예상 API
- `GET /api/courses`
- `GET /api/courses/:id`
- `GET /api/students/me`
- `GET /api/students/me/courses`
- `GET /api/students/me/schedule`
- `POST /api/enrollment`
- `DELETE /api/enrollment/:id`
- `POST /api/chat`
- `GET /api/notices`
- `GET /api/counseling/me`
- `POST /api/counseling/request`
- `GET /api/buildings`
- `GET /api/rooms/:id`

API가 아직 없으면 같은 응답 형태의 Mock 데이터를 사용한다.

## 작업 영역
주 작업 디렉터리:
```text
frontend/
```

공동 규격이 필요한 경우:
```text
shared/
docs/
```

## 완료 기준
1. 모바일/PC에서 사용할 수 있는 기본 레이아웃
2. 대시보드 동작
3. 과목 검색 및 상태 표시
4. 주간 시간표 렌더링
5. AI 채팅 UI 동작
6. 강의실 안내 화면
7. 상담 화면
8. Mock 데이터를 실제 REST API로 쉽게 교체 가능한 구조

## Claude Code 작업 규칙
- 기존 파일 구조를 먼저 확인한다.
- 개발자 A 담당 디렉터리를 불필요하게 수정하지 않는다.
- TypeScript 타입을 적극 사용한다.
- API 호출 코드를 UI 컴포넌트와 분리한다.
- API가 없어도 Mock 데이터로 실행 가능하게 한다.
- API Key/비밀값을 클라이언트 코드에 넣지 않는다.
- 대규모 리팩터링 전에 변경 범위를 확인한다.
- 작업 단위별로 Git commit이 가능하도록 구현한다.

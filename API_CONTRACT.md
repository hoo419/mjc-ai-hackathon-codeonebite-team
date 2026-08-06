# MJC AI Campus Agent — API Contract v0.1

## 1. 목적
이 문서는 개발자 A(Backend/AI)와 개발자 B(Frontend) 사이의 REST API 계약이다.

Frontend는 이 규격을 기준으로 Mock API를 작성할 수 있으며, Backend가 완성되면 URL/데이터 소스만 교체할 수 있도록 구현한다.

## 2. 공통 규칙

### Base URL
개발 환경 예시:
```text
http://localhost:8000/api
```

Frontend에서는 Base URL을 환경변수로 관리한다.

예:
```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

비밀 API Key는 `NEXT_PUBLIC_` 환경변수에 넣지 않는다.

### Content-Type
```text
application/json
```

### 날짜/시간
ISO 8601 형식을 사용한다.

예:
```text
2026-08-06T14:00:00+09:00
```

### 공통 오류 형식
```json
{
  "error": {
    "code": "COURSE_NOT_FOUND",
    "message": "과목을 찾을 수 없습니다."
  }
}
```

## 3. 공통 Enum

### CourseClassType
```text
OFFLINE
ONLINE_LIVE
ONLINE_RECORDED
HYBRID
```

### CourseStatus
```text
OPEN
FULL
CANCELLED
UPCOMING
CLOSED
```

### CourseCategory
```text
GENERAL_COURSE     // 교양과정
GENERAL_REQUIRED   // 교양필수
GENERAL_ELECTIVE   // 일반선택
MAJOR_COURSE       // 전공과정
INTEGRATED_MAJOR   // 통합전공교과
```

## 4. Course Object
```json
{
  "id": "T00137-101",
  "name": "딥러닝",
  "professor": "윤현구",
  "credits": 3,
  "category": "MAJOR_COURSE",
  "classType": "OFFLINE",
  "sessions": [
    { "day": "TUE", "startTime": "13:25", "endTime": "14:50", "building": null, "room": "공502" },
    { "day": "WED", "startTime": "10:25", "endTime": "11:50", "building": null, "room": "공502" }
  ],
  "targetGrade": 1,
  "eligibleDepts": [{ "code": "1200203", "name": "컴퓨터공학과" }],
  "capacity": 35,
  "enrolled": 30,
  "status": "OPEN",
  "lastUpdated": "2026-08-07T00:00:00+09:00"
}
```

- day/startTime/endTime/building/room 단일 필드는 sessions 배열로 대체됐다
  (한 분반이 여러 요일/시간에 걸칠 수 있어서다). 시간표가 없는 특수 과목은
  sessions: [].
- classType은 근거가 없으면(원격강좌) null이다 — 실시간/녹화를 구분할 방법이
  없어 지어내지 않는다.
- building은 항상 null이다 — 원본이 "공502" 같은 축약 코드라 정식 건물명을
  지어내지 않는다. room은 원본 문자열 그대로.
- eligibleDepts는 이 분반이 열려있는 학과 목록이며 1개 이상일 수 있다
  (여러 학과 공통 개방 분반 존재).

## 5. 과목 API

### GET /courses
과목 목록 조회.

선택 Query 예:
```text
?status=OPEN
?classType=ONLINE_LIVE
?category=GENERAL_ELECTIVE
?search=인공지능
```

Response:
```json
{
  "courses": [
    {
      "id": "T00137-101",
      "name": "딥러닝",
      "professor": "윤현구",
      "credits": 3,
      "category": "MAJOR_COURSE",
      "classType": "OFFLINE",
      "sessions": [
        { "day": "TUE", "startTime": "13:25", "endTime": "14:50", "building": null, "room": "공502" },
        { "day": "WED", "startTime": "10:25", "endTime": "11:50", "building": null, "room": "공502" }
      ],
      "targetGrade": 1,
      "eligibleDepts": [{ "code": "1200203", "name": "컴퓨터공학과" }],
      "capacity": 35,
      "enrolled": 30,
      "status": "OPEN",
      "lastUpdated": "2026-08-07T00:00:00+09:00"
    }
  ]
}
```

### GET /courses/{courseId}
과목 상세조회.

Response:
```json
{
  "course": {
    "id": "T00137-101",
    "name": "딥러닝",
    "professor": "윤현구",
    "credits": 3,
    "category": "MAJOR_COURSE",
    "classType": "OFFLINE",
    "sessions": [
      { "day": "TUE", "startTime": "13:25", "endTime": "14:50", "building": null, "room": "공502" },
      { "day": "WED", "startTime": "10:25", "endTime": "11:50", "building": null, "room": "공502" }
    ],
    "targetGrade": 1,
    "eligibleDepts": [{ "code": "1200203", "name": "컴퓨터공학과" }],
    "capacity": 35,
    "enrolled": 30,
    "status": "OPEN",
    "lastUpdated": "2026-08-07T00:00:00+09:00"
  }
}
```

## 6. Student API

### GET /students/me
현재 학생 정보.

Response:
```json
{
  "student": {
    "id": "mock-student-001",
    "name": "홍길동",
    "department": "컴퓨터공학과",
    "grade": 3,
    "semester": 1
  }
}
```

### PATCH /students/me
학생 프로필(학과/학년/학기) 갱신. 학교 포털 로그인은 학생이 직접 하고,
확인한 값을 우리 앱에 입력하는 방식 — 백엔드는 로그인 자격 증명을 절대
다루지 않는다.

Request:
```json
{
  "department": "컴퓨터공학과",
  "grade": 3,
  "semester": 1
}
```

Response: `GET /students/me`와 동일한 형식.
```json
{
  "student": {
    "id": "mock-student-001",
    "name": "홍길동",
    "department": "컴퓨터공학과",
    "grade": 3,
    "semester": 1
  }
}
```

### GET /students/me/courses
현재 신청 과목.

Response:
```json
{
  "courses": []
}
```

### GET /students/me/schedule
현재 시간표.

Response:
```json
{
  "schedule": [
    {
      "courseId": "T00137-101",
      "name": "딥러닝",
      "professor": "윤현구",
      "classType": "OFFLINE",
      "day": "TUE",
      "startTime": "13:25",
      "endTime": "14:50",
      "building": null,
      "room": "공502"
    }
  ]
}
```

## 7. Enrollment API

**의미 변경**: 실제 수강신청은 학생이 학교 수강신청시스템(sugang.mjc.ac.kr)에서
직접 한다. 이 API는 "신청 시도"가 아니라, **학생이 이미 그 사이트에서 신청을
마친 과목을 우리 시간표 도구에 기록**하는 것이다. 그래서 정원/폐강/자격/
신청기간 검증(`COURSE_FULL`/`COURSE_CANCELLED`/`NOT_ELIGIBLE`/
`ENROLLMENT_CLOSED`)은 더 이상 하지 않는다 - 그건 실제 신청 시점에 이미 끝난
일이다. 우리가 실제로 검증하는 건 `COURSE_NOT_FOUND`(존재하는 과목인지),
`ALREADY_ENROLLED`(중복 기록 방지), `TIME_CONFLICT`(학생이 실수로 겹치는
시간대 두 과목을 신청하지 않았는지 - 실제 신청 사이트가 놓칠 수도 있는
부분이라 우리 쪽 검증이 의미 있다)뿐이다.

### POST /enrollment
이미 실제로 신청 완료한 과목을 내 시간표에 추가.

Request:
```json
{
  "courseId": "CS301-01"
}
```

성공 Response:
```json
{
  "success": true,
  "enrollment": {
    "courseId": "CS301-01",
    "status": "ENROLLED"
  }
}
```

실패 예:
```json
{
  "success": false,
  "error": {
    "code": "COURSE_FULL",
    "message": "수강 정원이 마감되었습니다."
  }
}
```

가능 오류 (문서화 목적으로 전체 유지, 실제로 현재 검증하는 건 위 "의미 변경"
설명대로 `COURSE_NOT_FOUND`/`ALREADY_ENROLLED`/`TIME_CONFLICT` 뿐):
- COURSE_FULL
- COURSE_CANCELLED
- ENROLLMENT_CLOSED
- TIME_CONFLICT
- NOT_ELIGIBLE
- ALREADY_ENROLLED
- COURSE_NOT_FOUND

### DELETE /enrollment/{courseId}
내 시간표에서 과목 제거 (실제 수강취소는 학교 시스템에서 별도로 처리).

Response:
```json
{
  "success": true
}
```

## 8. Chat API

### POST /chat
AI 비서 질문.

Request:
```json
{
  "message": "지금 신청 가능한 온라인 교양 과목 알려줘."
}
```

Response:
```json
{
  "answer": "현재 신청 가능한 온라인 교양 과목을 찾았습니다.",
  "sources": [
    {
      "title": "2026학년도 수강신청 안내",
      "url": "https://example.ac.kr/notice/123"
    }
  ],
  "courses": [
    {
      "id": "GE101-01",
      "name": "디지털 리터러시",
      "professor": "이OO",
      "credits": 3,
      "category": "GENERAL_ELECTIVE",
      "classType": "ONLINE_LIVE",
      "sessions": [
        { "day": "MON", "startTime": "10:00", "endTime": "11:50", "building": null, "room": null }
      ],
      "targetGrade": 1,
      "eligibleDepts": [{ "code": "1200203", "name": "컴퓨터공학과" }],
      "capacity": 40,
      "enrolled": 31,
      "status": "OPEN",
      "lastUpdated": "2026-08-07T00:00:00+09:00"
    }
  ],
  "actions": [
    {
      "type": "VIEW_COURSE",
      "label": "과목 보기",
      "targetId": "GE101-01"
    }
  ]
}
```

Frontend는 `answer`를 반드시 표시하고, `sources`, `courses`, `actions`는 존재할 경우 추가 UI로 표시한다.

## 9. Notice API

### GET /notices
학교/학과 공지.

Response:
```json
{
  "notices": [
    {
      "id": "notice-001",
      "title": "2026학년도 수강신청 안내",
      "category": "ACADEMIC",
      "publishedAt": "2026-08-05T09:00:00+09:00",
      "url": "https://example.ac.kr/notice/001"
    }
  ]
}
```

## 10. Counseling API

### GET /counseling/me
학생에게 공개 가능한 상담/검사 요약.

Response:
```json
{
  "careerSummary": "소프트웨어 개발 직무에 높은 관심을 보입니다.",
  "personalitySummary": "Mock 데이터입니다.",
  "lastCounselingAt": "2026-07-01T15:00:00+09:00"
}
```

### POST /counseling/request
상담 요청.

Request:
```json
{
  "targetType": "ADVISOR",
  "message": "진로 상담을 받고 싶습니다."
}
```

Response:
```json
{
  "success": true,
  "requestId": "counsel-req-001",
  "status": "REQUESTED"
}
```

`targetType`:
```text
ADVISOR
CAREER_COUNSELOR
DEPARTMENT_OFFICE
```

### POST /counseling/analyze-aptitude
`mpu.mjc.ac.kr`(학생역량 이력관리 시스템, SMART CARE)은 로그인이 필수라 백엔드가
대신 접속할 수 없다. 학생이 직접 로그인해서 확인한 진로적성검사/핵심역량검사/
종합심리검사 결과 원문을 이 API에 붙여넣으면 AI가 요약/인사이트를 만들어준다
(`MPU_APTITUDE_ANALYSIS_HANDOFF.md` 참고).

Request:
```json
{
  "rawText": "학생이 mpu.mjc.ac.kr에서 복사해온 검사 결과 원문 (형식 자유)"
}
```

Response:
```json
{
  "summary": "AI가 정리한 한 문단 요약",
  "insights": [
    "핵심 인사이트 1",
    "핵심 인사이트 2"
  ]
}
```

`rawText`에 없는 내용은 추측/생성하지 않는다 (`AI_AGENT_RULES.md`). AI 미설정/
실패 시:
```json
{
  "error": {
    "code": "ANALYSIS_UNAVAILABLE",
    "message": "지금은 분석할 수 없습니다. 잠시 후 다시 시도해 주세요."
  }
}
```

## 11. Building / Room API

### GET /buildings
Response:
```json
{
  "buildings": [
    {
      "id": "engineering",
      "name": "공학관"
    }
  ]
}
```

### GET /rooms/{roomId}
Response:
```json
{
  "room": {
    "id": "engineering-503",
    "building": "공학관",
    "floor": 5,
    "room": "503",
    "directions": [
      "공학관 입구로 이동",
      "엘리베이터를 이용해 5층으로 이동",
      "엘리베이터에서 내려 503호로 이동"
    ]
  }
}
```

## 12. Frontend Mock 규칙
Backend API가 구현되지 않은 경우 Frontend는 이 문서와 동일한 JSON 구조의 Mock 데이터를 사용한다.

Backend가 완성된 뒤에는 컴포넌트를 다시 작성하지 않고 API Client의 데이터 소스만 변경할 수 있도록 한다.

## 13. 계약 변경 규칙
다음 항목을 변경할 경우 A/B가 먼저 합의한다.
- 필드명
- Enum
- Endpoint
- Request 구조
- Response 구조

Claude가 임의로 API 계약을 변경하지 않도록 한다.

변경이 필요하면 먼저 이 문서를 수정하고 양쪽 구현을 맞춘다.

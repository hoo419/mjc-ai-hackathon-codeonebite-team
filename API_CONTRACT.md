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
초기 MVP:
```text
MAJOR_REQUIRED
MAJOR_ELECTIVE
GENERAL_REQUIRED
GENERAL_ELECTIVE
OTHER
```

## 4. Course Object
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
  "lastUpdated": "2026-08-06T14:00:00+09:00"
}
```

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
      "lastUpdated": "2026-08-06T14:00:00+09:00"
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
    "lastUpdated": "2026-08-06T14:00:00+09:00"
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
      "courseId": "CS301-01",
      "name": "인공지능 프로그래밍",
      "professor": "김OO",
      "classType": "OFFLINE",
      "day": "THU",
      "startTime": "13:00",
      "endTime": "15:50",
      "building": "공학관",
      "room": "503"
    }
  ]
}
```

## 7. Enrollment API

### POST /enrollment
수강신청.

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

가능 오류:
- COURSE_FULL
- COURSE_CANCELLED
- ENROLLMENT_CLOSED
- TIME_CONFLICT
- NOT_ELIGIBLE
- ALREADY_ENROLLED
- COURSE_NOT_FOUND

### DELETE /enrollment/{courseId}
Mock 수강취소.

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
      "day": "MON",
      "startTime": "10:00",
      "endTime": "11:50",
      "building": null,
      "room": null,
      "capacity": 40,
      "enrolled": 31,
      "status": "OPEN",
      "lastUpdated": "2026-08-06T14:00:00+09:00"
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

# sugang 실데이터 반영 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `data/courses.json`의 가짜 18개 과목을 sugang.mjc.ac.kr에서 수집한 실제 246개 분반으로 교체하고, `Course` 스키마를 `sessions` 배열 기반으로 바꾸고, `courses` 화면에 실제 사이트처럼 강좌구분/대상학년/학과 필터를 추가한다.

**Architecture:** 원본 스냅샷(`data/raw/sugang_courses_raw_2026_2.json`) → 순수 변환 스크립트(`backend/scripts/transform_sugang_raw.py`) → `data/courses.json`(새 스키마). 백엔드 Pydantic 스키마·SQLAlchemy 모델·서비스 계층(시간충돌/학생 시간표/챗봇 필터)이 새 `sessions` 구조를 쓰도록 순차 수정. 프론트는 타입/라벨/시간표 계산/화면 UI를 같은 스키마에 맞춰 따라간다.

**Tech Stack:** Python 3.14 / FastAPI / Pydantic (backend), TypeScript / Next.js 16 (frontend), pytest, Neon PostgreSQL(JSON 컬럼).

## Global Constraints
- Mock/가짜 데이터로 학교 사실정보를 지어내지 않는다 — 근거 없는 값은 `null`/빈 값으로 남긴다 (예: `classType`이 원격강좌는 항상 `null`, `building`은 항상 `null`).
- API_CONTRACT.md 필드를 바꿀 땐 그 문서부터 고치고, 코드가 그 문서를 그대로 따른다.
- `backend/.env`/`frontend/.env.local`, 실제 비밀값은 절대 커밋하지 않는다 (이 계획에서는 건드리지 않음).
- TDD: 테스트 먼저 작성해 실패를 확인한 뒤 구현한다. 매 태스크 끝에 커밋한다.
- 브랜치: `feature/course-data-real` (이미 생성/체크아웃됨).

---

### Task 1: API_CONTRACT.md — Course 스키마 문서 갱신

**Files:**
- Modify: `API_CONTRACT.md` (섹션 3 CourseCategory, 섹션 4 Course Object, 섹션 5 예시들, 섹션 6 GET /students/me/schedule 예시, 섹션 8 Chat 예시)

**Interfaces:**
- Produces: 이후 모든 백엔드/프론트 태스크가 참조하는 "정답" 스키마 정의.

- [ ] **Step 1: CourseCategory 섹션 교체**

`API_CONTRACT.md`의 `### CourseCategory` 블록을:
```text
GENERAL_COURSE     // 교양과정
GENERAL_REQUIRED   // 교양필수
GENERAL_ELECTIVE   // 일반선택
MAJOR_COURSE       // 전공과정
INTEGRATED_MAJOR   // 통합전공교과
```
로 교체한다 (기존 `MAJOR_REQUIRED`/`MAJOR_ELECTIVE`/`OTHER` 제거).

- [ ] **Step 2: Course Object 섹션(4번) 교체**

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
바로 아래에 설명 추가:
```text
- day/startTime/endTime/building/room 단일 필드는 sessions 배열로 대체됐다
  (한 분반이 여러 요일/시간에 걸칠 수 있어서다). 시간표가 없는 특수 과목은
  sessions: [].
- classType은 근거가 없으면(원격강좌) null이다 — 실시간/녹화를 구분할 방법이
  없어 지어내지 않는다.
- building은 항상 null이다 — 원본이 "공502" 같은 축약 코드라 정식 건물명을
  지어내지 않는다. room은 원본 문자열 그대로.
- eligibleDepts는 이 분반이 열려있는 학과 목록이며 1개 이상일 수 있다
  (여러 학과 공통 개방 분반 존재).
```

- [ ] **Step 3: 섹션 5(GET /courses 예시), 섹션 6(GET /students/me/schedule 예시), 섹션 8(Chat 예시)의 Course/schedule JSON 예시를 Step 2와 같은 구조로 갱신**

`GET /students/me/schedule`의 schedule 항목은 여전히 세션 1개=엔트리 1개 형태(day/startTime/endTime/building/room 단일 필드, Course와 달리 이건 "이미 펼쳐진" 투영이라 바뀌지 않음)이므로, 예시의 `courseId`/`name`만 실제스러운 값으로 바꾸고 구조는 유지한다:
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
Chat 예시(섹션 8)의 `courses` 배열 항목도 Step 2 Course 구조로 교체.

- [ ] **Step 4: 커밋**

```bash
git add API_CONTRACT.md
git commit -m "docs: Course 스키마를 sessions 배열 기반으로 갱신 (API_CONTRACT)"
```

---

### Task 2: 백엔드 스키마 — Session/Course/CourseCategory

**Files:**
- Modify: `backend/app/schemas/course.py`
- Modify: `backend/app/schemas/student.py:34-47` (ScheduleItem.classType를 nullable로)
- Test: `backend/tests/test_course_schema.py` (신규)

**Interfaces:**
- Produces: `Session` pydantic 모델(`day`, `startTime`, `endTime`, `building`, `room`), `Course.sessions: list[Session]`, `Course.targetGrade: int`, `Course.eligibleDepts: list[EligibleDept]`, `Course.classType: CourseClassType | None`, `CourseCategory` 5종.

- [ ] **Step 1: 실패하는 스키마 테스트 작성**

`backend/tests/test_course_schema.py`:
```python
from app.schemas.course import Course


def test_course_accepts_sessions_array_and_new_category():
    course = Course.model_validate(
        {
            "id": "T00137-101",
            "name": "딥러닝",
            "professor": "윤현구",
            "credits": 3,
            "category": "MAJOR_COURSE",
            "classType": "OFFLINE",
            "sessions": [
                {"day": "TUE", "startTime": "13:25", "endTime": "14:50", "building": None, "room": "공502"},
                {"day": "WED", "startTime": "10:25", "endTime": "11:50", "building": None, "room": "공502"},
            ],
            "targetGrade": 1,
            "eligibleDepts": [{"code": "1200203", "name": "컴퓨터공학과"}],
            "capacity": 35,
            "enrolled": 30,
            "status": "OPEN",
            "lastUpdated": "2026-08-07T00:00:00+09:00",
        }
    )

    assert len(course.sessions) == 2
    assert course.sessions[0].day == "TUE"
    assert course.eligibleDepts[0].name == "컴퓨터공학과"
    assert course.targetGrade == 1


def test_course_classtype_can_be_null_for_remote_courses():
    course = Course.model_validate(
        {
            "id": "T00138-101",
            "name": "AI활용웹개발",
            "professor": "정지영",
            "credits": 2,
            "category": "INTEGRATED_MAJOR",
            "classType": None,
            "sessions": [],
            "targetGrade": 1,
            "eligibleDepts": [{"code": "1201301", "name": "통합전공"}],
            "capacity": 30,
            "enrolled": 0,
            "status": "OPEN",
            "lastUpdated": "2026-08-07T00:00:00+09:00",
        }
    )

    assert course.classType is None
    assert course.sessions == []
```

- [ ] **Step 2: 실패 확인**

Run: `cd backend && python -m pytest tests/test_course_schema.py -v`
Expected: FAIL — `Course`에 `sessions`/`targetGrade`/`eligibleDepts` 필드가 없거나 `category`/`day` 등 필수 필드 검증 오류로 실패.

- [ ] **Step 3: `backend/app/schemas/course.py` 재작성**

```python
from enum import StrEnum

from pydantic import BaseModel


class CourseClassType(StrEnum):
    OFFLINE = "OFFLINE"
    ONLINE_LIVE = "ONLINE_LIVE"
    ONLINE_RECORDED = "ONLINE_RECORDED"
    HYBRID = "HYBRID"


class CourseStatus(StrEnum):
    OPEN = "OPEN"
    FULL = "FULL"
    CANCELLED = "CANCELLED"
    UPCOMING = "UPCOMING"
    CLOSED = "CLOSED"


class CourseCategory(StrEnum):
    GENERAL_COURSE = "GENERAL_COURSE"
    GENERAL_REQUIRED = "GENERAL_REQUIRED"
    GENERAL_ELECTIVE = "GENERAL_ELECTIVE"
    MAJOR_COURSE = "MAJOR_COURSE"
    INTEGRATED_MAJOR = "INTEGRATED_MAJOR"


class Session(BaseModel):
    """한 분반의 요일별 시간 하나. 한 분반이 여러 요일에 걸치면 Course.sessions에
    여러 개 들어간다."""

    day: str
    startTime: str
    endTime: str
    building: str | None
    room: str | None


class EligibleDept(BaseModel):
    code: str
    name: str


class Course(BaseModel):
    """Mirrors the Course object in API_CONTRACT.md section 4. Field names
    and shape must stay in lockstep with that document."""

    id: str
    name: str
    professor: str
    credits: int
    category: CourseCategory
    classType: CourseClassType | None
    sessions: list[Session]
    targetGrade: int
    eligibleDepts: list[EligibleDept]
    capacity: int
    enrolled: int
    status: CourseStatus
    lastUpdated: str


class CourseListResponse(BaseModel):
    courses: list[Course]


class CourseDetailResponse(BaseModel):
    course: Course
```

- [ ] **Step 4: `backend/app/schemas/student.py`의 `ScheduleItem.classType`를 nullable로**

`backend/app/schemas/student.py:42` 줄을:
```python
    classType: CourseClassType | None
```
로 변경 (Course.classType이 null일 수 있으니 그걸 그대로 투영하는 ScheduleItem도 null 허용해야 함).

- [ ] **Step 5: 통과 확인**

Run: `cd backend && python -m pytest tests/test_course_schema.py -v`
Expected: PASS (2 passed)

- [ ] **Step 6: 전체 스위트 실행 — 이 시점엔 아직 `data/courses.json`이 옛 스키마라 대량 실패가 정상**

Run: `cd backend && python -m pytest -q`
Expected: 다수 FAIL (courses.json이 아직 옛 필드라 `Course.model_validate` 자체가 깨짐) — Task 4에서 데이터를 교체하면 해소된다. 지금은 실패 이유가 "필드 누락/구식 스키마"인지만 확인하고 넘어간다.

- [ ] **Step 7: 커밋**

```bash
git add backend/app/schemas/course.py backend/app/schemas/student.py backend/tests/test_course_schema.py
git commit -m "feat: Course 스키마를 sessions 배열 + 신규 CourseCategory로 교체"
```

---

### Task 3: 변환 스크립트 — 원본 → Course JSON

**Files:**
- Create: `backend/scripts/__init__.py` (빈 파일, 패키지화)
- Create: `backend/scripts/transform_sugang_raw.py`
- Test: `backend/tests/test_transform_sugang_raw.py`

**Interfaces:**
- Consumes: `Session`/`Course`/`CourseCategory` (Task 2).
- Produces: `transform_sugang_raw.parse_sessions(time: str) -> list[dict]`, `transform_sugang_raw.transform_row(row: dict) -> dict` (한 원본 row → Course dict), `transform_sugang_raw.main()` (파일 전체 변환 + `data/courses.json` 저장).

- [ ] **Step 1: 실패하는 테스트 작성**

`backend/tests/test_transform_sugang_raw.py`:
```python
from backend.scripts.transform_sugang_raw import parse_sessions, transform_row

RAW_MULTI_SESSION = {
    "subjectCd": "T00137",
    "bunban": "101",
    "subjectNmKor": "딥러닝",
    "nm": "윤현구",
    "credit": "3",
    "isuCdNm": "전공과정",
    "time": "화 13:25 - 14:50 ( 공502 ) <br> 수 10:25 - 11:50 ( 공502 )",
    "limitNum": "35",
    "inManNum": "30",
    "sugangGbnCodes": ["30"],
    "targetGrades": ["1"],
    "depts": [{"code": "1200203", "name": "컴퓨터공학과"}],
}

RAW_REMOTE_NO_SESSION = {
    "subjectCd": "T00140",
    "bunban": "104",
    "subjectNmKor": "진로설정동행세미나",
    "nm": "박준성",
    "credit": "1",
    "isuCdNm": "통합전공교과",
    "time": " ",
    "limitNum": "20",
    "inManNum": "20",
    "sugangGbnCodes": ["60"],
    "targetGrades": ["1"],
    "depts": [{"code": "1201301", "name": "통합전공"}],
}

RAW_MULTI_DEPT = {
    "subjectCd": "T00039",
    "bunban": "101",
    "subjectNmKor": "창업실습2",
    "nm": "김창업",
    "credit": "3",
    "isuCdNm": "통합전공교과",
    "time": "수 10:00 - 10:50 ( 예119 )",
    "limitNum": "15",
    "inManNum": "0",
    "sugangGbnCodes": ["30"],
    "targetGrades": ["2"],
    "depts": [
        {"code": "1201301", "name": "통합전공"},
        {"code": "1200301", "name": "경영학과"},
    ],
}


def test_parse_sessions_splits_multiple_br_separated_slots():
    sessions = parse_sessions("화 13:25 - 14:50 ( 공502 ) <br> 수 10:25 - 11:50 ( 공502 )")

    assert sessions == [
        {"day": "TUE", "startTime": "13:25", "endTime": "14:50", "building": None, "room": "공502"},
        {"day": "WED", "startTime": "10:25", "endTime": "11:50", "building": None, "room": "공502"},
    ]


def test_parse_sessions_blank_string_returns_empty_list():
    assert parse_sessions(" ") == []


def test_transform_row_maps_category_and_grade_and_dept():
    course = transform_row(RAW_MULTI_SESSION)

    assert course["id"] == "T00137-101"
    assert course["category"] == "MAJOR_COURSE"
    assert course["classType"] == "OFFLINE"
    assert course["targetGrade"] == 1
    assert course["eligibleDepts"] == [{"code": "1200203", "name": "컴퓨터공학과"}]
    assert course["capacity"] == 35
    assert course["enrolled"] == 30
    assert course["status"] == "OPEN"
    assert len(course["sessions"]) == 2


def test_transform_row_remote_course_has_null_classtype_and_empty_sessions():
    course = transform_row(RAW_REMOTE_NO_SESSION)

    assert course["classType"] is None
    assert course["sessions"] == []
    assert course["category"] == "INTEGRATED_MAJOR"
    assert course["status"] == "FULL"  # enrolled(20) >= capacity(20)


def test_transform_row_keeps_all_eligible_depts():
    course = transform_row(RAW_MULTI_DEPT)

    assert len(course["eligibleDepts"]) == 2
    assert {d["name"] for d in course["eligibleDepts"]} == {"통합전공", "경영학과"}
```

- [ ] **Step 2: 실패 확인**

Run: `cd backend && python -m pytest tests/test_transform_sugang_raw.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'backend.scripts.transform_sugang_raw'`

- [ ] **Step 3: `backend/scripts/__init__.py` 빈 파일 생성, `backend/scripts/transform_sugang_raw.py` 작성**

```python
"""원본 sugang 스냅샷(data/raw/sugang_courses_raw_2026_2.json)을
data/courses.json(Course 스키마)으로 변환하는 1회성 스크립트.
재수집 시 다시 실행해서 data/courses.json을 갱신할 수 있도록 리포에 남겨둔다."""

import json
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = REPO_ROOT / "data" / "raw" / "sugang_courses_raw_2026_2.json"
OUT_PATH = REPO_ROOT / "data" / "courses.json"

DAY_MAP = {
    "월": "MON", "화": "TUE", "수": "WED", "목": "THU",
    "금": "FRI", "토": "SAT", "일": "SUN",
}

CATEGORY_MAP = {
    "교양과정": "GENERAL_COURSE",
    "교양필수": "GENERAL_REQUIRED",
    "일반선택": "GENERAL_ELECTIVE",
    "전공과정": "MAJOR_COURSE",
    "통합전공교과": "INTEGRATED_MAJOR",
}

import re

_SESSION_RE = re.compile(r"^([월화수목금토일])\s+(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})\s*\(\s*(.+?)\s*\)$")


def parse_sessions(time_str: str) -> list[dict]:
    """"화 13:25 - 14:50 ( 공502 ) <br> 수 10:25 - 11:50 ( 공502 )" 같은 원본
    time 문자열을 세션 dict 리스트로 쪼갠다. 빈/공백 문자열은 세션 없음."""
    if not time_str or not time_str.strip():
        return []

    sessions = []
    for segment in time_str.split("<br>"):
        segment = segment.strip()
        if not segment:
            continue
        match = _SESSION_RE.match(segment)
        if match is None:
            raise ValueError(f"세션 문자열을 파싱하지 못함: {segment!r}")
        day_kr, start, end, room = match.groups()
        sessions.append(
            {
                "day": DAY_MAP[day_kr],
                "startTime": start,
                "endTime": end,
                "building": None,
                "room": room,
            }
        )
    return sessions


def transform_row(row: dict) -> dict:
    capacity = int(row["limitNum"])
    enrolled = int(row["inManNum"])
    is_remote = row["sugangGbnCodes"][0] == "60"

    return {
        "id": f"{row['subjectCd']}-{row['bunban']}",
        "name": row["subjectNmKor"],
        "professor": row["nm"],
        "credits": int(row["credit"]),
        "category": CATEGORY_MAP[row["isuCdNm"]],
        "classType": None if is_remote else "OFFLINE",
        "sessions": parse_sessions(row["time"]),
        "targetGrade": int(row["targetGrades"][0]),
        "eligibleDepts": row["depts"],
        "capacity": capacity,
        "enrolled": enrolled,
        "status": "FULL" if enrolled >= capacity else "OPEN",
        "lastUpdated": datetime.now().astimezone().isoformat(timespec="seconds"),
    }


def main() -> None:
    raw_rows = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    courses = [transform_row(row) for row in raw_rows]
    OUT_PATH.write_text(
        json.dumps(courses, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"wrote {len(courses)} courses to {OUT_PATH}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 통과 확인**

Run: `cd backend && python -m pytest tests/test_transform_sugang_raw.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: 커밋**

```bash
git add backend/scripts backend/tests/test_transform_sugang_raw.py
git commit -m "feat: sugang 원본 -> Course JSON 변환 스크립트 추가"
```

---

### Task 4: 실데이터로 `data/courses.json` 교체 + 의존 Mock 픽스처 재구성

**Files:**
- Modify (generated): `data/courses.json` (스크립트로 덮어씀)
- Modify: `data/enrollments.json`

**Interfaces:**
- Consumes: `transform_sugang_raw.main()` (Task 3).
- Produces: 이후 모든 백엔드/프론트 태스크가 실제로 읽는 246개 Course 레코드. 아래 4개 ID를 이후 태스크에서 재사용한다:
  - `T00138-101` ("AI활용웹개발", FRI 11:00-11:50, classType=null, status=OPEN) — 시나리오 A
  - `J01683-101` ("세무신고실무", TUE 09:25-10:25, status=OPEN) — 시나리오 B (A와 시간 안 겹침)
  - `J00105-101` ("경영정보시스템" 101분반, FRI 10:00/11:00/12:00 세 세션, 그중 FRI 11:00-11:50가 A와 겹침) — 시나리오 C (시간충돌용)
  - `J00105-102` ("경영정보시스템" 102분반, WED 14:00/15:00/16:00) — 시나리오 D (A/B 둘 다와 안 겹침, 단순 신청 성공용)
  - `J00936-101` ("마이크로콘트롤러프로그래밍", capacity 30 = enrolled 30) — FULL 상태 실례

- [ ] **Step 1: 변환 스크립트 실행**

Run: `cd backend && python -m scripts.transform_sugang_raw`
Expected: `wrote 246 courses to .../data/courses.json`

- [ ] **Step 2: 결과 검증**

Run:
```bash
python -c "
import json
courses = json.load(open('data/courses.json', encoding='utf-8'))
print('total', len(courses))
print('full', sum(1 for c in courses if c['status']=='FULL'))
ids = {c['id'] for c in courses}
for want in ['T00138-101','J01683-101','J00105-101','J00105-102','J00936-101']:
    assert want in ids, want
print('all fixture ids present')
"
```
Expected: `total 246`, `full 36`, `all fixture ids present`.

- [ ] **Step 3: `data/enrollments.json`을 실제 ID로 교체**

`mock-student-001`이 A(`T00138-101`)와 B(`J01683-101`)를 신청한 걸로 바꾼다 (둘은 요일이 달라 충돌 없음):
```json
[
  {
    "studentId": "mock-student-001",
    "courseId": "T00138-101",
    "status": "ENROLLED",
    "enrolledAt": "2026-08-01T10:00:00+09:00"
  },
  {
    "studentId": "mock-student-001",
    "courseId": "J01683-101",
    "status": "ENROLLED",
    "enrolledAt": "2026-08-01T10:05:00+09:00"
  }
]
```

- [ ] **Step 4: 커밋**

```bash
git add data/courses.json data/enrollments.json
git commit -m "feat: data/courses.json을 sugang 실데이터 246개 분반으로 교체"
```

---

### Task 5: `CourseModel`(DB) + repository — sessions JSON 컬럼

**Files:**
- Modify: `backend/app/models/course.py`
- Modify: `backend/app/repositories/course_repository.py:22-53`
- Modify: `backend/app/core/seed.py:28-47`

**Interfaces:**
- Consumes: `Session`/`EligibleDept`(Task 2), `data/courses.json`(Task 4).
- Produces: `CourseModel.sessions`/`eligible_depts`가 JSON 직렬화된 문자열 컬럼으로 저장/복원됨. `course_repository.list_courses()`/`get_course()`가 Mock/DB 양쪽에서 새 스키마의 `Course`를 반환.

- [ ] **Step 1: `backend/app/models/course.py` 수정**

```python
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class CourseModel(Base):
    """Mirrors the Course object in API_CONTRACT.md section 4. sessions/
    eligible_depts are stored as JSON-serialized text (Neon supports JSONB,
    but plain String keeps the Mock/DB code paths symmetric - the
    repository layer is the only place that (de)serializes)."""

    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    professor: Mapped[str] = mapped_column(String)
    credits: Mapped[int] = mapped_column(Integer)
    category: Mapped[str] = mapped_column(String)
    class_type: Mapped[str | None] = mapped_column(String, nullable=True)
    sessions_json: Mapped[str] = mapped_column(String)
    target_grade: Mapped[int] = mapped_column(Integer)
    eligible_depts_json: Mapped[str] = mapped_column(String)
    capacity: Mapped[int] = mapped_column(Integer)
    enrolled: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String)
    last_updated: Mapped[str] = mapped_column(String)
```

- [ ] **Step 2: `backend/app/repositories/course_repository.py`의 `_model_to_schema` 수정**

`backend/app/repositories/course_repository.py:36-53`을:
```python
def _model_to_schema(row: CourseModel) -> Course:
    return Course(
        id=row.id,
        name=row.name,
        professor=row.professor,
        credits=row.credits,
        category=row.category,
        classType=row.class_type,
        sessions=json.loads(row.sessions_json),
        targetGrade=row.target_grade,
        eligibleDepts=json.loads(row.eligible_depts_json),
        capacity=row.capacity,
        enrolled=row.enrolled,
        status=row.status,
        lastUpdated=row.last_updated,
    )
```
로 교체 (파일 상단에 이미 `import json`이 없다면 추가).

- [ ] **Step 3: `backend/app/core/seed.py`의 CourseModel 생성부 수정**

`backend/app/core/seed.py:28-47`을:
```python
        for item in _load_json("courses.json"):
            session.add(
                CourseModel(
                    id=item["id"],
                    name=item["name"],
                    professor=item["professor"],
                    credits=item["credits"],
                    category=item["category"],
                    class_type=item["classType"],
                    sessions_json=json.dumps(item["sessions"], ensure_ascii=False),
                    target_grade=item["targetGrade"],
                    eligible_depts_json=json.dumps(item["eligibleDepts"], ensure_ascii=False),
                    capacity=item["capacity"],
                    enrolled=item["enrolled"],
                    status=item["status"],
                    last_updated=item["lastUpdated"],
                )
            )
```
로 교체.

- [ ] **Step 4: DB 모드 테스트 확인 (있다면)**

Run: `cd backend && python -m pytest tests/test_db_repositories.py -v` (파일이 있을 때만; `DATABASE_URL` 없으면 스킵되는지 확인)
Expected: PASS 또는 SKIP (DB 미설정 환경에서는 skip이 정상).

- [ ] **Step 5: Mock 모드 리포지토리 테스트 실행 (아직 옛 하드코딩 ID라 실패 예상 — Task 6에서 고침)**

Run: `cd backend && python -m pytest tests/test_course_repository.py -v`
Expected: FAIL (`CS350-01` 등 존재하지 않는 ID) — 정상, Task 6에서 해결.

- [ ] **Step 6: 커밋**

```bash
git add backend/app/models/course.py backend/app/repositories/course_repository.py backend/app/core/seed.py
git commit -m "feat: CourseModel/시드/리포지토리를 sessions JSON 컬럼 기반으로 갱신"
```

---

### Task 6: `test_course_repository.py` — 실제 데이터 기반으로 재작성

**Files:**
- Modify: `backend/tests/test_course_repository.py`

**Interfaces:**
- Consumes: `course_repository.list_courses/get_course/increment_enrolled/decrement_enrolled` (변경 없음, Task 5까지 완료).

- [ ] **Step 1: 특정 mock ID에 의존하지 않는 범용 테스트로 재작성**

```python
from app.repositories import course_repository


def test_increment_enrolled_flips_status_to_full_at_capacity():
    # Pick the OPEN course closest to capacity so the loop below stays short
    # regardless of how big real capacities are (some run to 200+ seats).
    open_courses = [c for c in course_repository.list_courses() if c.status == "OPEN"]
    course = min(open_courses, key=lambda c: c.capacity - c.enrolled)

    for _ in range(course.capacity - course.enrolled):
        course_repository.increment_enrolled(course.id)

    updated = course_repository.get_course(course.id)
    assert updated.enrolled == updated.capacity
    assert updated.status == "FULL"


def test_decrement_enrolled_reverts_full_status_to_open():
    course = next(c for c in course_repository.list_courses() if c.status == "FULL")

    course_repository.decrement_enrolled(course.id)

    updated = course_repository.get_course(course.id)
    assert updated.enrolled == course.enrolled - 1
    assert updated.status == "OPEN"


def test_decrement_enrolled_never_goes_below_zero():
    course = next(c for c in course_repository.list_courses() if c.enrolled == 0)

    for _ in range(3):
        course_repository.decrement_enrolled(course.id)

    updated = course_repository.get_course(course.id)
    assert updated.enrolled == 0
```
(이전엔 `CS350-01`/`CS301-02`/`CS360-01` 같은 하드코딩 Mock ID에 의존했는데, 실데이터로 바뀌면서 그 ID들이 더 이상 없다 — 앞으로 데이터가 다시 갱신돼도 깨지지 않도록 "OPEN인 아무 과목"/"FULL인 아무 과목"/"enrolled=0인 아무 과목"을 런타임에 찾는 방식으로 바꿨다. `enrolled=0`인 과목이 실제로 존재하는지는 Task 4 Step 2에서 이미 여러 개 확인됨.)

- [ ] **Step 2: 통과 확인**

Run: `cd backend && python -m pytest tests/test_course_repository.py -v`
Expected: PASS (3 passed)

- [ ] **Step 3: 커밋**

```bash
git add backend/tests/test_course_repository.py
git commit -m "test: course_repository 테스트를 실데이터에 안 깨지는 범용 형태로 재작성"
```

---

### Task 7: `test_courses.py` — 실데이터 기준으로 재작성

**Files:**
- Modify: `backend/tests/test_courses.py`

- [ ] **Step 1: 필드셋/검색/상세조회 테스트를 새 스키마 + 실제 ID로 재작성**

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_courses_returns_all_mock_courses():
    response = client.get("/api/courses")

    assert response.status_code == 200
    body = response.json()
    assert "courses" in body
    assert len(body["courses"]) == 246
    first = body["courses"][0]
    assert set(first.keys()) == {
        "id",
        "name",
        "professor",
        "credits",
        "category",
        "classType",
        "sessions",
        "targetGrade",
        "eligibleDepts",
        "capacity",
        "enrolled",
        "status",
        "lastUpdated",
    }


def test_list_courses_filters_by_status():
    response = client.get("/api/courses", params={"status": "FULL"})

    assert response.status_code == 200
    courses = response.json()["courses"]
    assert len(courses) >= 1
    assert all(course["status"] == "FULL" for course in courses)


def test_list_courses_filters_by_category():
    response = client.get("/api/courses", params={"category": "MAJOR_COURSE"})

    assert response.status_code == 200
    courses = response.json()["courses"]
    assert len(courses) >= 1
    assert all(course["category"] == "MAJOR_COURSE" for course in courses)


def test_list_courses_search_matches_course_name():
    response = client.get("/api/courses", params={"search": "AI활용웹개발"})

    assert response.status_code == 200
    courses = response.json()["courses"]
    assert len(courses) >= 1
    assert all("AI활용웹개발" in course["name"] for course in courses)


def test_get_course_by_id_returns_course_detail():
    response = client.get("/api/courses/T00138-101")

    assert response.status_code == 200
    course = response.json()["course"]
    assert course["id"] == "T00138-101"
    assert course["name"] == "AI활용웹개발"


def test_get_course_by_id_returns_404_with_contract_error_shape():
    response = client.get("/api/courses/NOT-EXIST-01")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "COURSE_NOT_FOUND"
    assert "message" in body["error"]
```

주의: `test_list_courses_filters_by_class_type`(옛 `ONLINE_LIVE` 필터 테스트)은 삭제한다 — 실데이터엔 `classType`이 `OFFLINE` 또는 `null`만 존재하고 `ONLINE_LIVE`로 확정할 근거가 없어서, 이 필터가 실제로 매치할 데이터가 없다. classType 필터 자체(쿼리 파라미터)는 유지하되(Enum 값 자체는 그대로 정의돼 있으니 API가 거부하진 않음), "지어낸 값이 실제로 매치되는 걸 테스트로 못박지 않는다"는 원칙에 따라 이 테스트만 제거한다.

- [ ] **Step 2: 통과 확인**

Run: `cd backend && python -m pytest tests/test_courses.py -v`
Expected: PASS (5 passed)

- [ ] **Step 3: 커밋**

```bash
git add backend/tests/test_courses.py
git commit -m "test: test_courses를 sessions 스키마 + 실제 과목 ID 기준으로 재작성"
```

---

### Task 8: `enrollment_service` — 세션 배열 기준 시간충돌 검사

**Files:**
- Modify: `backend/app/services/enrollment_service.py:25-34`
- Modify: `backend/tests/test_enrollment.py`

**Interfaces:**
- Consumes: `Course.sessions: list[Session]` (Task 2).
- Produces: `_has_time_conflict(existing_courses: list[Course], candidate: Course) -> bool` — 시그니처는 그대로, 내부 로직만 세션 쌍 비교로 확장.

- [ ] **Step 1: `_has_time_conflict` 재작성**

`backend/app/services/enrollment_service.py:25-34`를:
```python
def _has_time_conflict(existing_courses: list[Course], candidate: Course) -> bool:
    """AI_AGENT_RULES.md 시간표 규칙: 두 세션이 같은 요일이고
    new_start < existing_end AND new_end > existing_start 이면 충돌.
    한 분반이 여러 세션을 가질 수 있으므로, 기존 과목들의 모든 세션과
    후보 과목의 모든 세션을 한 쌍씩 비교한다."""
    for existing in existing_courses:
        for existing_session in existing.sessions:
            for candidate_session in candidate.sessions:
                if existing_session.day != candidate_session.day:
                    continue
                if (
                    candidate_session.startTime < existing_session.endTime
                    and candidate_session.endTime > existing_session.startTime
                ):
                    return True
    return False
```

- [ ] **Step 2: `test_enrollment.py`를 실제 ID/시나리오로 재작성**

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# mock-student-001은 data/enrollments.json 기준으로 이미
# T00138-101(FRI 11:00-11:50)와 J01683-101(TUE 09:25-10:25)을 신청한 상태.


def test_enroll_open_course_with_no_conflict_succeeds():
    # J00105-102: WED 14:00/15:00/16:00 - 기존 두 과목과 요일이 안 겹침.
    response = client.post("/api/enrollment", json={"courseId": "J00105-102"})

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "success": True,
        "enrollment": {"courseId": "J00105-102", "status": "ENROLLED"},
    }


def test_enroll_already_enrolled_course_returns_error():
    response = client.post("/api/enrollment", json={"courseId": "T00138-101"})

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "ALREADY_ENROLLED"


def test_enroll_time_conflicting_course_returns_error():
    # J00105-101은 FRI 11:00-11:50 세션을 포함 - T00138-101(FRI 11:00-11:50)과 겹침.
    response = client.post("/api/enrollment", json={"courseId": "J00105-101"})

    assert response.json()["error"]["code"] == "TIME_CONFLICT"


def test_enroll_nonexistent_course_returns_error():
    response = client.post("/api/enrollment", json={"courseId": "NOPE-01"})

    assert response.json()["error"]["code"] == "COURSE_NOT_FOUND"


def test_enroll_then_appears_in_student_courses():
    client.post("/api/enrollment", json={"courseId": "J00105-102"})

    response = client.get("/api/students/me/courses")

    course_ids = {c["id"] for c in response.json()["courses"]}
    assert "J00105-102" in course_ids


def test_enroll_full_course_no_longer_blocked():
    """수강신청은 실제로는 학생이 sugang.mjc.ac.kr에서 이미 완료한 것을
    우리 시간표에 기록하는 것뿐이라, 정원 검증은 더 이상 우리 쪽에서 하지
    않는다. J00936-101은 capacity=enrolled=30(FULL)이지만 신청 기록은
    성공해야 한다. (CANCELLED/UPCOMING 시나리오는 실데이터에 그 상태가
    존재하지 않아 검증하지 않는다 - 지어내지 않는다는 원칙.)"""
    response = client.post("/api/enrollment", json={"courseId": "J00936-101"})

    assert response.json()["success"] is True


def test_delete_enrollment_returns_success_and_removes_course():
    response = client.delete("/api/enrollment/T00138-101")

    assert response.status_code == 200
    assert response.json() == {"success": True}

    remaining = client.get("/api/students/me/courses").json()["courses"]
    assert "T00138-101" not in {c["id"] for c in remaining}


def test_delete_enrollment_for_unenrolled_course_is_idempotent():
    response = client.delete("/api/enrollment/J00105-102")

    assert response.status_code == 200
    assert response.json() == {"success": True}
```

- [ ] **Step 3: 통과 확인**

Run: `cd backend && python -m pytest tests/test_enrollment.py -v`
Expected: PASS (8 passed)

- [ ] **Step 4: 커밋**

```bash
git add backend/app/services/enrollment_service.py backend/tests/test_enrollment.py
git commit -m "feat: 시간충돌 검사를 세션 배열 쌍 비교로 확장, 테스트를 실데이터로 재작성"
```

---

### Task 9: `student_service` — 세션별로 펼친 시간표

**Files:**
- Modify: `backend/app/services/student_service.py:33-48`
- Modify: `backend/tests/test_students.py`

**Interfaces:**
- Produces: `get_current_student_schedule() -> list[ScheduleItem]` — 한 과목이 세션 N개면 ScheduleItem N개를 만든다 (courseId는 공유).

- [ ] **Step 1: `get_current_student_schedule` 재작성**

`backend/app/services/student_service.py:33-48`을:
```python
def get_current_student_schedule() -> list[ScheduleItem]:
    """한 과목이 여러 세션(요일)을 가지면, 세션마다 하나씩 ScheduleItem을
    만든다 - 시간표 화면은 "언제 어디서 무슨 수업"인지 슬롯 단위로 봐야
    하기 때문이다."""
    courses = get_current_student_courses()
    return [
        ScheduleItem(
            courseId=course.id,
            name=course.name,
            professor=course.professor,
            classType=course.classType,
            day=session.day,
            startTime=session.startTime,
            endTime=session.endTime,
            building=session.building,
            room=session.room,
        )
        for course in courses
        for session in course.sessions
    ]
```

- [ ] **Step 2: `test_students.py`를 실제 ID로 재작성**

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_current_student_returns_mock_student():
    response = client.get("/api/students/me")

    assert response.status_code == 200
    student = response.json()["student"]
    assert student == {
        "id": "mock-student-001",
        "name": "홍길동",
        "department": "컴퓨터공학과",
        "grade": 3,
        "semester": 1,
    }


def test_get_current_student_courses_returns_enrolled_courses_only():
    response = client.get("/api/students/me/courses")

    assert response.status_code == 200
    courses = response.json()["courses"]
    course_ids = {c["id"] for c in courses}
    assert course_ids == {"T00138-101", "J01683-101"}
    assert "status" in courses[0]
    assert "capacity" in courses[0]


def test_patch_current_student_updates_profile_and_persists():
    response = client.patch(
        "/api/students/me",
        json={"department": "소프트웨어학과", "grade": 2, "semester": 2},
    )

    assert response.status_code == 200
    assert response.json() == {
        "student": {
            "id": "mock-student-001",
            "name": "홍길동",
            "department": "소프트웨어학과",
            "grade": 2,
            "semester": 2,
        }
    }

    follow_up = client.get("/api/students/me")
    assert follow_up.json()["student"]["department"] == "소프트웨어학과"
    assert follow_up.json()["student"]["grade"] == 2
    assert follow_up.json()["student"]["semester"] == 2


def test_get_current_student_schedule_returns_one_item_per_session():
    response = client.get("/api/students/me/schedule")

    assert response.status_code == 200
    schedule = response.json()["schedule"]
    # T00138-101은 세션 1개(FRI 11:00-11:50), J01683-101도 세션 1개(TUE 09:25-10:25).
    assert len(schedule) == 2
    item = next(s for s in schedule if s["courseId"] == "T00138-101")
    assert item == {
        "courseId": "T00138-101",
        "name": "AI활용웹개발",
        "professor": "정필성",
        "classType": None,
        "day": "FRI",
        "startTime": "11:00",
        "endTime": "11:50",
        "building": None,
        "room": " ",
    }
```

`professor`/`room`(" ") 값은 Task 4에서 확인한 실제 원본 값을 그대로 쓴 것이며, 실행 중 다르면(재수집으로 데이터가 바뀐 경우) `data/courses.json`에서 `T00138-101`의 실제 `professor`/`sessions[0].room`으로 맞춰 고친다.

- [ ] **Step 3: 통과 확인**

Run: `cd backend && python -m pytest tests/test_students.py -v`
Expected: PASS (4 passed)

- [ ] **Step 4: 커밋**

```bash
git add backend/app/services/student_service.py backend/tests/test_students.py
git commit -m "feat: 학생 시간표를 세션 단위로 펼쳐서 반환하도록 변경"
```

---

### Task 10: `chat_service` — 카테고리/온라인 필터 재정의

**Files:**
- Modify: `backend/app/services/chat_service.py:44-95, 110-115`
- Modify: `backend/tests/test_chat.py`

**Interfaces:**
- Produces: `CourseFilters.class_types: set[CourseClassType | None]` (None = "원격/판단불가"), `CourseFilters.categories: set[CourseCategory]`(5종), `extract_course_filters`/`classify_intent`/`_matches_filters` 동작 갱신.

- [ ] **Step 1: `extract_course_filters`/`_matches_filters` 재작성**

`backend/app/services/chat_service.py:44-95`를:
```python
@dataclass
class CourseFilters:
    class_types: set[CourseClassType | None] = field(default_factory=set)
    categories: set[CourseCategory] = field(default_factory=set)

    def is_empty(self) -> bool:
        return not self.class_types and not self.categories


def extract_course_filters(message: str) -> CourseFilters:
    """Very small rule-based keyword extractor. 실데이터엔 classType이
    OFFLINE 또는 None(원격, 실시간/녹화 구분 불가)만 존재하므로 "온라인"
    관련 언급은 전부 None으로 모은다 - 실시간/녹화를 구분해서 답하면
    근거 없이 지어내는 것이라 그렇게 하지 않는다."""
    filters = CourseFilters()

    if "온라인" in message:
        filters.class_types.add(None)
    if "오프라인" in message:
        filters.class_types.add(CourseClassType.OFFLINE)
    if "하이브리드" in message or "혼합" in message:
        filters.class_types.add(CourseClassType.HYBRID)

    if "전공" in message:
        filters.categories.add(CourseCategory.MAJOR_COURSE)
    if "교양" in message:
        wants_required = "필수" in message
        wants_elective = "선택" in message
        if wants_required:
            filters.categories.add(CourseCategory.GENERAL_REQUIRED)
        if wants_elective:
            filters.categories.add(CourseCategory.GENERAL_ELECTIVE)
        if not wants_required and not wants_elective:
            filters.categories.update(
                {
                    CourseCategory.GENERAL_COURSE,
                    CourseCategory.GENERAL_REQUIRED,
                    CourseCategory.GENERAL_ELECTIVE,
                }
            )

    return filters
```
(`_matches_filters`(110-115줄)는 `course.classType not in filters.class_types` 비교라 `None`이 집합 원소여도 그대로 동작 — 수정 불필요.)

- [ ] **Step 2: `test_chat.py`의 과목검색 테스트 2개를 실데이터 기준으로 재작성**

`backend/tests/test_chat.py:19-47`을:
```python
def test_chat_finds_available_online_general_courses():
    response = client.post(
        "/api/chat", json={"message": "지금 신청 가능한 온라인 교양 과목 알려줘."}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    assert len(body["courses"]) >= 1
    assert all(c["classType"] is None for c in body["courses"])
    assert all(
        c["category"] in {"GENERAL_COURSE", "GENERAL_REQUIRED", "GENERAL_ELECTIVE"}
        for c in body["courses"]
    )
    assert all(c["status"] == "OPEN" for c in body["courses"])
    assert {a["targetId"] for a in body["actions"]} == {c["id"] for c in body["courses"]}
    assert all(a["type"] == "VIEW_COURSE" for a in body["actions"])


def test_chat_searches_major_courses_regardless_of_status():
    response = client.post("/api/chat", json={"message": "전공 과목 알려줘"})

    assert response.status_code == 200
    courses = response.json()["courses"]
    assert len(courses) >= 1
    assert all(c["category"] == "MAJOR_COURSE" for c in courses)
```

- [ ] **Step 3: `test_chat_today_schedule_*`/`test_chat_next_class_*` 테스트를 실제 시간표에 맞춰 갱신**

`backend/tests/test_chat.py:50-74`를, T00138-101(FRI 11:00-11:50)/J01683-101(TUE 09:25-10:25) 기준으로 재작성:
```python
A_TUESDAY_MORNING = datetime(2024, 1, 2, 9, 0, tzinfo=KST)  # 2024-01-02는 화요일
A_FRIDAY_MORNING = datetime(2024, 1, 5, 9, 0, tzinfo=KST)  # 2024-01-05는 금요일
A_FRIDAY_AFTERNOON = datetime(2024, 1, 5, 12, 0, tzinfo=KST)


def test_chat_today_schedule_returns_only_todays_courses():
    result = chat_service.handle_message("오늘 수업 뭐 있어?", now=A_FRIDAY_MORNING)

    assert {c.id for c in result.courses} == {"T00138-101"}
    assert "AI활용웹개발" in result.answer


def test_chat_today_schedule_on_tuesday():
    result = chat_service.handle_message("오늘 수업 뭐 있어?", now=A_TUESDAY_MORNING)

    assert {c.id for c in result.courses} == {"J01683-101"}


def test_chat_next_class_before_todays_class():
    result = chat_service.handle_message("다음 수업 뭐야?", now=A_FRIDAY_MORNING)

    assert {c.id for c in result.courses} == {"T00138-101"}


def test_chat_next_class_wraps_to_following_week():
    # FRI 11:00-11:50(T00138-101)이 끝난 뒤엔 다음 주 TUE 09:25(J01683-101)가 다음 수업.
    result = chat_service.handle_message("다음 수업 뭐야?", now=A_FRIDAY_AFTERNOON)

    assert {c.id for c in result.courses} == {"J01683-101"}
```
(날짜 요일은 `date +%A` 등으로 실제 확인하고 틀리면 맞는 요일의 실제 날짜로 고친다 — 2024-01-01이 월요일이라는 옛 주석 패턴을 그대로 따른 것.)

- [ ] **Step 4: AI rephrase 관련 테스트(108-157줄)의 "전공필수" 메시지/카운트 갱신**

`test_chat_uses_ai_rephrased_answer_when_ai_client_available`와 `test_chat_falls_back_to_template_answer_when_ai_client_fails`에서 메시지를 `"전공 과목 알려줘"`로 바꾸고, `len(result.courses) == 6`/`"6건"` 부분을 실제 MAJOR_COURSE 개수(Task 4 검증 시 확인한 35개)로 맞춘다:
```python
def test_chat_uses_ai_rephrased_answer_when_ai_client_available(monkeypatch):
    monkeypatch.setattr(
        chat_service.ai_client, "get_client", lambda: _FakeAIClient("다듬어진 답변입니다.")
    )

    result = chat_service.handle_message("전공 과목 알려줘")

    assert result.answer == "다듬어진 답변입니다."
    assert len(result.courses) == 35


def test_chat_falls_back_to_template_answer_when_ai_client_fails(monkeypatch):
    monkeypatch.setattr(chat_service.ai_client, "get_client", lambda: _FakeAIClient(None))

    result = chat_service.handle_message("전공 과목 알려줘")

    assert result.answer == "조건에 맞는 과목을 35건 찾았습니다."
```

- [ ] **Step 5: 통과 확인**

Run: `cd backend && python -m pytest tests/test_chat.py -v`
Expected: PASS (전체)

- [ ] **Step 6: 커밋**

```bash
git add backend/app/services/chat_service.py backend/tests/test_chat.py
git commit -m "feat: 챗봇 필터를 새 CourseCategory/None-온라인 기준으로 재정의"
```

---

### Task 11: 백엔드 전체 스위트 그린 확인

**Files:** (없음, 검증만)

- [ ] **Step 1: 전체 백엔드 테스트 실행**

Run: `cd backend && python -m pytest -q`
Expected: 전부 PASS. 실패가 남아있으면 어떤 파일인지 확인 — `test_school_info.py`/`test_counseling.py`/`test_buildings.py` 등 Course와 무관한 테스트가 이번 변경으로 깨졌다면 Course 스키마와 무관한 회귀이니 원인을 별도로 조사한다 (이 계획 범위 밖의 버그일 가능성이 높음 — 원인만 기록하고 계속 진행할지 사용자에게 확인).

- [ ] **Step 2: 커밋할 변경 없음 — 다음 태스크(프론트)로 이동**

---

### Task 12: 프론트 타입 + 라벨

**Files:**
- Modify: `frontend/src/types/index.ts`
- Modify: `frontend/src/lib/labels.ts`

- [ ] **Step 1: `frontend/src/types/index.ts`의 Course 관련 타입 교체**

```typescript
export type CourseCategory =
  | "GENERAL_COURSE"
  | "GENERAL_REQUIRED"
  | "GENERAL_ELECTIVE"
  | "MAJOR_COURSE"
  | "INTEGRATED_MAJOR";

export interface Session {
  day: Day;
  startTime: string; // "13:00"
  endTime: string; // "15:50"
  building: string | null;
  room: string | null;
}

export interface EligibleDept {
  code: string;
  name: string;
}

export interface Course {
  id: string;
  name: string;
  professor: string;
  credits: number;
  category: CourseCategory;
  classType: CourseClassType | null;
  sessions: Session[];
  targetGrade: number;
  eligibleDepts: EligibleDept[];
  capacity: number;
  enrolled: number;
  status: CourseStatus;
  lastUpdated: string; // ISO 8601
}
```
(`CourseClassType`/`CourseStatus`/`Day`/`ScheduleEntry`는 변경 없음 — `ScheduleEntry`는 여전히 세션 1개=엔트리 1개 투영이라 그대로 두되, `classType: CourseClassType | null`로만 nullable 반영.)

`frontend/src/types/index.ts:51-61`의 `ScheduleEntry`를:
```typescript
export interface ScheduleEntry {
  courseId: string;
  name: string;
  professor: string;
  classType: CourseClassType | null;
  day: Day;
  startTime: string;
  endTime: string;
  building: string | null;
  room: string | null;
}
```

- [ ] **Step 2: `frontend/src/lib/labels.ts`의 `categoryLabel` 교체**

```typescript
export const categoryLabel: Record<CourseCategory, string> = {
  GENERAL_COURSE: "교양과정",
  GENERAL_REQUIRED: "교양필수",
  GENERAL_ELECTIVE: "일반선택",
  MAJOR_COURSE: "전공과정",
  INTEGRATED_MAJOR: "통합전공교과",
};
```

- [ ] **Step 3: 타입체크**

Run: `cd frontend && npx tsc --noEmit`
Expected: `course-card.tsx`/`schedule/page.tsx`/`courses/page.tsx`에서 `course.day`/`course.startTime`/`classTypeLabel[course.classType]`(null 인덱싱) 관련 에러 다수 발생 — 이후 태스크에서 해소.

- [ ] **Step 4: 커밋**

```bash
git add frontend/src/types/index.ts frontend/src/lib/labels.ts
git commit -m "feat: 프론트 Course 타입을 sessions 배열 + 신규 CourseCategory로 갱신"
```

---

### Task 13: `course-card.tsx` — 다중 세션 표시 + null classType 처리

**Files:**
- Modify: `frontend/src/components/course-card.tsx`

- [ ] **Step 1: 세션 목록 렌더링으로 교체**

```tsx
import { Badge } from "@/components/ui/badge";
import { Card, CardAction, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { categoryLabel, classTypeLabel, dayLabel, statusBadgeVariant, statusLabel } from "@/lib/labels";
import { formatDateTime } from "@/lib/time";
import type { Course } from "@/types";
import type { ReactNode } from "react";

export function CourseCard({ course, footer }: { course: Course; footer?: ReactNode }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{course.name}</CardTitle>
        <p className="text-xs text-muted-foreground">
          {course.professor} · {course.credits}학점 · {categoryLabel[course.category]}
        </p>
        <CardAction>
          <Badge variant={statusBadgeVariant[course.status]}>{statusLabel[course.status]}</Badge>
        </CardAction>
      </CardHeader>
      <CardContent className="space-y-1 text-sm">
        <p className="text-muted-foreground">
          {course.classType ? classTypeLabel[course.classType] : "온라인(방식 확인 안 됨)"} · {course.targetGrade}학년 대상
        </p>
        {course.sessions.length === 0 ? (
          <p className="text-muted-foreground">지정된 시간 없음</p>
        ) : (
          course.sessions.map((s, i) => (
            <p key={i}>
              {dayLabel[s.day]} {s.startTime}~{s.endTime} ·{" "}
              {s.building ? `${s.building} ${s.room}` : s.room ? `${s.room}` : "장소 미정"}
            </p>
          ))
        )}
        <p className="text-muted-foreground">
          {course.enrolled}/{course.capacity}명 · 갱신 {formatDateTime(course.lastUpdated)}
        </p>
      </CardContent>
      {footer && <CardFooter className="gap-2">{footer}</CardFooter>}
    </Card>
  );
}
```

- [ ] **Step 2: 커밋**

```bash
git add frontend/src/components/course-card.tsx
git commit -m "feat: CourseCard가 여러 세션을 줄줄이 표시하고 null classType을 안전 처리"
```

---

### Task 14: `schedule/page.tsx` — 미리보기 블록을 세션별로 펼치기

**Files:**
- Modify: `frontend/src/app/schedule/page.tsx:67-104, 200-225`

**Interfaces:**
- Consumes: `Course.sessions` (Task 12).

- [ ] **Step 1: `previewBlocks` 계산을 세션 flatMap으로 변경**

`frontend/src/app/schedule/page.tsx:85-101`을:
```typescript
    const previewBlocks: Block[] = previewIds
      .map((id) => courseList.find((c) => c.id === id))
      .filter((c): c is NonNullable<typeof c> => !!c)
      .flatMap((c) =>
        c.sessions.map((s, i) => ({
          key: `preview-${c.id}-${i}`,
          courseId: c.id,
          day: s.day,
          startTime: s.startTime,
          endTime: s.endTime,
          name: c.name,
          professor: c.professor,
          classType: c.classType,
          building: s.building,
          room: s.room,
          status: c.status,
          isPreview: true,
        }))
      );
```

- [ ] **Step 2: `Block.classType` 타입과 상세 다이얼로그(200-225줄)의 null 처리**

`Block` 인터페이스(28-41줄)의 `classType: string`을 `classType: string | null`로 바꾸고, 다이얼로그의 `classTypeLabel[selected.classType as keyof typeof classTypeLabel]` 부분을:
```tsx
                <p>
                  수업방식:{" "}
                  {selected.classType
                    ? classTypeLabel[selected.classType as keyof typeof classTypeLabel]
                    : "온라인(방식 확인 안 됨)"}
                </p>
```
로 교체.

- [ ] **Step 3: 타입체크 + 빌드**

Run: `cd frontend && npx tsc --noEmit && npm run build`
Expected: 에러 없이 통과 (courses/page.tsx는 Task 15에서 마저 고침 — 그 전까진 여기도 에러 남을 수 있음, 이 태스크는 schedule 관련 에러 소거까지만 확인).

- [ ] **Step 4: 커밋**

```bash
git add frontend/src/app/schedule/page.tsx
git commit -m "feat: 시간표 미리보기 블록을 과목의 세션 배열 기준으로 펼치기"
```

---

### Task 15: `courses/page.tsx` — 강좌구분/대상학년/학과 필터 UI

**Files:**
- Modify: `frontend/src/app/courses/page.tsx`

**Interfaces:**
- Consumes: `Course.targetGrade`, `Course.eligibleDepts`, `Course.classType`(null=원격) — 전부 이미 `getCourses()` 응답에 포함되어 있음(백엔드 쿼리 파라미터 추가 없이 **클라이언트 사이드**로 추가 필터링).

- [ ] **Step 1: 강좌구분(교양/전공/원격)·대상학년·학과 필터 상태 추가**

`courses/page.tsx` 상단 상태 선언부에 추가:
```tsx
  const [gubun, setGubun] = useState<"ALL" | "GENERAL" | "MAJOR" | "REMOTE">("ALL");
  const [grade, setGrade] = useState<number | "ALL">("ALL");
  const [dept, setDept] = useState<string | "ALL">("ALL");
```

- [ ] **Step 2: 서버 응답을 받은 뒤 클라이언트에서 강좌구분/학년/학과로 추가 필터링, 학과 목록은 로드된 과목들에서 유도**

```tsx
  const allCourses = coursesData?.courses ?? [];

  const courses = allCourses.filter((c) => {
    if (gubun === "REMOTE" && c.classType !== null) return false;
    if (gubun === "GENERAL" && !c.category.startsWith("GENERAL")) return false;
    if (gubun === "MAJOR" && c.category !== "MAJOR_COURSE" && c.category !== "INTEGRATED_MAJOR") return false;
    if (grade !== "ALL" && c.targetGrade !== grade) return false;
    if (dept !== "ALL" && !c.eligibleDepts.some((d) => d.code === dept)) return false;
    return true;
  });

  const deptOptions = Array.from(
    new Map(allCourses.flatMap((c) => c.eligibleDepts).map((d) => [d.code, d])).values()
  ).sort((a, b) => a.name.localeCompare(b.name, "ko"));
```
(기존 `const courses = coursesData?.courses ?? [];` 줄을 위 블록으로 교체.)

- [ ] **Step 3: 필터 UI(드롭다운 3개) 추가 — 기존 상태 필터 옆에**

기존 `<Select value={category} ...>` 블록 바로 뒤에 추가:
```tsx
        <Select value={gubun} onValueChange={(v) => setGubun(v as typeof gubun)}>
          <SelectTrigger size="sm">
            <SelectValue placeholder="강좌구분" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">전체 강좌구분</SelectItem>
            <SelectItem value="GENERAL">교양</SelectItem>
            <SelectItem value="MAJOR">전공</SelectItem>
            <SelectItem value="REMOTE">원격강좌</SelectItem>
          </SelectContent>
        </Select>
        <Select
          value={grade === "ALL" ? "ALL" : String(grade)}
          onValueChange={(v) => setGrade(v === "ALL" ? "ALL" : Number(v))}
        >
          <SelectTrigger size="sm">
            <SelectValue placeholder="대상학년" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">전체 학년</SelectItem>
            {[1, 2, 3, 4].map((g) => (
              <SelectItem key={g} value={String(g)}>
                {g}학년
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={dept} onValueChange={(v) => setDept(v)}>
          <SelectTrigger size="sm">
            <SelectValue placeholder="학과" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">전체 학과</SelectItem>
            {deptOptions.map((d) => (
              <SelectItem key={d.code} value={d.code}>
                {d.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
```

- [ ] **Step 4: 타입체크 + 빌드**

Run: `cd frontend && npx tsc --noEmit && npm run build`
Expected: 에러 없이 통과.

- [ ] **Step 5: `run` 스킬로 앱을 띄워 `courses` 화면을 스크린샷으로 확인**

`run` 스킬 사용 (frontend `npm run dev` + backend `uvicorn` 둘 다 필요 — 이미 `.env` 세팅된 상태 가정), `/courses` 페이지에서 강좌구분/대상학년/학과 드롭다운으로 실제 246개 데이터가 걸러지는지 눈으로 확인.

- [ ] **Step 6: 커밋**

```bash
git add frontend/src/app/courses/page.tsx
git commit -m "feat: 과목 검색 화면에 강좌구분/대상학년/학과 필터 추가"
```

---

### Task 16: 마무리 — 전체 검증 + 브랜치 병합 준비

**Files:** (없음, 검증만)

- [ ] **Step 1: 백엔드 전체 테스트**

Run: `cd backend && python -m pytest -q`
Expected: 전부 PASS.

- [ ] **Step 2: 프론트 빌드**

Run: `cd frontend && npx tsc --noEmit && npm run build`
Expected: 에러 없이 통과.

- [ ] **Step 3: `superpowers:requesting-code-review` 스킬로 이 브랜치 변경분 리뷰 요청**

- [ ] **Step 4: 리뷰 통과 후 `superpowers:finishing-a-development-branch` 스킬로 `integration/fullstack-demo`에 병합할지, PR을 올릴지 결정**

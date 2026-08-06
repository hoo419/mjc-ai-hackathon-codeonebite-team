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

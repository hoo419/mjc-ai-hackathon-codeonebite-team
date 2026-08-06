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
    MAJOR_REQUIRED = "MAJOR_REQUIRED"
    MAJOR_ELECTIVE = "MAJOR_ELECTIVE"
    GENERAL_REQUIRED = "GENERAL_REQUIRED"
    GENERAL_ELECTIVE = "GENERAL_ELECTIVE"
    OTHER = "OTHER"


class Course(BaseModel):
    """Mirrors the Course object in API_CONTRACT.md section 4. Field names
    and shape must stay in lockstep with that document."""

    id: str
    name: str
    professor: str
    credits: int
    category: CourseCategory
    classType: CourseClassType
    day: str
    startTime: str
    endTime: str
    building: str | None
    room: str | None
    capacity: int
    enrolled: int
    status: CourseStatus
    lastUpdated: str


class CourseListResponse(BaseModel):
    courses: list[Course]


class CourseDetailResponse(BaseModel):
    course: Course

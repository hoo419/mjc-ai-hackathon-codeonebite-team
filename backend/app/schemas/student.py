from pydantic import BaseModel

from app.schemas.course import Course, CourseClassType


class Student(BaseModel):
    """Mirrors API_CONTRACT.md section 6 - GET /students/me."""

    id: str
    name: str
    department: str
    grade: int
    semester: int


class StudentResponse(BaseModel):
    student: Student


class StudentCoursesResponse(BaseModel):
    courses: list[Course]


class ScheduleItem(BaseModel):
    """Mirrors the schedule entry shape in API_CONTRACT.md section 6 -
    GET /students/me/schedule. Deliberately a smaller projection of Course,
    not the full object."""

    courseId: str
    name: str
    professor: str
    classType: CourseClassType
    day: str
    startTime: str
    endTime: str
    building: str | None
    room: str | None


class ScheduleResponse(BaseModel):
    schedule: list[ScheduleItem]

from enum import StrEnum

from pydantic import BaseModel


class EnrollmentStatus(StrEnum):
    ENROLLED = "ENROLLED"
    CANCELLED = "CANCELLED"


class EnrollmentRecord(BaseModel):
    """Internal Mock storage shape (data/enrollments.json), not part of
    API_CONTRACT.md directly - it backs the Student/Enrollment endpoints."""

    studentId: str
    courseId: str
    status: EnrollmentStatus
    enrolledAt: str

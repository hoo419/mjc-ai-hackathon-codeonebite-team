from enum import StrEnum

from pydantic import BaseModel


class CounselingSummaryResponse(BaseModel):
    """Mirrors API_CONTRACT.md section 10 - GET /counseling/me."""

    careerSummary: str
    personalitySummary: str
    lastCounselingAt: str


class CounselingTargetType(StrEnum):
    ADVISOR = "ADVISOR"
    CAREER_COUNSELOR = "CAREER_COUNSELOR"
    DEPARTMENT_OFFICE = "DEPARTMENT_OFFICE"


class CounselingRequestPayload(BaseModel):
    targetType: CounselingTargetType
    message: str


class CounselingRequestStatus(StrEnum):
    REQUESTED = "REQUESTED"


class CounselingRequestResponse(BaseModel):
    success: bool
    requestId: str
    status: CounselingRequestStatus

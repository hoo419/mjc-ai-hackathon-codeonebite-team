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


class AptitudeAnalysisRequest(BaseModel):
    """mpu.mjc.ac.kr(SMART CARE)은 로그인이 필수라 백엔드가 대신 접속할 수
    없다 - 학생이 직접 로그인해서 확인한 검사 결과 원문을 붙여넣는다."""

    rawText: str


class AptitudeAnalysisResponse(BaseModel):
    summary: str
    insights: list[str] = []

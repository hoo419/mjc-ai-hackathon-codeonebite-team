from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.counseling import (
    AptitudeAnalysisRequest,
    AptitudeAnalysisResponse,
    CounselingRequestPayload,
    CounselingRequestResponse,
)
from app.services import counseling_service

router = APIRouter(prefix="/counseling", tags=["counseling"])


@router.get("/me")
def get_my_counseling_summary():
    summary = counseling_service.get_current_student_summary()
    if summary is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "COUNSELING_SUMMARY_NOT_FOUND",
                    "message": "상담 요약 정보를 찾을 수 없습니다.",
                }
            },
        )
    return summary


@router.post("/request", response_model=CounselingRequestResponse)
def request_counseling(payload: CounselingRequestPayload) -> CounselingRequestResponse:
    return counseling_service.submit_request(payload)


@router.post("/analyze-aptitude")
def analyze_aptitude(payload: AptitudeAnalysisRequest):
    result = counseling_service.analyze_aptitude(payload.rawText)
    if result is None:
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "ANALYSIS_UNAVAILABLE",
                    "message": "지금은 분석할 수 없습니다. 잠시 후 다시 시도해 주세요.",
                }
            },
        )
    return result

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.counseling import CounselingRequestPayload, CounselingRequestResponse
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

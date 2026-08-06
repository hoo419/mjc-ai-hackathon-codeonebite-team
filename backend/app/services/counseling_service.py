from app.repositories import counseling_repository
from app.schemas.counseling import (
    CounselingRequestPayload,
    CounselingRequestResponse,
    CounselingRequestStatus,
    CounselingSummaryResponse,
)
from app.services import student_service


def get_current_student_summary() -> CounselingSummaryResponse | None:
    student = student_service.get_current_student()
    return counseling_repository.get_summary_for_student(student.id)


def submit_request(payload: CounselingRequestPayload) -> CounselingRequestResponse:
    """Mock 상담 요청 접수. 실제 라우팅/담당자 배정은 아직 없고, 요청을
    받았다는 것만 확인해준다."""
    student = student_service.get_current_student()
    request_id = counseling_repository.add_request(student.id, payload)
    return CounselingRequestResponse(
        success=True,
        requestId=request_id,
        status=CounselingRequestStatus.REQUESTED,
    )

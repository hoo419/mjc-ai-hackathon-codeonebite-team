from fastapi import APIRouter
from pydantic import BaseModel

from app.services import enrollment_service

router = APIRouter(prefix="/enrollment", tags=["enrollment"])


class EnrollmentRequest(BaseModel):
    courseId: str


@router.post("")
def create_enrollment(payload: EnrollmentRequest):
    try:
        record = enrollment_service.enroll(payload.courseId)
    except enrollment_service.EnrollmentError as exc:
        # Expected business-rule failures (COURSE_FULL, TIME_CONFLICT, ...)
        # are reported via the "success" flag rather than an HTTP error
        # status, matching the response shape API_CONTRACT.md documents.
        return {
            "success": False,
            "error": {"code": exc.code, "message": exc.message},
        }
    return {
        "success": True,
        "enrollment": {"courseId": record.courseId, "status": record.status.value},
    }


@router.delete("/{course_id}")
def delete_enrollment(course_id: str):
    enrollment_service.cancel(course_id)
    return {"success": True}

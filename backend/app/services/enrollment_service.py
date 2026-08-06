from datetime import datetime

from app.core.time import KST
from app.repositories import enrollment_repository
from app.schemas.course import Course, CourseStatus
from app.schemas.enrollment import EnrollmentRecord, EnrollmentStatus
from app.schemas.student import Student
from app.services import course_service, student_service

ERROR_MESSAGES = {
    "COURSE_NOT_FOUND": "과목을 찾을 수 없습니다.",
    "ALREADY_ENROLLED": "이미 신청한 과목입니다.",
    "COURSE_CANCELLED": "폐강된 과목입니다.",
    "ENROLLMENT_CLOSED": "현재 수강신청 기간이 아닙니다.",
    "COURSE_FULL": "수강 정원이 마감되었습니다.",
    "NOT_ELIGIBLE": "수강 자격 조건을 충족하지 않습니다.",
    "TIME_CONFLICT": "기존 수강 과목과 시간이 겹칩니다.",
}


class EnrollmentError(Exception):
    """Carries one of the error codes listed in API_CONTRACT.md section 7."""

    def __init__(self, code: str):
        self.code = code
        self.message = ERROR_MESSAGES[code]
        super().__init__(self.message)


def _has_time_conflict(existing_courses: list[Course], candidate: Course) -> bool:
    """AI_AGENT_RULES.md 시간표 규칙: 같은 요일이고
    new_start < existing_end AND new_end > existing_start 이면 충돌.
    시간 비교는 "HH:MM" 문자열이 자릿수 고정이라 사전식 비교가 시간 순서와 일치한다."""
    for existing in existing_courses:
        if existing.day != candidate.day:
            continue
        if candidate.startTime < existing.endTime and candidate.endTime > existing.startTime:
            return True
    return False


def is_student_eligible(student: Student, course: Course) -> bool:
    """No eligibility Mock data (prerequisites, grade-level restrictions,
    department-only majors, ...) exists yet, so every student currently
    passes. Replace this once real eligibility data exists - never let the
    LLM decide eligibility instead."""
    return True


def enroll(course_id: str) -> EnrollmentRecord:
    """Validates in the order BACKEND_IMPLEMENTATION_PLAN.md Phase 5 defines,
    raising EnrollmentError with a contract error code on the first failure."""
    student = student_service.get_current_student()
    course = course_service.get_course_by_id(course_id)

    if course is None:
        raise EnrollmentError("COURSE_NOT_FOUND")

    existing = enrollment_repository.find_enrollment(student.id, course_id)
    if existing is not None and existing.status == EnrollmentStatus.ENROLLED:
        raise EnrollmentError("ALREADY_ENROLLED")

    if course.status == CourseStatus.CANCELLED:
        raise EnrollmentError("COURSE_CANCELLED")

    if course.status in (CourseStatus.UPCOMING, CourseStatus.CLOSED):
        raise EnrollmentError("ENROLLMENT_CLOSED")

    # Defensive: trust the computed remaining seats over the stored status
    # string, in case the two ever disagree.
    if course_service.remaining_seats(course) <= 0:
        raise EnrollmentError("COURSE_FULL")

    if not is_student_eligible(student, course):
        raise EnrollmentError("NOT_ELIGIBLE")

    current_courses = student_service.get_current_student_courses()
    if _has_time_conflict(current_courses, course):
        raise EnrollmentError("TIME_CONFLICT")

    record = EnrollmentRecord(
        studentId=student.id,
        courseId=course_id,
        status=EnrollmentStatus.ENROLLED,
        enrolledAt=datetime.now(KST).isoformat(),
    )
    enrollment_repository.upsert_enrolled(record)
    # Only reached on a genuinely new successful enrollment (ALREADY_ENROLLED
    # already returned above), so this always represents one new seat taken.
    course_service.record_enrollment(course_id)
    return record


def cancel(course_id: str) -> None:
    """Mock 수강취소: 신청 기록이 없어도 조용히 성공 처리한다 (idempotent)."""
    student = student_service.get_current_student()
    existing = enrollment_repository.find_enrollment(student.id, course_id)
    was_enrolled = existing is not None and existing.status == EnrollmentStatus.ENROLLED

    enrollment_repository.cancel_enrollment(student.id, course_id)

    if was_enrolled:
        course_service.record_cancellation(course_id)

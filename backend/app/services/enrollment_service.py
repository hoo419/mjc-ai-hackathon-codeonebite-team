from datetime import datetime

from app.core.time import KST
from app.repositories import enrollment_repository
from app.schemas.course import Course
from app.schemas.enrollment import EnrollmentRecord, EnrollmentStatus
from app.services import course_service, student_service

ERROR_MESSAGES = {
    "COURSE_NOT_FOUND": "과목을 찾을 수 없습니다.",
    "ALREADY_ENROLLED": "이미 신청한 과목입니다.",
    "TIME_CONFLICT": "기존 수강 과목과 시간이 겹칩니다.",
}


class EnrollmentError(Exception):
    """Carries one of the error codes listed in API_CONTRACT.md section 7."""

    def __init__(self, code: str):
        self.code = code
        self.message = ERROR_MESSAGES[code]
        super().__init__(self.message)


def _has_time_conflict(existing_courses: list[Course], candidate: Course) -> bool:
    """AI_AGENT_RULES.md 시간표 규칙: 두 세션이 같은 요일이고
    new_start < existing_end AND new_end > existing_start 이면 충돌.
    한 분반이 여러 세션을 가질 수 있으므로, 기존 과목들의 모든 세션과
    후보 과목의 모든 세션을 한 쌍씩 비교한다."""
    for existing in existing_courses:
        for existing_session in existing.sessions:
            for candidate_session in candidate.sessions:
                if existing_session.day != candidate_session.day:
                    continue
                if (
                    candidate_session.startTime < existing_session.endTime
                    and candidate_session.endTime > existing_session.startTime
                ):
                    return True
    return False


def enroll(course_id: str) -> EnrollmentRecord:
    """"수강신청"은 학생이 실제 sugang.mjc.ac.kr에서 이미 마친 신청을 우리
    시간표 도구에 기록하는 것이다 (정원/폐강/자격/신청기간 검증은 실제
    신청 시점에 이미 끝난 일이라 여기서 다시 하지 않는다). 우리가 하는 건
    딱 두 가지: 중복 기록 방지, 그리고 학생이 실수로 겹치는 시간대 두
    과목을 등록하지 않았는지 확인하는 것 - 이건 실제 신청 사이트가 안
    잡아줄 수도 있는 부분이라 우리 쪽에서 검증하는 의미가 있다."""
    student = student_service.get_current_student()
    course = course_service.get_course_by_id(course_id)

    if course is None:
        raise EnrollmentError("COURSE_NOT_FOUND")

    existing = enrollment_repository.find_enrollment(student.id, course_id)
    if existing is not None and existing.status == EnrollmentStatus.ENROLLED:
        raise EnrollmentError("ALREADY_ENROLLED")

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
    # Only reached on a genuinely new successful add (ALREADY_ENROLLED
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

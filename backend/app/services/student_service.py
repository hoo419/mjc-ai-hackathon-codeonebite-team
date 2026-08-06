from app.repositories import enrollment_repository, student_repository
from app.schemas.course import Course
from app.schemas.enrollment import EnrollmentStatus
from app.schemas.student import ScheduleItem, Student
from app.services import course_service


def get_current_student() -> Student:
    return student_repository.get_current_student()


def update_current_student_profile(*, department: str, grade: int, semester: int) -> Student:
    return student_repository.update_current_student_profile(
        department=department, grade=grade, semester=semester
    )


def get_current_student_courses() -> list[Course]:
    """Active enrollments only. Which courses/seats/status exist is decided
    by the enrollment records + course data, never guessed here."""
    student = get_current_student()
    enrollments = enrollment_repository.list_enrollments_for_student(student.id)
    course_ids = [e.courseId for e in enrollments if e.status == EnrollmentStatus.ENROLLED]

    courses = []
    for course_id in course_ids:
        course = course_service.get_course_by_id(course_id)
        if course is not None:
            courses.append(course)
    return courses


def get_current_student_schedule() -> list[ScheduleItem]:
    """한 과목이 여러 세션(요일)을 가지면, 세션마다 하나씩 ScheduleItem을
    만든다 - 시간표 화면은 "언제 어디서 무슨 수업"인지 슬롯 단위로 봐야
    하기 때문이다."""
    courses = get_current_student_courses()
    return [
        ScheduleItem(
            courseId=course.id,
            name=course.name,
            professor=course.professor,
            classType=course.classType,
            day=session.day,
            startTime=session.startTime,
            endTime=session.endTime,
            building=session.building,
            room=session.room,
        )
        for course in courses
        for session in course.sessions
    ]

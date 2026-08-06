from app.repositories import enrollment_repository, student_repository
from app.schemas.course import Course
from app.schemas.enrollment import EnrollmentStatus
from app.schemas.student import ScheduleItem, Student
from app.services import course_service


def get_current_student() -> Student:
    return student_repository.get_current_student()


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
    courses = get_current_student_courses()
    return [
        ScheduleItem(
            courseId=course.id,
            name=course.name,
            professor=course.professor,
            classType=course.classType,
            day=course.day,
            startTime=course.startTime,
            endTime=course.endTime,
            building=course.building,
            room=course.room,
        )
        for course in courses
    ]

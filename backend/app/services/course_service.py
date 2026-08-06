from app.repositories import course_repository
from app.schemas.course import Course, CourseCategory, CourseClassType, CourseStatus


def search_courses(
    *,
    status: CourseStatus | None = None,
    class_type: CourseClassType | None = None,
    category: CourseCategory | None = None,
    search: str | None = None,
) -> list[Course]:
    """Filter mock courses. All facts (status, capacity, schedule, ...) come
    straight from the stored data — nothing here is inferred or guessed."""
    courses = course_repository.list_courses()

    if status is not None:
        courses = [c for c in courses if c.status == status]
    if class_type is not None:
        courses = [c for c in courses if c.classType == class_type]
    if category is not None:
        courses = [c for c in courses if c.category == category]
    if search:
        needle = search.strip().lower()
        courses = [c for c in courses if needle in c.name.lower()]

    return courses


def get_course_by_id(course_id: str) -> Course | None:
    return course_repository.get_course(course_id)


def remaining_seats(course: Course) -> int:
    return course.capacity - course.enrolled

import json
from pathlib import Path

from app.core.config import settings
from app.schemas.course import Course, CourseStatus

# Course.enrolled is mutated at runtime once a Mock enrollment actually
# succeeds (so a later GET reflects reality - remaining seats, FULL status),
# so - like enrollment_repository - this can't just be an lru_cache'd read
# of the JSON file.
_courses: list[Course] | None = None


def _load_from_disk(data_dir: Path) -> list[Course]:
    path = data_dir / "courses.json"
    with path.open(encoding="utf-8") as f:
        raw = json.load(f)
    return [Course.model_validate(item) for item in raw]


def _ensure_loaded() -> list[Course]:
    global _courses
    if _courses is None:
        _courses = _load_from_disk(settings.data_dir)
    return _courses


def reset() -> None:
    """Reload from data/courses.json, discarding in-memory Mock writes
    (enrolled counts bumped by successful enrollments). Used between tests
    so they don't leak state into each other."""
    global _courses
    _courses = _load_from_disk(settings.data_dir)


def list_courses() -> list[Course]:
    return list(_ensure_loaded())


def get_course(course_id: str) -> Course | None:
    for course in _ensure_loaded():
        if course.id == course_id:
            return course
    return None


def increment_enrolled(course_id: str) -> None:
    """Called once an enrollment actually succeeds. Flips OPEN -> FULL when
    capacity is reached so later reads (GET /courses, chat search) stay
    consistent with what just happened - this status change is a computed
    fact, not something an LLM decides."""
    course = get_course(course_id)
    if course is None:
        return
    course.enrolled += 1
    if course.enrolled >= course.capacity and course.status == CourseStatus.OPEN:
        course.status = CourseStatus.FULL


def decrement_enrolled(course_id: str) -> None:
    """Called once a Mock cancellation actually removes an ENROLLED record."""
    course = get_course(course_id)
    if course is None:
        return
    course.enrolled = max(0, course.enrolled - 1)
    if course.enrolled < course.capacity and course.status == CourseStatus.FULL:
        course.status = CourseStatus.OPEN

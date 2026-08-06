import json
from pathlib import Path

from app.core import db as db_core
from app.core.config import settings
from app.models import CourseModel
from app.schemas.course import Course, CourseStatus

# Course.enrolled is mutated at runtime once a Mock enrollment actually
# succeeds (so a later GET reflects reality - remaining seats, FULL status).
#
# Two backends share this module's public interface:
# - Mock (default): in-memory list loaded from data/courses.json.
# - Database (Phase 9, when settings.database_url is set): reads/writes
#   CourseModel rows via app.core.db.
# Services never know which one is active - that's the point of the
# repository pattern (Mock -> DB must be swappable without touching
# anything above this layer).
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


def _model_to_schema(row: CourseModel) -> Course:
    return Course(
        id=row.id,
        name=row.name,
        professor=row.professor,
        credits=row.credits,
        category=row.category,
        classType=row.class_type,
        sessions=json.loads(row.sessions_json),
        targetGrade=row.target_grade,
        eligibleDepts=json.loads(row.eligible_depts_json),
        capacity=row.capacity,
        enrolled=row.enrolled,
        status=row.status,
        lastUpdated=row.last_updated,
    )


def reset() -> None:
    """Mock mode: reload from data/courses.json, discarding in-memory
    writes. DB mode: wipe and reseed. Used between tests."""
    global _courses
    if settings.database_url:
        from app.core import seed

        seed.reset_from_mock()
        return
    _courses = _load_from_disk(settings.data_dir)


def list_courses() -> list[Course]:
    if settings.database_url:
        with db_core.get_session() as session:
            return [_model_to_schema(row) for row in session.query(CourseModel).all()]
    return list(_ensure_loaded())


def get_course(course_id: str) -> Course | None:
    if settings.database_url:
        with db_core.get_session() as session:
            row = session.get(CourseModel, course_id)
            return _model_to_schema(row) if row is not None else None
    for course in _ensure_loaded():
        if course.id == course_id:
            return course
    return None


def increment_enrolled(course_id: str) -> None:
    """Called once an enrollment actually succeeds. Flips OPEN -> FULL when
    capacity is reached so later reads (GET /courses, chat search) stay
    consistent with what just happened - this status change is a computed
    fact, not something an LLM decides."""
    if settings.database_url:
        with db_core.get_session() as session:
            row = session.get(CourseModel, course_id)
            if row is None:
                return
            row.enrolled += 1
            if row.enrolled >= row.capacity and row.status == CourseStatus.OPEN:
                row.status = CourseStatus.FULL
            session.commit()
        return

    course = get_course(course_id)
    if course is None:
        return
    course.enrolled += 1
    if course.enrolled >= course.capacity and course.status == CourseStatus.OPEN:
        course.status = CourseStatus.FULL


def decrement_enrolled(course_id: str) -> None:
    """Called once a Mock cancellation actually removes an ENROLLED record."""
    if settings.database_url:
        with db_core.get_session() as session:
            row = session.get(CourseModel, course_id)
            if row is None:
                return
            row.enrolled = max(0, row.enrolled - 1)
            if row.enrolled < row.capacity and row.status == CourseStatus.FULL:
                row.status = CourseStatus.OPEN
            session.commit()
        return

    course = get_course(course_id)
    if course is None:
        return
    course.enrolled = max(0, course.enrolled - 1)
    if course.enrolled < course.capacity and course.status == CourseStatus.FULL:
        course.status = CourseStatus.OPEN

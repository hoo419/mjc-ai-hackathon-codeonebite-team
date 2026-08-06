import json
from pathlib import Path

from app.core import db as db_core
from app.core.config import settings
from app.models import StudentModel
from app.schemas.student import Student

# Student profile fields (department/grade/semester) can now be edited via
# PATCH /students/me - the student checks the real school portal themselves
# (we never touch their login credentials) and types in what they see. Like
# course/enrollment, Mock mode needs real in-memory mutable state instead of
# an lru_cache'd read-only reload.
_students: list[Student] | None = None


def _load_from_disk(data_dir: Path) -> list[Student]:
    path = data_dir / "students.json"
    with path.open(encoding="utf-8") as f:
        raw = json.load(f)
    return [Student.model_validate(item) for item in raw]


def _ensure_loaded() -> list[Student]:
    global _students
    if _students is None:
        _students = _load_from_disk(settings.data_dir)
    return _students


def reset() -> None:
    """Mock mode: reload from data/students.json, discarding profile edits.
    DB mode: wipe and reseed (shared with course/enrollment reset). Used
    between tests."""
    global _students
    if settings.database_url:
        from app.core import seed

        seed.reset_from_mock()
        return
    _students = _load_from_disk(settings.data_dir)


def _model_to_schema(row: StudentModel) -> Student:
    return Student(
        id=row.id,
        name=row.name,
        department=row.department,
        grade=row.grade,
        semester=row.semester,
    )


def list_students() -> list[Student]:
    if settings.database_url:
        with db_core.get_session() as session:
            return [_model_to_schema(row) for row in session.query(StudentModel).all()]
    return list(_ensure_loaded())


def get_current_student() -> Student:
    """MVP has exactly one mock student; there is no auth yet, so 'current
    student' is always the first (and only) entry."""
    return list_students()[0]


def update_current_student_profile(*, department: str, grade: int, semester: int) -> Student:
    if settings.database_url:
        with db_core.get_session() as session:
            row = session.query(StudentModel).first()
            row.department = department
            row.grade = grade
            row.semester = semester
            session.commit()
            return _model_to_schema(row)

    student = _ensure_loaded()[0]
    student.department = department
    student.grade = grade
    student.semester = semester
    return student

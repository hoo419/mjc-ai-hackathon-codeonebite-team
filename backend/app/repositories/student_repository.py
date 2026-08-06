import json
from functools import lru_cache
from pathlib import Path

from app.core import db as db_core
from app.core.config import settings
from app.models import StudentModel
from app.schemas.student import Student


@lru_cache
def _load_raw(data_dir: Path) -> list[dict]:
    path = data_dir / "students.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


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
    return [Student.model_validate(item) for item in _load_raw(settings.data_dir)]


def get_current_student() -> Student:
    """MVP has exactly one mock student; there is no auth yet, so 'current
    student' is always the first (and only) entry."""
    return list_students()[0]

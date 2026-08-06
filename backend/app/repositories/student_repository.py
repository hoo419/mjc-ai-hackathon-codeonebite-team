import json
from functools import lru_cache
from pathlib import Path

from app.core.config import settings
from app.schemas.student import Student


@lru_cache
def _load_raw(data_dir: Path) -> list[dict]:
    path = data_dir / "students.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def list_students() -> list[Student]:
    return [Student.model_validate(item) for item in _load_raw(settings.data_dir)]


def get_current_student() -> Student:
    """MVP has exactly one mock student; there is no auth yet, so 'current
    student' is always the first (and only) entry."""
    return list_students()[0]

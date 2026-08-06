import json
from functools import lru_cache
from pathlib import Path

from app.core.config import settings
from app.schemas.course import Course


@lru_cache
def _load_raw(data_dir: Path) -> list[dict]:
    path = data_dir / "courses.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def list_courses() -> list[Course]:
    """Load all mock courses. Pure read of data/courses.json so this can be
    swapped for a database-backed repository later without touching callers."""
    return [Course.model_validate(item) for item in _load_raw(settings.data_dir)]


def get_course(course_id: str) -> Course | None:
    for course in list_courses():
        if course.id == course_id:
            return course
    return None

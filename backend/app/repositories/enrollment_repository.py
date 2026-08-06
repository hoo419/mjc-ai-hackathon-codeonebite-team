import json
from pathlib import Path

from app.core.config import settings
from app.schemas.enrollment import EnrollmentRecord, EnrollmentStatus

# Enrollment is the one piece of Mock data that gets mutated at runtime
# (POST/DELETE /enrollment), so unlike course/student repositories it can't
# just be an lru_cache'd read of the JSON file - it needs real in-memory
# state that a later database-backed repository would own instead.
_enrollments: list[EnrollmentRecord] | None = None


def _load_from_disk(data_dir: Path) -> list[EnrollmentRecord]:
    path = data_dir / "enrollments.json"
    with path.open(encoding="utf-8") as f:
        raw = json.load(f)
    return [EnrollmentRecord.model_validate(item) for item in raw]


def _ensure_loaded() -> list[EnrollmentRecord]:
    global _enrollments
    if _enrollments is None:
        _enrollments = _load_from_disk(settings.data_dir)
    return _enrollments


def reset() -> None:
    """Reload from data/enrollments.json, discarding in-memory Mock writes.
    Used between tests so POST/DELETE enrollment tests don't leak state."""
    global _enrollments
    _enrollments = _load_from_disk(settings.data_dir)


def list_enrollments_for_student(student_id: str) -> list[EnrollmentRecord]:
    return [e for e in _ensure_loaded() if e.studentId == student_id]


def find_enrollment(student_id: str, course_id: str) -> EnrollmentRecord | None:
    for e in _ensure_loaded():
        if e.studentId == student_id and e.courseId == course_id:
            return e
    return None


def upsert_enrolled(record: EnrollmentRecord) -> None:
    existing = find_enrollment(record.studentId, record.courseId)
    if existing is not None:
        existing.status = record.status
        existing.enrolledAt = record.enrolledAt
    else:
        _ensure_loaded().append(record)


def cancel_enrollment(student_id: str, course_id: str) -> None:
    existing = find_enrollment(student_id, course_id)
    if existing is not None:
        existing.status = EnrollmentStatus.CANCELLED

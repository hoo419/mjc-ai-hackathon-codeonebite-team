import json
from pathlib import Path

from app.core import db as db_core
from app.core.config import settings
from app.models import EnrollmentModel
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


def _model_to_schema(row: EnrollmentModel) -> EnrollmentRecord:
    return EnrollmentRecord(
        studentId=row.student_id,
        courseId=row.course_id,
        status=row.status,
        enrolledAt=row.enrolled_at,
    )


def reset() -> None:
    """Mock mode: reload from data/enrollments.json. DB mode: wipe and
    reseed (course_repository.reset() also does this - calling either is
    enough, but tests may call both; seed.reset_from_mock() is idempotent
    within a single reset call)."""
    global _enrollments
    if settings.database_url:
        from app.core import seed

        seed.reset_from_mock()
        return
    _enrollments = _load_from_disk(settings.data_dir)


def list_enrollments_for_student(student_id: str) -> list[EnrollmentRecord]:
    if settings.database_url:
        with db_core.get_session() as session:
            rows = session.query(EnrollmentModel).filter_by(student_id=student_id).all()
            return [_model_to_schema(row) for row in rows]
    return [e for e in _ensure_loaded() if e.studentId == student_id]


def find_enrollment(student_id: str, course_id: str) -> EnrollmentRecord | None:
    if settings.database_url:
        with db_core.get_session() as session:
            row = (
                session.query(EnrollmentModel)
                .filter_by(student_id=student_id, course_id=course_id)
                .one_or_none()
            )
            return _model_to_schema(row) if row is not None else None
    for e in _ensure_loaded():
        if e.studentId == student_id and e.courseId == course_id:
            return e
    return None


def upsert_enrolled(record: EnrollmentRecord) -> None:
    if settings.database_url:
        with db_core.get_session() as session:
            row = (
                session.query(EnrollmentModel)
                .filter_by(student_id=record.studentId, course_id=record.courseId)
                .one_or_none()
            )
            if row is not None:
                row.status = record.status
                row.enrolled_at = record.enrolledAt
            else:
                session.add(
                    EnrollmentModel(
                        student_id=record.studentId,
                        course_id=record.courseId,
                        status=record.status,
                        enrolled_at=record.enrolledAt,
                    )
                )
            session.commit()
        return

    existing = find_enrollment(record.studentId, record.courseId)
    if existing is not None:
        existing.status = record.status
        existing.enrolledAt = record.enrolledAt
    else:
        _ensure_loaded().append(record)


def cancel_enrollment(student_id: str, course_id: str) -> None:
    if settings.database_url:
        with db_core.get_session() as session:
            row = (
                session.query(EnrollmentModel)
                .filter_by(student_id=student_id, course_id=course_id)
                .one_or_none()
            )
            if row is not None:
                row.status = EnrollmentStatus.CANCELLED
                session.commit()
        return

    existing = find_enrollment(student_id, course_id)
    if existing is not None:
        existing.status = EnrollmentStatus.CANCELLED

import json
from pathlib import Path

from app.core import db
from app.core.config import settings
from app.models import CourseModel, EnrollmentModel, StudentModel


def _load_json(name: str) -> list[dict]:
    path = settings.data_dir / name
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def seed_if_empty() -> None:
    """Populate courses/students/enrollments from data/*.json the first
    time the database is empty. Safe to call on every startup - it's a
    no-op once seeded. This keeps data/*.json as the single source of
    truth for Mock content whether the app is running with or without a
    database."""
    with db.get_session() as session:
        if session.query(CourseModel).first() is not None:
            return  # already seeded

        # Committed in FK dependency order (enrollments references both
        # courses and students) - one flush mixing all three confused
        # SQLAlchemy's insert ordering against a real Postgres FK constraint.
        for item in _load_json("courses.json"):
            session.add(
                CourseModel(
                    id=item["id"],
                    name=item["name"],
                    professor=item["professor"],
                    credits=item["credits"],
                    category=item["category"],
                    class_type=item["classType"],
                    sessions_json=json.dumps(item["sessions"], ensure_ascii=False),
                    target_grade=item["targetGrade"],
                    eligible_depts_json=json.dumps(item["eligibleDepts"], ensure_ascii=False),
                    capacity=item["capacity"],
                    enrolled=item["enrolled"],
                    status=item["status"],
                    last_updated=item["lastUpdated"],
                )
            )
        session.commit()

        for item in _load_json("students.json"):
            session.add(
                StudentModel(
                    id=item["id"],
                    name=item["name"],
                    department=item["department"],
                    grade=item["grade"],
                    semester=item["semester"],
                )
            )
        session.commit()

        for item in _load_json("enrollments.json"):
            session.add(
                EnrollmentModel(
                    student_id=item["studentId"],
                    course_id=item["courseId"],
                    status=item["status"],
                    enrolled_at=item["enrolledAt"],
                )
            )
        session.commit()


def reset_from_mock(data_dir: Path | None = None) -> None:
    """Wipe and reseed - used between tests so DB-mode tests don't leak
    state, mirroring the Mock repositories' reset()."""
    with db.get_session() as session:
        session.query(EnrollmentModel).delete()
        session.query(CourseModel).delete()
        session.query(StudentModel).delete()
        session.commit()
    seed_if_empty()

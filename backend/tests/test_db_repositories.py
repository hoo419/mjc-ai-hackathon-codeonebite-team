from app.core import db as db_core
from app.core import seed
from app.core.config import settings
from app.models import CourseModel, EnrollmentModel, StudentModel
from app.repositories import course_repository, enrollment_repository, student_repository
from app.schemas.enrollment import EnrollmentRecord, EnrollmentStatus


def _use_sqlite_db(monkeypatch, tmp_path):
    """Points every repository at a throwaway SQLite file for this test
    only, seeded from the same data/*.json used by Mock mode. Called
    explicitly inside each test body (not as a fixture) so it always runs
    after conftest's autouse `default_to_mock_mode` fixture has already
    forced settings.database_url back to None - fixture setup order across
    conftest.py and a test module isn't guaranteed otherwise."""
    db_url = f"sqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setattr(settings, "database_url", db_url)
    db_core.init_engine(db_url)
    seed.seed_if_empty()


def test_db_get_course_reads_live_database_state_not_json(monkeypatch, tmp_path):
    _use_sqlite_db(monkeypatch, tmp_path)

    # Mutate the DB directly, bypassing the repository entirely - proves
    # get_course() is actually querying the database, not a JSON-loaded
    # in-memory copy.
    with db_core.get_session() as session:
        row = session.get(CourseModel, "J00105-101")
        row.enrolled = 999
        session.commit()

    course = course_repository.get_course("J00105-101")
    assert course.enrolled == 999


def test_db_increment_enrolled_writes_to_database(monkeypatch, tmp_path):
    _use_sqlite_db(monkeypatch, tmp_path)

    course_repository.increment_enrolled("J00105-101")

    with db_core.get_session() as session:
        row = session.get(CourseModel, "J00105-101")
        assert row.enrolled == 31  # seeded at 30 (capacity 35, OPEN)


def test_db_decrement_enrolled_writes_to_database(monkeypatch, tmp_path):
    _use_sqlite_db(monkeypatch, tmp_path)

    course_repository.decrement_enrolled("J00936-101")  # seeded at 30/30 (FULL)

    with db_core.get_session() as session:
        row = session.get(CourseModel, "J00936-101")
        assert row.enrolled == 29
        assert row.status == "OPEN"


def test_db_get_current_student_reads_live_database_state(monkeypatch, tmp_path):
    _use_sqlite_db(monkeypatch, tmp_path)

    with db_core.get_session() as session:
        row = session.get(StudentModel, "mock-student-001")
        row.grade = 4
        session.commit()

    student = student_repository.get_current_student()
    assert student.grade == 4


def test_db_enrollment_upsert_writes_to_database(monkeypatch, tmp_path):
    _use_sqlite_db(monkeypatch, tmp_path)

    record = EnrollmentRecord(
        studentId="mock-student-001",
        courseId="J01840-101",
        status=EnrollmentStatus.ENROLLED,
        enrolledAt="2026-01-01T00:00:00+09:00",
    )
    enrollment_repository.upsert_enrolled(record)

    with db_core.get_session() as session:
        row = (
            session.query(EnrollmentModel)
            .filter_by(student_id="mock-student-001", course_id="J01840-101")
            .one()
        )
        assert row.status == "ENROLLED"


def test_db_enrollment_cancel_writes_to_database(monkeypatch, tmp_path):
    _use_sqlite_db(monkeypatch, tmp_path)

    # T00138-101 is seeded (data/enrollments.json) as an existing ENROLLED
    # row for mock-student-001.
    enrollment_repository.cancel_enrollment("mock-student-001", "T00138-101")

    with db_core.get_session() as session:
        row = (
            session.query(EnrollmentModel)
            .filter_by(student_id="mock-student-001", course_id="T00138-101")
            .one()
        )
        assert row.status == "CANCELLED"

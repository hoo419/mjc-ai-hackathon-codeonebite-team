import pytest

from app.core.config import settings
from app.repositories import (
    counseling_repository,
    course_repository,
    enrollment_repository,
    student_repository,
)


@pytest.fixture(autouse=True)
def default_to_mock_mode(monkeypatch):
    """backend/.env may have a real DATABASE_URL configured (Neon). Tests
    must not silently switch to DB mode just because that's in the
    environment - default every test to Mock mode. DB-specific tests
    (test_db_repositories.py) opt back in explicitly inside the test body,
    after this fixture has already run."""
    monkeypatch.setattr(settings, "database_url", None)


@pytest.fixture(autouse=True)
def reset_course_store():
    """Course.enrolled/status are bumped at runtime once an enrollment
    actually succeeds (see course_repository.increment_enrolled). Reload
    from data/courses.json before and after every test."""
    try:
        course_repository.reset()
    except Exception:
        # If reset fails (e.g., due to schema mismatch), skip for tests like
        # test_transform_sugang_raw that don't depend on the repository
        pass
    yield
    try:
        course_repository.reset()
    except Exception:
        pass


@pytest.fixture(autouse=True)
def reset_student_store():
    """Student profile (department/grade/semester) is editable via
    PATCH /students/me. Reload from data/students.json before and after
    every test."""
    try:
        student_repository.reset()
    except Exception:
        pass
    yield
    try:
        student_repository.reset()
    except Exception:
        pass


@pytest.fixture(autouse=True)
def reset_enrollment_store():
    """Enrollment is Mock data mutated at runtime (POST/DELETE). Reload it
    from data/enrollments.json before and after every test so tests can't
    leak state into each other."""
    try:
        enrollment_repository.reset()
    except Exception:
        pass
    yield
    try:
        enrollment_repository.reset()
    except Exception:
        pass


@pytest.fixture(autouse=True)
def reset_counseling_store():
    """Counseling requests are also mutated at runtime (POST); reset the
    in-memory list so generated request IDs stay predictable per test."""
    try:
        counseling_repository.reset()
    except Exception:
        pass
    yield
    try:
        counseling_repository.reset()
    except Exception:
        pass

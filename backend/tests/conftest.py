import pytest

from app.core.config import settings
from app.repositories import (
    counseling_repository,
    course_repository,
    enrollment_repository,
    notice_repository,
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
    course_repository.reset()
    yield
    course_repository.reset()


@pytest.fixture(autouse=True)
def reset_student_store():
    """Student profile (department/grade/semester) is editable via
    PATCH /students/me. Reload from data/students.json before and after
    every test."""
    student_repository.reset()
    yield
    student_repository.reset()


@pytest.fixture(autouse=True)
def reset_enrollment_store():
    """Enrollment is Mock data mutated at runtime (POST/DELETE). Reload it
    from data/enrollments.json before and after every test so tests can't
    leak state into each other."""
    enrollment_repository.reset()
    yield
    enrollment_repository.reset()


@pytest.fixture(autouse=True)
def reset_counseling_store():
    """Counseling requests are also mutated at runtime (POST); reset the
    in-memory list so generated request IDs stay predictable per test."""
    counseling_repository.reset()
    yield
    counseling_repository.reset()


@pytest.fixture(autouse=True)
def reset_notice_store():
    """notice_repository caches the live-scraped 학사공지 list in memory
    (6h TTL) - reset it so a test's monkeypatched fetch, or a real network
    hit, never leaks into the next test."""
    notice_repository.reset()
    yield
    notice_repository.reset()

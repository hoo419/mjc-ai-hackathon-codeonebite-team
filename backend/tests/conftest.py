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
def reset_course_store(request):
    """Course.enrolled/status are bumped at runtime once an enrollment
    actually succeeds (see course_repository.increment_enrolled). Reload
    from data/courses.json before and after every test."""
    # Skip for test_transform_sugang_raw.py which doesn't depend on repos
    if request.node.fspath.basename != "test_transform_sugang_raw.py":
        course_repository.reset()
    yield
    if request.node.fspath.basename != "test_transform_sugang_raw.py":
        course_repository.reset()


@pytest.fixture(autouse=True)
def reset_student_store(request):
    """Student profile (department/grade/semester) is editable via
    PATCH /students/me. Reload from data/students.json before and after
    every test."""
    if request.node.fspath.basename != "test_transform_sugang_raw.py":
        student_repository.reset()
    yield
    if request.node.fspath.basename != "test_transform_sugang_raw.py":
        student_repository.reset()


@pytest.fixture(autouse=True)
def reset_enrollment_store(request):
    """Enrollment is Mock data mutated at runtime (POST/DELETE). Reload it
    from data/enrollments.json before and after every test so tests can't
    leak state into each other."""
    if request.node.fspath.basename != "test_transform_sugang_raw.py":
        enrollment_repository.reset()
    yield
    if request.node.fspath.basename != "test_transform_sugang_raw.py":
        enrollment_repository.reset()


@pytest.fixture(autouse=True)
def reset_counseling_store(request):
    """Counseling requests are also mutated at runtime (POST); reset the
    in-memory list so generated request IDs stay predictable per test."""
    if request.node.fspath.basename != "test_transform_sugang_raw.py":
        counseling_repository.reset()
    yield
    if request.node.fspath.basename != "test_transform_sugang_raw.py":
        counseling_repository.reset()

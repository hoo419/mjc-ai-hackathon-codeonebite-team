import pytest

from app.repositories import counseling_repository, course_repository, enrollment_repository


@pytest.fixture(autouse=True)
def reset_course_store():
    """Course.enrolled/status are bumped at runtime once an enrollment
    actually succeeds (see course_repository.increment_enrolled). Reload
    from data/courses.json before and after every test."""
    course_repository.reset()
    yield
    course_repository.reset()


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

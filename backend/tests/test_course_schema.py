import pytest

from app.schemas.course import Course


@pytest.fixture(autouse=True)
def reset_course_store():
    """Override autouse fixture from conftest.py - schema tests don't need repo reset."""
    yield


@pytest.fixture(autouse=True)
def reset_student_store():
    """Override autouse fixture from conftest.py - schema tests don't need repo reset."""
    yield


@pytest.fixture(autouse=True)
def reset_enrollment_store():
    """Override autouse fixture from conftest.py - schema tests don't need repo reset."""
    yield


@pytest.fixture(autouse=True)
def reset_counseling_store():
    """Override autouse fixture from conftest.py - schema tests don't need repo reset."""
    yield


def test_course_accepts_sessions_array_and_new_category():
    course = Course.model_validate(
        {
            "id": "T00137-101",
            "name": "딥러닝",
            "professor": "윤현구",
            "credits": 3,
            "category": "MAJOR_COURSE",
            "classType": "OFFLINE",
            "sessions": [
                {"day": "TUE", "startTime": "13:25", "endTime": "14:50", "building": None, "room": "공502"},
                {"day": "WED", "startTime": "10:25", "endTime": "11:50", "building": None, "room": "공502"},
            ],
            "targetGrade": 1,
            "eligibleDepts": [{"code": "1200203", "name": "컴퓨터공학과"}],
            "capacity": 35,
            "enrolled": 30,
            "status": "OPEN",
            "lastUpdated": "2026-08-07T00:00:00+09:00",
        }
    )

    assert len(course.sessions) == 2
    assert course.sessions[0].day == "TUE"
    assert course.eligibleDepts[0].name == "컴퓨터공학과"
    assert course.targetGrade == 1


def test_course_classtype_can_be_null_for_remote_courses():
    course = Course.model_validate(
        {
            "id": "T00138-101",
            "name": "AI활용웹개발",
            "professor": "정지영",
            "credits": 2,
            "category": "INTEGRATED_MAJOR",
            "classType": None,
            "sessions": [],
            "targetGrade": 1,
            "eligibleDepts": [{"code": "1201301", "name": "통합전공"}],
            "capacity": 30,
            "enrolled": 0,
            "status": "OPEN",
            "lastUpdated": "2026-08-07T00:00:00+09:00",
        }
    )

    assert course.classType is None
    assert course.sessions == []

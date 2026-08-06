from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_current_student_returns_mock_student():
    response = client.get("/api/students/me")

    assert response.status_code == 200
    student = response.json()["student"]
    assert student == {
        "id": "mock-student-001",
        "name": "홍길동",
        "department": "컴퓨터공학과",
        "grade": 3,
        "semester": 1,
    }


def test_get_current_student_courses_returns_enrolled_courses_only():
    response = client.get("/api/students/me/courses")

    assert response.status_code == 200
    courses = response.json()["courses"]
    course_ids = {c["id"] for c in courses}
    assert course_ids == {"CS301-01", "GE101-01"}
    # Full course objects, not just enrollment records.
    assert "status" in courses[0]
    assert "capacity" in courses[0]


def test_get_current_student_schedule_returns_weekly_schedule():
    response = client.get("/api/students/me/schedule")

    assert response.status_code == 200
    schedule = response.json()["schedule"]
    assert len(schedule) == 2
    item = next(s for s in schedule if s["courseId"] == "CS301-01")
    assert item == {
        "courseId": "CS301-01",
        "name": "인공지능 프로그래밍",
        "professor": "김민준",
        "classType": "OFFLINE",
        "day": "THU",
        "startTime": "13:00",
        "endTime": "15:50",
        "building": "공학관",
        "room": "503",
    }

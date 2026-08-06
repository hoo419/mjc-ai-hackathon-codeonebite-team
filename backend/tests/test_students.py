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
    assert course_ids == {"T00138-101", "J01683-101"}
    assert "status" in courses[0]
    assert "capacity" in courses[0]


def test_patch_current_student_updates_profile_and_persists():
    response = client.patch(
        "/api/students/me",
        json={"department": "소프트웨어학과", "grade": 2, "semester": 2},
    )

    assert response.status_code == 200
    assert response.json() == {
        "student": {
            "id": "mock-student-001",
            "name": "홍길동",
            "department": "소프트웨어학과",
            "grade": 2,
            "semester": 2,
        }
    }

    follow_up = client.get("/api/students/me")
    assert follow_up.json()["student"]["department"] == "소프트웨어학과"
    assert follow_up.json()["student"]["grade"] == 2
    assert follow_up.json()["student"]["semester"] == 2


def test_get_current_student_schedule_returns_one_item_per_session():
    response = client.get("/api/students/me/schedule")

    assert response.status_code == 200
    schedule = response.json()["schedule"]
    # T00138-101은 세션 1개(FRI 11:00-11:50), J01683-101도 세션 1개(TUE 09:25-10:25).
    assert len(schedule) == 2
    item = next(s for s in schedule if s["courseId"] == "T00138-101")
    assert item == {
        "courseId": "T00138-101",
        "name": "AI활용웹개발",
        "professor": "정필성",
        "classType": None,
        "day": "FRI",
        "startTime": "11:00",
        "endTime": "11:50",
        "building": None,
        "room": " ",
    }

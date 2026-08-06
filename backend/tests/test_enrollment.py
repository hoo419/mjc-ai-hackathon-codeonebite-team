from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_enroll_open_course_with_no_conflict_succeeds():
    response = client.post("/api/enrollment", json={"courseId": "CS220-01"})

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "success": True,
        "enrollment": {"courseId": "CS220-01", "status": "ENROLLED"},
    }


def test_enroll_already_enrolled_course_returns_error():
    response = client.post("/api/enrollment", json={"courseId": "CS301-01"})

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "ALREADY_ENROLLED"


def test_enroll_cancelled_course_returns_error():
    response = client.post("/api/enrollment", json={"courseId": "CS330-01"})

    assert response.json()["error"]["code"] == "COURSE_CANCELLED"


def test_enroll_full_course_returns_error():
    response = client.post("/api/enrollment", json={"courseId": "CS301-02"})

    assert response.json()["error"]["code"] == "COURSE_FULL"


def test_enroll_upcoming_course_returns_enrollment_closed():
    response = client.post("/api/enrollment", json={"courseId": "CS360-01"})

    assert response.json()["error"]["code"] == "ENROLLMENT_CLOSED"


def test_enroll_time_conflicting_course_returns_error():
    # Student already has GE101-01 on MON 10:00-11:50.
    # CS210-01 is MON 09:00-11:50 -> overlaps.
    response = client.post("/api/enrollment", json={"courseId": "CS210-01"})

    assert response.json()["error"]["code"] == "TIME_CONFLICT"


def test_enroll_nonexistent_course_returns_error():
    response = client.post("/api/enrollment", json={"courseId": "NOPE-01"})

    assert response.json()["error"]["code"] == "COURSE_NOT_FOUND"


def test_enroll_then_appears_in_student_courses():
    client.post("/api/enrollment", json={"courseId": "CS220-01"})

    response = client.get("/api/students/me/courses")

    course_ids = {c["id"] for c in response.json()["courses"]}
    assert "CS220-01" in course_ids


def test_delete_enrollment_returns_success_and_removes_course():
    response = client.delete("/api/enrollment/CS301-01")

    assert response.status_code == 200
    assert response.json() == {"success": True}

    remaining = client.get("/api/students/me/courses").json()["courses"]
    assert "CS301-01" not in {c["id"] for c in remaining}


def test_delete_enrollment_for_unenrolled_course_is_idempotent():
    response = client.delete("/api/enrollment/CS220-01")

    assert response.status_code == 200
    assert response.json() == {"success": True}

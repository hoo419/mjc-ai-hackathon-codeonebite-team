from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# mock-student-001은 data/enrollments.json 기준으로 이미
# T00138-101(FRI 11:00-11:50)와 J01683-101(TUE 09:25-10:25)을 신청한 상태.


def test_enroll_open_course_with_no_conflict_succeeds():
    # J00105-102: WED 14:00/15:00/16:00 - 기존 두 과목과 요일이 안 겹침.
    response = client.post("/api/enrollment", json={"courseId": "J00105-102"})

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "success": True,
        "enrollment": {"courseId": "J00105-102", "status": "ENROLLED"},
    }


def test_enroll_already_enrolled_course_returns_error():
    response = client.post("/api/enrollment", json={"courseId": "T00138-101"})

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "ALREADY_ENROLLED"


def test_enroll_time_conflicting_course_returns_error():
    # J00105-101은 FRI 11:00-11:50 세션을 포함 - T00138-101(FRI 11:00-11:50)과 겹침.
    response = client.post("/api/enrollment", json={"courseId": "J00105-101"})

    assert response.json()["error"]["code"] == "TIME_CONFLICT"


def test_enroll_nonexistent_course_returns_error():
    response = client.post("/api/enrollment", json={"courseId": "NOPE-01"})

    assert response.json()["error"]["code"] == "COURSE_NOT_FOUND"


def test_enroll_then_appears_in_student_courses():
    client.post("/api/enrollment", json={"courseId": "J00105-102"})

    response = client.get("/api/students/me/courses")

    course_ids = {c["id"] for c in response.json()["courses"]}
    assert "J00105-102" in course_ids


def test_enroll_full_course_no_longer_blocked():
    """수강신청은 실제로는 학생이 sugang.mjc.ac.kr에서 이미 완료한 것을
    우리 시간표에 기록하는 것뿐이라, 정원 검증은 더 이상 우리 쪽에서 하지
    않는다. J00936-101은 capacity=enrolled=30(FULL)이지만 신청 기록은
    성공해야 한다. (CANCELLED/UPCOMING 시나리오는 실데이터에 그 상태가
    존재하지 않아 검증하지 않는다 - 지어내지 않는다는 원칙.)"""
    response = client.post("/api/enrollment", json={"courseId": "J00936-101"})

    assert response.json()["success"] is True


def test_delete_enrollment_returns_success_and_removes_course():
    response = client.delete("/api/enrollment/T00138-101")

    assert response.status_code == 200
    assert response.json() == {"success": True}

    remaining = client.get("/api/students/me/courses").json()["courses"]
    assert "T00138-101" not in {c["id"] for c in remaining}


def test_delete_enrollment_for_unenrolled_course_is_idempotent():
    response = client.delete("/api/enrollment/J00105-102")

    assert response.status_code == 200
    assert response.json() == {"success": True}

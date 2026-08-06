from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_courses_returns_all_mock_courses():
    response = client.get("/api/courses")

    assert response.status_code == 200
    body = response.json()
    assert "courses" in body
    assert len(body["courses"]) >= 15
    first = body["courses"][0]
    assert set(first.keys()) == {
        "id",
        "name",
        "professor",
        "credits",
        "category",
        "classType",
        "day",
        "startTime",
        "endTime",
        "building",
        "room",
        "capacity",
        "enrolled",
        "status",
        "lastUpdated",
    }


def test_list_courses_filters_by_status():
    response = client.get("/api/courses", params={"status": "CANCELLED"})

    assert response.status_code == 200
    courses = response.json()["courses"]
    assert len(courses) >= 1
    assert all(course["status"] == "CANCELLED" for course in courses)


def test_list_courses_filters_by_class_type():
    response = client.get("/api/courses", params={"classType": "ONLINE_LIVE"})

    assert response.status_code == 200
    courses = response.json()["courses"]
    assert len(courses) >= 1
    assert all(course["classType"] == "ONLINE_LIVE" for course in courses)


def test_list_courses_filters_by_category():
    response = client.get("/api/courses", params={"category": "GENERAL_ELECTIVE"})

    assert response.status_code == 200
    courses = response.json()["courses"]
    assert len(courses) >= 1
    assert all(course["category"] == "GENERAL_ELECTIVE" for course in courses)


def test_list_courses_search_matches_course_name():
    response = client.get("/api/courses", params={"search": "인공지능"})

    assert response.status_code == 200
    courses = response.json()["courses"]
    assert len(courses) >= 1
    assert all("인공지능" in course["name"] for course in courses)


def test_get_course_by_id_returns_course_detail():
    response = client.get("/api/courses/CS301-01")

    assert response.status_code == 200
    course = response.json()["course"]
    assert course["id"] == "CS301-01"
    assert course["name"] == "인공지능 프로그래밍"


def test_get_course_by_id_returns_404_with_contract_error_shape():
    response = client.get("/api/courses/NOT-EXIST-01")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "COURSE_NOT_FOUND"
    assert "message" in body["error"]

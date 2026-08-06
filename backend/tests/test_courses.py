from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_courses_returns_all_mock_courses():
    response = client.get("/api/courses")

    assert response.status_code == 200
    body = response.json()
    assert "courses" in body
    assert len(body["courses"]) == 246
    first = body["courses"][0]
    assert set(first.keys()) == {
        "id",
        "name",
        "professor",
        "credits",
        "category",
        "classType",
        "sessions",
        "targetGrade",
        "eligibleDepts",
        "capacity",
        "enrolled",
        "status",
        "lastUpdated",
    }


def test_list_courses_filters_by_status():
    response = client.get("/api/courses", params={"status": "FULL"})

    assert response.status_code == 200
    courses = response.json()["courses"]
    assert len(courses) >= 1
    assert all(course["status"] == "FULL" for course in courses)


def test_list_courses_filters_by_category():
    response = client.get("/api/courses", params={"category": "MAJOR_COURSE"})

    assert response.status_code == 200
    courses = response.json()["courses"]
    assert len(courses) >= 1
    assert all(course["category"] == "MAJOR_COURSE" for course in courses)


def test_list_courses_search_matches_course_name():
    response = client.get("/api/courses", params={"search": "AI활용웹개발"})

    assert response.status_code == 200
    courses = response.json()["courses"]
    assert len(courses) >= 1
    assert all("AI활용웹개발" in course["name"] for course in courses)


def test_get_course_by_id_returns_course_detail():
    response = client.get("/api/courses/T00138-101")

    assert response.status_code == 200
    course = response.json()["course"]
    assert course["id"] == "T00138-101"
    assert course["name"] == "AI활용웹개발"


def test_get_course_by_id_returns_404_with_contract_error_shape():
    response = client.get("/api/courses/NOT-EXIST-01")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "COURSE_NOT_FOUND"
    assert "message" in body["error"]

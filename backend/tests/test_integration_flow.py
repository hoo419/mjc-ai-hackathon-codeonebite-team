from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_full_flow_chat_search_enroll_schedule_and_capacity_updates():
    """PROJECT_REQUIREMENTS.md 7절 완료 판단 기준 시나리오를 끝까지 확인한다:
    사용자 -> Chat API -> Course 조건 검사 -> 과목 선택 -> 수강신청 ->
    시간표 반영 -> 교수/시간/수업방식/강의실/상태 확인, 그리고 신청 후
    잔여석이 실제로 줄어드는지까지 본다."""
    chat_response = client.post(
        "/api/chat", json={"message": "지금 신청 가능한 온라인 과목 알려줘."}
    )
    assert chat_response.status_code == 200
    chat_body = chat_response.json()
    assert chat_body["answer"]
    assert chat_body["courses"], "추천된 과목이 없습니다"
    assert all(c["status"] == "OPEN" for c in chat_body["courses"])

    # mock-student-001 is already enrolled in a couple of courses (seeded
    # via data/enrollments.json) - skip past those so the enroll call below
    # actually succeeds instead of returning ALREADY_ENROLLED. Also require
    # at least one session so the schedule-matching assertions below have
    # something to compare against.
    already_enrolled_ids = {
        item["courseId"]
        for item in client.get("/api/students/me/schedule").json()["schedule"]
    }
    chosen = next(
        c
        for c in chat_body["courses"]
        if c["id"] not in already_enrolled_ids and c["sessions"]
    )
    course_id = chosen["id"]
    assert any(a["targetId"] == course_id for a in chat_body["actions"])

    before = client.get(f"/api/courses/{course_id}").json()["course"]
    remaining_before = before["capacity"] - before["enrolled"]

    enroll_response = client.post("/api/enrollment", json={"courseId": course_id})
    assert enroll_response.status_code == 200
    assert enroll_response.json() == {
        "success": True,
        "enrollment": {"courseId": course_id, "status": "ENROLLED"},
    }

    schedule = client.get("/api/students/me/schedule").json()["schedule"]
    scheduled = next((s for s in schedule if s["courseId"] == course_id), None)
    assert scheduled is not None
    chosen_session = chosen["sessions"][0]
    assert scheduled["name"] == chosen["name"]
    assert scheduled["professor"] == chosen["professor"]
    assert scheduled["classType"] == chosen["classType"]
    assert scheduled["day"] == chosen_session["day"]
    assert scheduled["startTime"] == chosen_session["startTime"]
    assert scheduled["endTime"] == chosen_session["endTime"]
    assert scheduled["building"] == chosen_session["building"]
    assert scheduled["room"] == chosen_session["room"]

    after = client.get(f"/api/courses/{course_id}").json()["course"]
    assert after["enrolled"] == before["enrolled"] + 1
    assert after["capacity"] - after["enrolled"] == remaining_before - 1

    cancel_response = client.delete(f"/api/enrollment/{course_id}")
    assert cancel_response.status_code == 200
    assert cancel_response.json() == {"success": True}

    schedule_after_cancel = client.get("/api/students/me/schedule").json()["schedule"]
    assert all(s["courseId"] != course_id for s in schedule_after_cancel)

    restored = client.get(f"/api/courses/{course_id}").json()["course"]
    assert restored["enrolled"] == before["enrolled"]
    assert restored["capacity"] - restored["enrolled"] == remaining_before

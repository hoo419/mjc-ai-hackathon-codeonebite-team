from fastapi.testclient import TestClient

from app.main import app
from app.repositories import campus_repository

client = TestClient(app)


def test_list_buildings_returns_real_campus_buildings():
    response = client.get("/api/buildings")

    assert response.status_code == 200
    buildings = response.json()["buildings"]
    assert {"id": "engineering", "name": "공학관"} in buildings


def test_get_room_returns_a_real_room_derived_from_course_data():
    # data/rooms.json is derived from real course room codes (id == the
    # code itself, e.g. "공502") - pick any real one at runtime instead of
    # hardcoding, so this test survives a future data refresh.
    room_id = campus_repository.list_rooms()[0].id

    response = client.get(f"/api/rooms/{room_id}")

    assert response.status_code == 200
    room = response.json()["room"]
    assert room["id"] == room_id
    assert room["building"] in {"공학관", "본관", "사회교육관", "예술관 (Art & Design House)"}
    assert isinstance(room["floor"], int)
    # 실제 길찾기 문구는 지어내지 않기로 했으므로 항상 빈 배열이어야 한다.
    assert room["directions"] == []


def test_get_room_returns_404_with_error_shape_when_not_found():
    response = client.get("/api/rooms/nonexistent-room")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "ROOM_NOT_FOUND"
    assert "message" in body["error"]

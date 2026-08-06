from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_buildings_returns_mock_buildings():
    response = client.get("/api/buildings")

    assert response.status_code == 200
    buildings = response.json()["buildings"]
    assert {"id": "engineering", "name": "공학관"} in buildings


def test_get_room_returns_directions():
    response = client.get("/api/rooms/engineering-503")

    assert response.status_code == 200
    room = response.json()["room"]
    assert room["building"] == "공학관"
    assert room["floor"] == 5
    assert room["room"] == "503"
    assert len(room["directions"]) >= 1


def test_get_room_returns_404_with_error_shape_when_not_found():
    response = client.get("/api/rooms/nonexistent-room")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "ROOM_NOT_FOUND"
    assert "message" in body["error"]

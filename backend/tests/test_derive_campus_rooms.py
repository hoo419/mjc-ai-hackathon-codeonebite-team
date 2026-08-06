import pytest

from scripts.derive_campus_rooms import build_building_name, derive_room_entry, parse_room_code


def test_parse_room_code_regular_floor():
    assert parse_room_code("공501") == {"prefix": "공", "floor": 5, "roomNumber": "501"}


def test_parse_room_code_basement_floor():
    # "공B101" - 공학관 지하1층 101호. 코드의 B는 지하를 뜻하고, 나머지 규칙(첫 자리=층)은 동일.
    assert parse_room_code("공B101") == {"prefix": "공", "floor": -1, "roomNumber": "101"}


def test_parse_room_code_unknown_format_raises():
    with pytest.raises(ValueError):
        parse_room_code("abc")


def test_build_building_name_known_prefix():
    assert build_building_name("예") == "예술관 (Art & Design House)"


def test_build_building_name_unknown_prefix_raises():
    with pytest.raises(ValueError):
        build_building_name("X")


def test_derive_room_entry_shape():
    assert derive_room_entry("본615") == {
        "id": "본615",
        "building": "본관",
        "floor": 6,
        "room": "615",
        "directions": [],
    }

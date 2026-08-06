"""data/courses.json에 실제로 등장하는 강의실 코드를 뽑아 data/rooms.json을
생성하는 1회성 스크립트. 지어낸 강의실을 넣지 않기 위해, 실제 강좌가 쓰는
강의실만 대상으로 삼는다.

건물 접두문자는 캠퍼스 배치도(www.mjc.ac.kr)에서 확인한 실제 건물명과
사용자 확인을 거쳐 정한 것이다. 층수는 사용자가 알려준 표기 규칙을 그대로
따른다: 강의실 코드 첫 자리가 층수(예: 501 -> 5층, 813 -> 8층). "B"가 붙으면
지하층이며(예: B101 -> 지하1층), 나머지 규칙은 동일하다.

상세 길찾기 문구(directions)는 실제 정보가 없어 지어내지 않고 항상 빈
배열로 둔다.
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COURSES_PATH = REPO_ROOT / "data" / "courses.json"
ROOMS_OUT_PATH = REPO_ROOT / "data" / "rooms.json"

BUILDING_MAP = {
    "본": "본관",
    "공": "공학관",
    "사": "사회교육관",
    "예": "예술관 (Art & Design House)",
}

_CODE_RE = re.compile(r"^([가-힣]+)(B)?(\d{3})$")


def parse_room_code(code: str) -> dict:
    match = _CODE_RE.match(code)
    if match is None:
        raise ValueError(f"알 수 없는 강의실 코드 형식: {code!r}")
    prefix, is_basement, number = match.groups()
    floor = int(number[0])
    if is_basement:
        floor = -floor
    return {"prefix": prefix, "floor": floor, "roomNumber": number}


def build_building_name(prefix: str) -> str:
    if prefix not in BUILDING_MAP:
        raise ValueError(f"알 수 없는 건물 접두문자: {prefix!r}")
    return BUILDING_MAP[prefix]


def derive_room_entry(code: str) -> dict:
    parsed = parse_room_code(code)
    return {
        "id": code,
        "building": build_building_name(parsed["prefix"]),
        "floor": parsed["floor"],
        "room": parsed["roomNumber"],
        "directions": [],
    }


def collect_real_room_codes() -> list[str]:
    courses = json.loads(COURSES_PATH.read_text(encoding="utf-8"))
    codes: set[str] = set()
    for course in courses:
        for session in course["sessions"]:
            room = session.get("room")
            if room and room.strip():
                codes.add(room.strip())
    return sorted(codes)


def main() -> None:
    codes = collect_real_room_codes()
    rooms = [derive_room_entry(code) for code in codes]
    ROOMS_OUT_PATH.write_text(
        json.dumps(rooms, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"wrote {len(rooms)} rooms to {ROOMS_OUT_PATH}")


if __name__ == "__main__":
    main()

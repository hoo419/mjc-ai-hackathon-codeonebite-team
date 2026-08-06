"""원본 sugang 스냅샷(data/raw/sugang_courses_raw_2026_2.json)을
data/courses.json(Course 스키마)으로 변환하는 1회성 스크립트.
재수집 시 다시 실행해서 data/courses.json을 갱신할 수 있도록 리포에 남겨둔다."""

import json
from datetime import datetime
from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = REPO_ROOT / "data" / "raw" / "sugang_courses_raw_2026_2.json"
OUT_PATH = REPO_ROOT / "data" / "courses.json"

DAY_MAP = {
    "월": "MON", "화": "TUE", "수": "WED", "목": "THU",
    "금": "FRI", "토": "SAT", "일": "SUN",
}

CATEGORY_MAP = {
    "교양과정": "GENERAL_COURSE",
    "교양필수": "GENERAL_REQUIRED",
    "일반선택": "GENERAL_ELECTIVE",
    "전공과정": "MAJOR_COURSE",
    "통합전공교과": "INTEGRATED_MAJOR",
}

_SESSION_RE = re.compile(r"^([월화수목금토일])\s+(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})\s*\(\s*(.+?)\s*\)$")


def parse_sessions(time_str: str) -> list[dict]:
    """"화 13:25 - 14:50 ( 공502 ) <br> 수 10:25 - 11:50 ( 공502 )" 같은 원본
    time 문자열을 세션 dict 리스트로 쪼갠다. 빈/공백 문자열은 세션 없음."""
    if not time_str or not time_str.strip():
        return []

    sessions = []
    for segment in time_str.split("<br>"):
        segment = segment.strip()
        if not segment:
            continue
        match = _SESSION_RE.match(segment)
        if match is None:
            raise ValueError(f"세션 문자열을 파싱하지 못함: {segment!r}")
        day_kr, start, end, room = match.groups()
        sessions.append(
            {
                "day": DAY_MAP[day_kr],
                "startTime": start,
                "endTime": end,
                "building": None,
                "room": room,
            }
        )
    return sessions


def transform_row(row: dict) -> dict:
    capacity = int(row["limitNum"])
    enrolled = int(row["inManNum"])
    is_remote = row["sugangGbnCodes"][0] == "60"

    return {
        "id": f"{row['subjectCd']}-{row['bunban']}",
        "name": row["subjectNmKor"],
        "professor": row["nm"],
        "credits": int(row["credit"]),
        "category": CATEGORY_MAP[row["isuCdNm"]],
        "classType": None if is_remote else "OFFLINE",
        "sessions": parse_sessions(row["time"]),
        "targetGrade": int(row["targetGrades"][0]),
        "eligibleDepts": row["depts"],
        "capacity": capacity,
        "enrolled": enrolled,
        "status": "FULL" if enrolled >= capacity else "OPEN",
        "lastUpdated": datetime.now().astimezone().isoformat(timespec="seconds"),
    }


def main() -> None:
    raw_rows = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    courses = [transform_row(row) for row in raw_rows]
    OUT_PATH.write_text(
        json.dumps(courses, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"wrote {len(courses)} courses to {OUT_PATH}")


if __name__ == "__main__":
    main()

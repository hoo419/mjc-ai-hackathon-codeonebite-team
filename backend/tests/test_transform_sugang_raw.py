from scripts.transform_sugang_raw import parse_sessions, transform_row

RAW_MULTI_SESSION = {
    "subjectCd": "T00137",
    "bunban": "101",
    "subjectNmKor": "딥러닝",
    "nm": "윤현구",
    "credit": "3",
    "isuCdNm": "전공과정",
    "time": "화 13:25 - 14:50 ( 공502 ) <br> 수 10:25 - 11:50 ( 공502 )",
    "limitNum": "35",
    "inManNum": "30",
    "sugangGbnCodes": ["30"],
    "targetGrades": ["1"],
    "depts": [{"code": "1200203", "name": "컴퓨터공학과"}],
}

RAW_REMOTE_NO_SESSION = {
    "subjectCd": "T00140",
    "bunban": "104",
    "subjectNmKor": "진로설정동행세미나",
    "nm": "박준성",
    "credit": "1",
    "isuCdNm": "통합전공교과",
    "time": " ",
    "limitNum": "20",
    "inManNum": "20",
    "sugangGbnCodes": ["60"],
    "targetGrades": ["1"],
    "depts": [{"code": "1201301", "name": "통합전공"}],
}

RAW_MULTI_DEPT = {
    "subjectCd": "T00039",
    "bunban": "101",
    "subjectNmKor": "창업실습2",
    "nm": "김창업",
    "credit": "3",
    "isuCdNm": "통합전공교과",
    "time": "수 10:00 - 10:50 ( 예119 )",
    "limitNum": "15",
    "inManNum": "0",
    "sugangGbnCodes": ["30"],
    "targetGrades": ["2"],
    "depts": [
        {"code": "1201301", "name": "통합전공"},
        {"code": "1200301", "name": "경영학과"},
    ],
}


def test_parse_sessions_splits_multiple_br_separated_slots():
    sessions = parse_sessions("화 13:25 - 14:50 ( 공502 ) <br> 수 10:25 - 11:50 ( 공502 )")

    assert sessions == [
        {"day": "TUE", "startTime": "13:25", "endTime": "14:50", "building": None, "room": "공502"},
        {"day": "WED", "startTime": "10:25", "endTime": "11:50", "building": None, "room": "공502"},
    ]


def test_parse_sessions_blank_string_returns_empty_list():
    assert parse_sessions(" ") == []


def test_parse_sessions_skips_exam_scheduling_marker():
    sessions = parse_sessions("금 17:00 - 17:50 ( 공614 ) <br> 원격시험 배정시간")

    assert sessions == [
        {"day": "FRI", "startTime": "17:00", "endTime": "17:50", "building": None, "room": "공614"},
    ]


def test_transform_row_maps_category_and_grade_and_dept():
    course = transform_row(RAW_MULTI_SESSION)

    assert course["id"] == "T00137-101"
    assert course["category"] == "MAJOR_COURSE"
    assert course["classType"] == "OFFLINE"
    assert course["targetGrade"] == 1
    assert course["eligibleDepts"] == [{"code": "1200203", "name": "컴퓨터공학과"}]
    assert course["capacity"] == 35
    assert course["enrolled"] == 30
    assert course["status"] == "OPEN"
    assert len(course["sessions"]) == 2


def test_transform_row_remote_course_has_null_classtype_and_empty_sessions():
    course = transform_row(RAW_REMOTE_NO_SESSION)

    assert course["classType"] is None
    assert course["sessions"] == []
    assert course["category"] == "INTEGRATED_MAJOR"
    assert course["status"] == "FULL"  # enrolled(20) >= capacity(20)


def test_transform_row_keeps_all_eligible_depts():
    course = transform_row(RAW_MULTI_DEPT)

    assert len(course["eligibleDepts"]) == 2
    assert {d["name"] for d in course["eligibleDepts"]} == {"통합전공", "경영학과"}

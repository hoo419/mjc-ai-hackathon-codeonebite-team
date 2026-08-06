from app.repositories import course_repository


def test_increment_enrolled_flips_status_to_full_at_capacity():
    # CS350-01: capacity 40, enrolled 39, status OPEN in data/courses.json.
    course_repository.increment_enrolled("CS350-01")

    updated = course_repository.get_course("CS350-01")
    assert updated.enrolled == 40
    assert updated.status == "FULL"


def test_decrement_enrolled_reverts_full_status_to_open():
    # CS301-02: capacity 30, enrolled 30, status FULL in data/courses.json.
    course_repository.decrement_enrolled("CS301-02")

    updated = course_repository.get_course("CS301-02")
    assert updated.enrolled == 29
    assert updated.status == "OPEN"


def test_decrement_enrolled_never_goes_below_zero():
    course = course_repository.get_course("CS360-01")  # enrolled 0
    for _ in range(3):
        course_repository.decrement_enrolled("CS360-01")

    updated = course_repository.get_course("CS360-01")
    assert updated.enrolled == 0

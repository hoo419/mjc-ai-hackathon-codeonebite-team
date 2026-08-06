from app.repositories import course_repository


def test_increment_enrolled_flips_status_to_full_at_capacity():
    # Pick the OPEN course closest to capacity so the loop below stays short
    # regardless of how big real capacities are (some run to 200+ seats).
    open_courses = [c for c in course_repository.list_courses() if c.status == "OPEN"]
    course = min(open_courses, key=lambda c: c.capacity - c.enrolled)

    for _ in range(course.capacity - course.enrolled):
        course_repository.increment_enrolled(course.id)

    updated = course_repository.get_course(course.id)
    assert updated.enrolled == updated.capacity
    assert updated.status == "FULL"


def test_decrement_enrolled_reverts_full_status_to_open():
    course = next(c for c in course_repository.list_courses() if c.status == "FULL")
    enrolled_before = course.enrolled

    course_repository.decrement_enrolled(course.id)

    updated = course_repository.get_course(course.id)
    assert updated.enrolled == enrolled_before - 1
    assert updated.status == "OPEN"


def test_decrement_enrolled_never_goes_below_zero():
    course = next(c for c in course_repository.list_courses() if c.enrolled == 0)

    for _ in range(3):
        course_repository.decrement_enrolled(course.id)

    updated = course_repository.get_course(course.id)
    assert updated.enrolled == 0

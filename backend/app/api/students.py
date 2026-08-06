from fastapi import APIRouter

from app.schemas.student import (
    ScheduleResponse,
    StudentCoursesResponse,
    StudentProfileUpdate,
    StudentResponse,
)
from app.services import student_service

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/me", response_model=StudentResponse)
def get_me() -> StudentResponse:
    return StudentResponse(student=student_service.get_current_student())


@router.patch("/me", response_model=StudentResponse)
def patch_me(payload: StudentProfileUpdate) -> StudentResponse:
    updated = student_service.update_current_student_profile(
        department=payload.department, grade=payload.grade, semester=payload.semester
    )
    return StudentResponse(student=updated)


@router.get("/me/courses", response_model=StudentCoursesResponse)
def get_me_courses() -> StudentCoursesResponse:
    return StudentCoursesResponse(courses=student_service.get_current_student_courses())


@router.get("/me/schedule", response_model=ScheduleResponse)
def get_me_schedule() -> ScheduleResponse:
    return ScheduleResponse(schedule=student_service.get_current_student_schedule())

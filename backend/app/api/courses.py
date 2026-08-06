from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.course import (
    CourseCategory,
    CourseClassType,
    CourseDetailResponse,
    CourseListResponse,
    CourseStatus,
)
from app.services import course_service

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=CourseListResponse)
def get_courses(
    status: CourseStatus | None = None,
    classType: CourseClassType | None = None,
    category: CourseCategory | None = None,
    search: str | None = None,
) -> CourseListResponse:
    courses = course_service.search_courses(
        status=status, class_type=classType, category=category, search=search
    )
    return CourseListResponse(courses=courses)


@router.get("/{course_id}")
def get_course(course_id: str):
    course = course_service.get_course_by_id(course_id)
    if course is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "COURSE_NOT_FOUND",
                    "message": "과목을 찾을 수 없습니다.",
                }
            },
        )
    return CourseDetailResponse(course=course)

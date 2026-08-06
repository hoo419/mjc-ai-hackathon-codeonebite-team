from fastapi import APIRouter

from app.schemas.notice import NoticeListResponse
from app.services import notice_service

router = APIRouter(prefix="/notices", tags=["notices"])


@router.get("", response_model=NoticeListResponse)
def get_notices() -> NoticeListResponse:
    return NoticeListResponse(notices=notice_service.list_notices())

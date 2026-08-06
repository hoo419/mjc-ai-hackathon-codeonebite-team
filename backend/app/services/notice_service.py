from app.repositories import notice_repository
from app.schemas.notice import Notice


def list_notices() -> list[Notice]:
    return notice_repository.list_notices()

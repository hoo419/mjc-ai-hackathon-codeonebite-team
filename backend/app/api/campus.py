from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.campus import BuildingListResponse, RoomResponse
from app.services import campus_service

router = APIRouter(tags=["campus"])


@router.get("/buildings", response_model=BuildingListResponse)
def get_buildings() -> BuildingListResponse:
    return BuildingListResponse(buildings=campus_service.list_buildings())


@router.get("/rooms/{room_id}")
def get_room(room_id: str):
    room = campus_service.get_room(room_id)
    if room is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "ROOM_NOT_FOUND",
                    "message": "강의실 정보를 찾을 수 없습니다.",
                }
            },
        )
    return RoomResponse(room=room)

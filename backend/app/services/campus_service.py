from app.repositories import campus_repository
from app.schemas.campus import Building, Room


def list_buildings() -> list[Building]:
    return campus_repository.list_buildings()


def get_room(room_id: str) -> Room | None:
    return campus_repository.get_room(room_id)

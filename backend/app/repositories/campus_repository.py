import json
from functools import lru_cache
from pathlib import Path

from app.core.config import settings
from app.schemas.campus import Building, Room


@lru_cache
def _load_buildings_raw(data_dir: Path) -> list[dict]:
    path = data_dir / "buildings.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache
def _load_rooms_raw(data_dir: Path) -> list[dict]:
    path = data_dir / "rooms.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def list_buildings() -> list[Building]:
    return [Building.model_validate(item) for item in _load_buildings_raw(settings.data_dir)]


def list_rooms() -> list[Room]:
    return [Room.model_validate(item) for item in _load_rooms_raw(settings.data_dir)]


def get_room(room_id: str) -> Room | None:
    for item in _load_rooms_raw(settings.data_dir):
        if item["id"] == room_id:
            return Room.model_validate(item)
    return None

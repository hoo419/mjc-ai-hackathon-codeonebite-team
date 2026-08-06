from pydantic import BaseModel


class Building(BaseModel):
    id: str
    name: str


class BuildingListResponse(BaseModel):
    buildings: list[Building]


class Room(BaseModel):
    id: str
    building: str
    floor: int
    room: str
    directions: list[str]


class RoomResponse(BaseModel):
    room: Room

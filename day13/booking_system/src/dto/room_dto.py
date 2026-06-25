from pydantic import BaseModel
from typing import Optional


class RoomCreateDTO(BaseModel):
    hotel_id: int
    number: str
    capacity: int
    price_per_night: float
    room_type: str = "standard"
    external_id: Optional[str] = None


class RoomResponseDTO(BaseModel):
    id: int
    hotel_id: int
    number: str
    capacity: int
    price_per_night: float
    is_active: bool
    room_type: str
    external_id: Optional[str] = None

    @classmethod
    def from_room(cls, room):
        return cls(
            id=room.id,
            hotel_id=room.hotel_id,
            number=room.number,
            capacity=room.capacity,
            price_per_night=room.price_per_night,
            is_active=room.is_active,
            room_type=room.room_type,
            external_id=room.external_id,
        )


class RoomUpdateDTO(BaseModel):
    number: Optional[str] = None
    capacity: Optional[int] = None
    price_per_night: Optional[float] = None
    is_active: Optional[bool] = None
    room_type: Optional[str] = None
    external_id: Optional[str] = None

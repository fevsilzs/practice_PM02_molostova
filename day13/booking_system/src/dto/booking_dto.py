from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional


class BookingCreateDTO(BaseModel):
    room_id: int
    guest_name: str
    guest_email: str
    check_in: date
    check_out: date
    sync_with_external: bool = True

    @field_validator("check_out")
    @classmethod
    def validate_dates(cls, v, info):
        if "check_in" in info.data and v <= info.data["check_in"]:
            raise ValueError("Дата выезда должна быть позже даты заезда")
        if (v - info.data["check_in"]).days > 30:
            raise ValueError("Бронирование не может превышать 30 дней")
        return v


class BookingResponseDTO(BaseModel):
    id: int
    room_id: int
    guest_name: str
    check_in: date
    check_out: date
    total_price: float
    status: str
    created_at: datetime
    external_booking_id: Optional[str] = None
    synced_with_external: bool

    @classmethod
    def from_booking(cls, booking, synced: bool = False):
        return cls(
            id=booking.id,
            room_id=booking.room_id,
            guest_name=booking.guest_name,
            check_in=booking.check_in,
            check_out=booking.check_out,
            total_price=booking.total_price,
            status=booking.status.value,
            created_at=booking.created_at,
            external_booking_id=booking.external_booking_id,
            synced_with_external=synced,
        )


class BookingUpdateDTO(BaseModel):
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None

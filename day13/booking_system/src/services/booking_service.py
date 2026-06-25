from datetime import date, datetime
from typing import List, Optional

from src.domain.models import Booking, BookingStatus
from src.domain.exceptions import (
    BookingConflictError,
    BookingNotFoundError,
    DomainError,
    ExternalAPIConnectionError,
    ExternalRoomNotAvailableError,
    RoomNotFoundError,
)
from src.dto.booking_dto import BookingCreateDTO, BookingResponseDTO, BookingUpdateDTO
from src.services.pricing_service import PricingService
from src.uow.unit_of_work import UnitOfWork
from src.adapters.room_availability_adapter import RoomAvailabilityProvider


class BookingService:
    def __init__(
        self,
        uow: UnitOfWork,
        pricing_service: PricingService,
        availability_provider: RoomAvailabilityProvider,
    ):
        self.uow = uow
        self.pricing_service = pricing_service
        self.availability_provider = availability_provider

    def create(self, dto: BookingCreateDTO) -> BookingResponseDTO:
        room = self.uow.rooms.get_by_id(dto.room_id)
        if not room:
            raise RoomNotFoundError(f"Номер {dto.room_id} не найден")

        if not room.is_active:
            raise RoomNotFoundError(f"Номер {dto.room_id} не активен")

        # Проверяем локальные бронирования
        existing = self.uow.bookings.get_by_room_and_dates(
            dto.room_id, dto.check_in, dto.check_out
        )
        if existing:
            raise BookingConflictError(
                f"Номер {dto.room_id} уже забронирован на эти даты",
                details={"conflicting_bookings": [b.id for b in existing]},
            )

        # Проверяем доступность через внешний API
        external_booking_id = None
        synced = False

        if dto.sync_with_external:
            try:
                external_booking_id = self.availability_provider.book_room(
                    room,
                    dto.guest_name,
                    dto.guest_email,
                    dto.check_in,
                    dto.check_out,
                    total_price=0,
                )
                synced = True
            except ExternalAPIConnectionError:
                synced = False

        # Рассчитываем стоимость
        total_price = self.pricing_service.calculate_price(
            room, dto.check_in, dto.check_out
        )

        booking = Booking(
            id=None,
            room_id=dto.room_id,
            guest_name=dto.guest_name,
            guest_email=dto.guest_email,
            check_in=dto.check_in,
            check_out=dto.check_out,
            total_price=total_price,
            status=BookingStatus.PENDING,
            external_booking_id=external_booking_id,
        )

        saved = self.uow.bookings.add(booking)
        self.uow.commit()

        return BookingResponseDTO.from_booking(saved, synced=synced)

    def cancel(self, booking_id: int) -> bool:
        booking = self.uow.bookings.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(f"Бронирование {booking_id} не найдено")

        if booking.status in (BookingStatus.CHECKED_IN, BookingStatus.CHECKED_OUT):
            raise DomainError(
                f"Нельзя отменить бронирование в статусе {booking.status.value}"
            )

        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = datetime.now()

        self.uow.bookings.update(booking)
        self.uow.commit()

        return True

    def get_available_rooms(
        self,
        hotel_id: int,
        check_in: date,
        check_out: date,
        capacity: Optional[int] = None
    ) -> List[dict]:
        rooms = self.uow.rooms.get_by_hotel(hotel_id, active_only=True)

        if capacity:
            rooms = [r for r in rooms if r.capacity >= capacity]

        available = []
        for room in rooms:
            # Проверяем локально
            existing = self.uow.bookings.get_by_room_and_dates(
                room.id, check_in, check_out
            )
            if existing:
                continue

            # Проверяем через внешний API
            if room.external_id:
                try:
                    ext_result = self.availability_provider.check_availability(
                        room, check_in, check_out
                    )
                    if not ext_result.get("available", False):
                        continue
                except Exception:
                    pass

            available.append({
                'room_id': room.id,
                'number': room.number,
                'capacity': room.capacity,
                'price_per_night': room.price_per_night,
                'external_id': room.external_id
            })

        return available

    def confirm(self, booking_id: int) -> None:
        booking = self.uow.bookings.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(f"Бронирование {booking_id} не найдено")

        if booking.status != BookingStatus.PENDING:
            raise DomainError(
                f"Бронирование в статусе {booking.status.value} нельзя подтвердить"
            )

        booking.status = BookingStatus.CONFIRMED
        self.uow.bookings.update(booking)
        self.uow.commit()

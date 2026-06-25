import random
import time
from datetime import date, datetime
from typing import List, Dict, Optional, Any

from src.domain.exceptions import ExternalAPIConnectionError, ExternalAPIResponseError


class ExternalAPIClient:
    """Мок-клиент для внешнего API системы бронирования"""

    def __init__(self, base_url: str = "https://api.external-booking.com/v1"):
        self.base_url = base_url
        self._rooms: Dict[str, Dict] = {}
        self._bookings: Dict[str, Dict] = {}
        self._next_booking_id = 1000
        self._failure_rate = 0.05
        self._response_delay = 0.1

    def _simulate_network(self) -> None:
        time.sleep(self._response_delay + random.uniform(0, 0.05))

    def _simulate_failure(self) -> None:
        if random.random() < self._failure_rate:
            raise ExternalAPIConnectionError(
                "Внешний API временно недоступен",
                details={"retry_after": random.randint(1, 5)},
            )

    def _generate_external_room_id(self, hotel_id: int, room_number: str) -> str:
        return f"EXT_{hotel_id}_{room_number}"

    def create_room(
        self,
        hotel_id: int,
        room_number: str,
        capacity: int,
        price_per_night: float,
        room_type: str = "standard",
    ) -> Dict:
        self._simulate_network()
        self._simulate_failure()

        external_id = self._generate_external_room_id(hotel_id, room_number)

        room_data = {
            "external_id": external_id,
            "hotel_id": hotel_id,
            "number": room_number,
            "capacity": capacity,
            "price_per_night": price_per_night,
            "room_type": room_type,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
        }

        self._rooms[external_id] = room_data
        return room_data

    def check_room_availability(
        self, external_room_id: str, check_in: date, check_out: date
    ) -> Dict[str, Any]:
        self._simulate_network()
        self._simulate_failure()

        if external_room_id not in self._rooms:
            raise ExternalAPIResponseError(
                f"Номер {external_room_id} не найден во внешней системе"
            )

        room = self._rooms[external_room_id]

        for booking_id, booking in self._bookings.items():
            if booking.get("external_room_id") != external_room_id:
                continue
            if booking.get("status") in ["cancelled", "checked_out"]:
                continue

            b_check_in = datetime.fromisoformat(booking["check_in"]).date()
            b_check_out = datetime.fromisoformat(booking["check_out"]).date()

            if b_check_in < check_out and b_check_out > check_in:
                return {
                    "available": False,
                    "reason": "Room already booked for these dates",
                    "conflicting_booking": booking_id,
                }

        nights = (check_out - check_in).days
        base_price = room["price_per_night"]
        seasonal_coeff = self._get_seasonal_coefficient(check_in)
        price = base_price * nights * seasonal_coeff

        return {
            "available": True,
            "price": round(price, 2),
            "currency": "USD",
            "external_room_id": external_room_id,
        }

    def _get_seasonal_coefficient(self, date_obj: date) -> float:
        month = date_obj.month
        coefficients = {6: 1.2, 7: 1.5, 8: 1.5, 12: 1.4, 1: 1.2}
        return coefficients.get(month, 1.0)

    def check_multiple_rooms_availability(
        self, external_room_ids: List[str], check_in: date, check_out: date
    ) -> Dict[str, Dict]:
        self._simulate_network()
        self._simulate_failure()

        results = {}
        for external_id in external_room_ids:
            try:
                results[external_id] = self.check_room_availability(
                    external_id, check_in, check_out
                )
            except Exception as e:
                results[external_id] = {"available": False, "error": str(e)}

        return results

    def create_booking(
        self,
        external_room_id: str,
        guest_name: str,
        guest_email: str,
        check_in: date,
        check_out: date,
        total_price: float,
    ) -> Dict:
        self._simulate_network()
        self._simulate_failure()

        availability = self.check_room_availability(
            external_room_id, check_in, check_out
        )

        if not availability["available"]:
            raise ExternalAPIResponseError(
                f"Номер {external_room_id} недоступен для бронирования",
                details={"reason": availability.get("reason", "unknown")},
            )

        booking_id = f"EXT_BOOK_{self._next_booking_id}"
        self._next_booking_id += 1

        booking_data = {
            "id": booking_id,
            "external_room_id": external_room_id,
            "guest_name": guest_name,
            "guest_email": guest_email,
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "total_price": total_price,
            "status": "confirmed",
            "created_at": datetime.now().isoformat(),
        }

        self._bookings[booking_id] = booking_data
        return booking_data

    def cancel_booking(self, external_booking_id: str) -> bool:
        self._simulate_network()
        self._simulate_failure()

        if external_booking_id not in self._bookings:
            raise ExternalAPIResponseError(
                f"Бронирование {external_booking_id} не найдено во внешней системе"
            )

        booking = self._bookings[external_booking_id]
        booking["status"] = "cancelled"
        booking["cancelled_at"] = datetime.now().isoformat()
        return True

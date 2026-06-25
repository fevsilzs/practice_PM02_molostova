from abc import ABC, abstractmethod
from datetime import date
from typing import List, Dict, Optional, Any

from src.domain.models import Room
from src.domain.exceptions import (
    ExternalAPIConnectionError,
    ExternalAPIResponseError,
    ExternalRoomNotAvailableError,
)
from src.adapters.external_api import ExternalAPIClient


class RoomAvailabilityProvider(ABC):
    @abstractmethod
    def check_availability(
        self, room: Room, check_in: date, check_out: date
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def check_multiple_availability(
        self, rooms: List[Room], check_in: date, check_out: date
    ) -> Dict[int, Dict[str, Any]]:
        pass

    @abstractmethod
    def book_room(
        self,
        room: Room,
        guest_name: str,
        guest_email: str,
        check_in: date,
        check_out: date,
        total_price: float,
    ) -> Optional[str]:
        pass

    @abstractmethod
    def cancel_booking(self, external_booking_id: str) -> bool:
        pass


class LocalAvailabilityProvider(RoomAvailabilityProvider):
    def __init__(self, booking_repo):
        self.booking_repo = booking_repo

    def check_availability(
        self, room: Room, check_in: date, check_out: date
    ) -> Dict[str, Any]:
        bookings = self.booking_repo.get_by_room_and_dates(room.id, check_in, check_out)
        is_available = len(bookings) == 0

        return {
            "available": is_available,
            "price": room.price_per_night * (check_out - check_in).days,
            "source": "local",
        }

    def check_multiple_availability(
        self, rooms: List[Room], check_in: date, check_out: date
    ) -> Dict[int, Dict[str, Any]]:
        result = {}
        for room in rooms:
            result[room.id] = self.check_availability(room, check_in, check_out)
        return result

    def book_room(
        self,
        room: Room,
        guest_name: str,
        guest_email: str,
        check_in: date,
        check_out: date,
        total_price: float,
    ) -> Optional[str]:
        return None

    def cancel_booking(self, external_booking_id: str) -> bool:
        return True


class ExternalRoomAvailabilityAdapter(RoomAvailabilityProvider):
    def __init__(
        self,
        api_client: ExternalAPIClient,
        fallback_provider: Optional[RoomAvailabilityProvider] = None,
        use_cache: bool = True,
    ):
        self.api_client = api_client
        self.fallback_provider = fallback_provider
        self.use_cache = use_cache
        self._cache = {}

    def _get_cache_key(self, room: Room, check_in: date, check_out: date) -> str:
        return f"{room.external_id}_{check_in}_{check_out}"

    def _clear_cache(self, room: Room = None, check_in: date = None, check_out: date = None):
        if room and check_in and check_out:
            key = self._get_cache_key(room, check_in, check_out)
            self._cache.pop(key, None)
        else:
            self._cache.clear()

    def _fallback_check(self, room: Room, check_in: date, check_out: date) -> Dict[str, Any]:
        if self.fallback_provider:
            return self.fallback_provider.check_availability(room, check_in, check_out)

        return {
            "available": False,
            "price": 0,
            "source": "fallback",
            "error": "External API unavailable and no fallback provider",
        }

    def check_availability(
        self, room: Room, check_in: date, check_out: date
    ) -> Dict[str, Any]:
        if self.use_cache:
            cache_key = self._get_cache_key(room, check_in, check_out)
            if cache_key in self._cache:
                return self._cache[cache_key]

        try:
            if not room.external_id:
                return self._fallback_check(room, check_in, check_out)

            result = self.api_client.check_room_availability(
                room.external_id, check_in, check_out
            )

            normalized_result = {
                "available": result["available"],
                "price": result.get(
                    "price", room.price_per_night * (check_out - check_in).days
                ),
                "currency": result.get("currency", "USD"),
                "external_room_id": result.get("external_room_id"),
                "source": "external",
                "conflicting_booking": result.get("conflicting_booking"),
            }

            if self.use_cache:
                cache_key = self._get_cache_key(room, check_in, check_out)
                self._cache[cache_key] = normalized_result

            return normalized_result

        except (ExternalAPIConnectionError, ExternalAPIResponseError):
            return self._fallback_check(room, check_in, check_out)

    def check_multiple_availability(
        self, rooms: List[Room], check_in: date, check_out: date
    ) -> Dict[int, Dict[str, Any]]:
        external_rooms = [r for r in rooms if r.external_id]
        local_rooms = [r for r in rooms if not r.external_id]

        result = {}

        if external_rooms:
            external_ids = [r.external_id for r in external_rooms]
            try:
                external_results = self.api_client.check_multiple_rooms_availability(
                    external_ids, check_in, check_out
                )

                for room in external_rooms:
                    ext_result = external_results.get(room.external_id, {})
                    result[room.id] = {
                        "available": ext_result.get("available", False),
                        "price": ext_result.get(
                            "price", room.price_per_night * (check_out - check_in).days
                        ),
                        "source": "external",
                        "error": ext_result.get("error"),
                    }
            except Exception:
                for room in external_rooms:
                    result[room.id] = self._fallback_check(room, check_in, check_out)

        if local_rooms and self.fallback_provider:
            local_results = self.fallback_provider.check_multiple_availability(
                local_rooms, check_in, check_out
            )
            for room_id, res in local_results.items():
                result[room_id] = res

        return result

    def book_room(
        self,
        room: Room,
        guest_name: str,
        guest_email: str,
        check_in: date,
        check_out: date,
        total_price: float,
    ) -> Optional[str]:
        try:
            if not room.external_id:
                return None

            availability = self.check_availability(room, check_in, check_out)
            if not availability.get("available", False):
                raise ExternalRoomNotAvailableError(
                    f"Номер {room.id} недоступен для бронирования во внешней системе"
                )

            booking_data = self.api_client.create_booking(
                external_room_id=room.external_id,
                guest_name=guest_name,
                guest_email=guest_email,
                check_in=check_in,
                check_out=check_out,
                total_price=total_price,
            )

            self._clear_cache(room, check_in, check_out)
            return booking_data.get("id")

        except ExternalAPIConnectionError:
            raise ExternalAPIConnectionError(
                "Не удалось создать бронирование во внешней системе",
                details={"room_id": room.id},
            )

    def cancel_booking(self, external_booking_id: str) -> bool:
        try:
            return self.api_client.cancel_booking(external_booking_id)
        except (ExternalAPIConnectionError, ExternalAPIResponseError):
            return False

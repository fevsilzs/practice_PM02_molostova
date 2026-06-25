from typing import List, Optional
from src.domain.models import Hotel
from src.domain.exceptions import HotelNotFoundError
from src.dto.hotel_dto import HotelCreateDTO, HotelResponseDTO, HotelUpdateDTO
from src.uow.unit_of_work import UnitOfWork


class HotelService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.hotel_repo = uow.hotels

    def create(self, dto: HotelCreateDTO) -> HotelResponseDTO:
        hotel = Hotel(
            id=None,
            name=dto.name,
            address=dto.address,
            phone=dto.phone,
            rating=dto.rating
        )
        saved = self.hotel_repo.add(hotel)
        self.uow.commit()
        return HotelResponseDTO.from_hotel(saved)

    def get_by_id(self, hotel_id: int) -> HotelResponseDTO:
        hotel = self.hotel_repo.get_by_id(hotel_id)
        if not hotel:
            raise HotelNotFoundError(f"Отель с ID {hotel_id} не найден")
        return HotelResponseDTO.from_hotel(hotel)

    def get_all(self, **filters) -> List[HotelResponseDTO]:
        hotels = self.hotel_repo.get_all(**filters)
        return [HotelResponseDTO.from_hotel(h) for h in hotels]

    def update(self, hotel_id: int, dto: HotelUpdateDTO) -> HotelResponseDTO:
        hotel = self.hotel_repo.get_by_id(hotel_id)
        if not hotel:
            raise HotelNotFoundError(f"Отель с ID {hotel_id} не найден")

        if dto.name is not None:
            hotel.name = dto.name
        if dto.address is not None:
            hotel.address = dto.address
        if dto.phone is not None:
            hotel.phone = dto.phone
        if dto.rating is not None:
            hotel.rating = dto.rating

        updated = self.hotel_repo.update(hotel)
        self.uow.commit()
        return HotelResponseDTO.from_hotel(updated)

    def delete(self, hotel_id: int) -> bool:
        result = self.hotel_repo.delete(hotel_id)
        self.uow.commit()
        return result

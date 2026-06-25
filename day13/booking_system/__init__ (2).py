import sys
import os

# Добавляем ПАПКУ day13 в путь поиска
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# ПРОВЕРКА: видит ли Python папку booking_system?
try:
    import booking_system
    print("✅ Папка booking_system найдена!")
except ImportError:
    print("❌ Папка booking_system НЕ найдена!")
    print(f"   Текущая папка: {current_dir}")
    print(f"   Содержимое папки: {os.listdir(current_dir)}")
    sys.exit(1)

# Теперь импортируем
from booking_system.src.dto.booking_dto import BookingCreateDTO
from booking_system.src.domain.models import Hotel, Room
from booking_system.src.repositories.booking_repo import BookingRepository
from booking_system.src.services.pricing_service import PricingService
from booking_system.src.uow.unit_of_work import UnitOfWork
from booking_system.src.adapters.external_api import ExternalAPIClient
from booking_system.src.adapters.room_availability_adapter import (
    ExternalRoomAvailabilityAdapter,
    LocalAvailabilityProvider
)
from booking_system.src.services.booking_service import BookingService

from datetime import date

print("=" * 50)
print("🚀 ЗАПУСК ТЕСТОВОГО СКРИПТА")
print("=" * 50)

# Создаем UoW (Unit of Work)
uow = UnitOfWork()

# Создаем отель
hotel = uow.hotels.add(
    Hotel(id=None, name="Grand Hotel", address="ул. Примерная, 1", phone="+7-999-123-4567")
)
print(f"✅ Создан отель: {hotel.name} (ID: {hotel.id})")

# Создаем номер с внешним ID
room = uow.rooms.add(
    Room(
        id=None,
        hotel_id=hotel.id,
        number="101",
        capacity=2,
        price_per_night=100.0,
        external_id="EXT_1_101"
    )
)
print(f"✅ Создан номер: {room.number} (ID: {room.id}, External ID: {room.external_id})")

# Создаем сервисы
pricing = PricingService()
api_client = ExternalAPIClient()
local_provider = LocalAvailabilityProvider(uow.bookings)
adapter = ExternalRoomAvailabilityAdapter(api_client, fallback_provider=local_provider)
booking_service = BookingService(uow, pricing, adapter)

# Создаем DTO для бронирования
dto = BookingCreateDTO(
    room_id=room.id,
    guest_name="Иван Иванов",
    guest_email="ivan@example.com",
    check_in=date(2026, 7, 15),
    check_out=date(2026, 7, 20)
)

print(f"✅ Создан DTO для бронирования")
print(f"   - Номер: {dto.room_id}")
print(f"   - Гость: {dto.guest_name}")
print(f"   - Заезд: {dto.check_in}")
print(f"   - Выезд: {dto.check_out}")

print("\n" + "=" * 50)
print("📋 ПРОБУЕМ СОЗДАТЬ БРОНИРОВАНИЕ...")
print("=" * 50)

# Пробуем создать бронирование
try:
    result = booking_service.create(dto)
    print("\n✅ БРОНИРОВАНИЕ УСПЕШНО СОЗДАНО!")
    print(f"   - ID бронирования: {result.id}")
    print(f"   - Стоимость: {result.total_price} руб.")
    print(f"   - Статус: {result.status}")
    print(f"   - External ID: {result.external_booking_id}")
except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")

print("\n" + "=" * 50)
print("🏁 СКРИПТ ЗАВЕРШЕН")
print("=" * 50)

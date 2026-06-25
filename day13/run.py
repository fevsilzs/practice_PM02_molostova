import sys
import os

# Добавляем все возможные пути
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'booking_system'))
sys.path.insert(0, os.path.join(current_dir, 'booking_system', 'src'))

# ПРОВЕРКА: что мы видим
print("=" * 50)
print("🔍 ДИАГНОСТИКА ПУТЕЙ")
print("=" * 50)
print(f"Текущая папка: {current_dir}")
print(f"Содержимое папки day13: {os.listdir(current_dir)}")

# Проверяем папку booking_system
booking_dir = os.path.join(current_dir, 'booking_system')
if os.path.exists(booking_dir):
    print(f"Содержимое booking_system: {os.listdir(booking_dir)}")
    src_dir = os.path.join(booking_dir, 'src')
    if os.path.exists(src_dir):
        print(f"Содержимое src: {os.listdir(src_dir)}")
        repos_dir = os.path.join(src_dir, 'repositories')
        if os.path.exists(repos_dir):
            print(f"Содержимое repositories: {os.listdir(repos_dir)}")
        else:
            print("❌ Папка repositories НЕ НАЙДЕНА!")
    else:
        print("❌ Папка src НЕ НАЙДЕНА!")
else:
    print("❌ Папка booking_system НЕ НАЙДЕНА!")

print("=" * 50)

# Теперь пытаемся импортировать
try:
    from booking_system.src.repositories.booking_repo import BookingRepository
    print("✅ Импорт BookingRepository УСПЕШЕН!")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    try:
        from src.repositories.booking_repo import BookingRepository
        print("✅ Импорт через src.repositories УСПЕШЕН!")
    except ImportError as e2:
        print(f"❌ Альтернативный импорт тоже не работает: {e2}")
        try:
            import booking_repo
            print("✅ Прямой импорт booking_repo УСПЕШЕН!")
        except ImportError as e3:
            print(f"❌ Прямой импорт не работает: {e3}")
            sys.exit(1)

# Если дошли сюда - всё работает, продолжаем
print("=" * 50)
print("🚀 ЗАПУСК ТЕСТОВОГО СКРИПТА")
print("=" * 50)

# Теперь импортируем всё остальное
from booking_system.src.dto.booking_dto import BookingCreateDTO
from booking_system.src.domain.models import Hotel, Room
from booking_system.src.services.pricing_service import PricingService
from booking_system.src.uow.unit_of_work import UnitOfWork
from booking_system.src.adapters.external_api import ExternalAPIClient
from booking_system.src.adapters.room_availability_adapter import (
    ExternalRoomAvailabilityAdapter,
    LocalAvailabilityProvider
)
from booking_system.src.services.booking_service import BookingService

from datetime import date

# Создаем UoW (Unit of Work)
uow = UnitOfWork()

# Создаем отель
hotel = uow.hotels.add(
    Hotel(id=None, name="Grand Hotel", address="ул. Примерная, 1", phone="+7-999-123-4567")
)
print(f"✅ Создан отель: {hotel.name} (ID: {hotel.id})")

# ===== НОВЫЙ КОД: Создаем клиент внешнего API =====
api_client = ExternalAPIClient()

# Создаем номер во внешней системе ДО бронирования
print("\n📡 СОЗДАЕМ НОМЕР ВО ВНЕШНЕЙ СИСТЕМЕ...")
external_room_data = api_client.create_room(
    hotel_id=hotel.id,
    room_number="101",
    capacity=2,
    price_per_night=100.0,
    room_type="standard"
)
external_id = external_room_data["external_id"]
print(f"✅ Номер создан во внешней системе! External ID: {external_id}")

# Создаем локальный номер с привязкой к внешнему ID
room = uow.rooms.add(
    Room(
        id=None,
        hotel_id=hotel.id,
        number="101",
        capacity=2,
        price_per_night=100.0,
        external_id=external_id  # ← Теперь есть привязка!
    )
)
print(f"✅ Создан локальный номер: {room.number} (ID: {room.id})")

# Создаем сервисы
pricing = PricingService()
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
    print(f"   - Синхронизировано с внешним API: {result.synced_with_external}")
except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")

print("\n" + "=" * 50)
print("🏁 СКРИПТ ЗАВЕРШЕН")
print("=" * 50)

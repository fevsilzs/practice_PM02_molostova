import sys
import os

# Добавляем корневую папку в PYTHONPATH, чтобы импорты работали
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.courier_service import CourierService
from src.services.routing import RoutingService
from src.repositories.in_memory import InMemoryOrderRepository, InMemoryCourierRepository
from src.utils.logging_config import setup_logging


def main():
    # Настройка логирования
    setup_logging()

    print("=" * 60)
    print("КУРЬЕРСКАЯ СЛУЖБА - ДЕМОНСТРАЦИЯ РАБОТЫ")
    print("=" * 60)

    # Инициализация зависимостей (Dependency Injection)
    order_repo = InMemoryOrderRepository()
    courier_repo = InMemoryCourierRepository()
    routing_service = RoutingService(use_mock=True)

    # Создание сервиса
    service = CourierService(order_repo, courier_repo, routing_service)

    # ========== 1. СОЗДАЁМ ЗАКАЗ ==========
    print("\n📦 ШАГ 1: Создание заказа")
    print("-" * 40)

    order_data = {
        "customer_name": "Иван Петров",
        "customer_phone": "+79111234567",
        "pickup": {
            "street": "ул. Тверская, 1",
            "city": "Москва",
            "postal_code": "101000",
            "latitude": 55.7558,
            "longitude": 37.6173
        },
        "delivery": {
            "street": "ул. Арбат, 20",
            "city": "Москва",
            "postal_code": "119002",
            "latitude": 55.7516,
            "longitude": 37.6189
        }
    }

    try:
        order = service.create_order(order_data)
        print(f"✅ Заказ создан успешно!")
        print(f"   ID заказа: {order.id}")
        print(f"   Клиент: {order.customer_name}")
        print(f"   Статус: {order.status}")
        print(f"   Расчётное время доставки: {order.estimated_delivery_time_minutes} мин.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    # ========== 2. РЕГИСТРИРУЕМ КУРЬЕРА ==========
    print("\n🚴 ШАГ 2: Регистрация курьера")
    print("-" * 40)

    courier_data = {
        "name": "Алексей Курьер",
        "phone": "+79119876543",
        "max_orders": 3
    }

    try:
        courier = service.register_courier(courier_data)
        print(f"✅ Курьер зарегистрирован успешно!")
        print(f"   ID курьера: {courier.id}")
        print(f"   Имя: {courier.name}")
        print(f"   Статус: {courier.status}")
        print(f"   Макс. заказов: {courier.max_orders}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    # ========== 3. НАЗНАЧАЕМ КУРЬЕРА ==========
    print("\n📋 ШАГ 3: Назначение курьера на заказ")
    print("-" * 40)

    try:
        assigned_order = service.assign_courier(order.id, courier.id)
        print(f"✅ Курьер назначен успешно!")
        print(f"   Заказ {assigned_order.id} -> курьер {assigned_order.courier_id}")
        print(f"   Статус заказа: {assigned_order.status}")
        
        # Проверяем статус курьера
        updated_courier = service.get_courier(courier.id)
        print(f"   Статус курьера: {updated_courier.status}")
        print(f"   Активных заказов у курьера: {len(updated_courier.active_order_ids)}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    # ========== 4. ОБНОВЛЯЕМ СТАТУС ДО "В ПУТИ" ==========
    print("\n🚚 ШАГ 4: Обновление статуса заказа (в пути)")
    print("-" * 40)

    try:
        in_progress_order = service.update_order_status(order.id, "in_progress")
        print(f"✅ Статус обновлён!")
        print(f"   Заказ {in_progress_order.id}: {in_progress_order.status}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    # ========== 5. ДОСТАВЛЯЕМ ЗАКАЗ ==========
    print("\n🏁 ШАГ 5: Доставка заказа")
    print("-" * 40)

    try:
        delivered_order = service.update_order_status(order.id, "delivered")
        print(f"✅ Заказ доставлен!")
        print(f"   Заказ {delivered_order.id}: {delivered_order.status}")
        print(f"   Фактическое время доставки: {delivered_order.actual_delivery_time_minutes} мин.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    # ========== 6. СТАТИСТИКА КУРЬЕРА ==========
    print("\n📊 ШАГ 6: Статистика курьера")
    print("-" * 40)

    try:
        stats = service.get_courier_performance(courier.id)
        print(f"📈 Статистика курьера {stats['name']}:")
        print(f"   Всего заказов: {stats['total_orders']}")
        print(f"   Доставлено: {stats['delivered']}")
        print(f"   Активных заказов: {stats['active_orders']}")
        if stats['avg_delivery_time']:
            print(f"   Среднее время доставки: {stats['avg_delivery_time']} мин.")
        else:
            print(f"   Среднее время доставки: нет данных")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    # ========== 7. ПОЛУЧАЕМ СПИСОК ДОСТУПНЫХ КУРЬЕРОВ ==========
    print("\n👥 ШАГ 7: Список доступных курьеров")
    print("-" * 40)

    try:
        available = service.get_available_couriers()
        print(f"✅ Доступных курьеров: {len(available)}")
        for c in available:
            print(f"   • {c.name} (ID: {c.id}) - {c.status}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    # ========== 8. ПОИСК ЗАКАЗА ПО ID ==========
    print("\n🔍 ШАГ 8: Поиск заказа по ID")
    print("-" * 40)

    try:
        found_order = service.get_order(order.id)
        print(f"✅ Заказ найден:")
        print(f"   ID: {found_order.id}")
        print(f"   Клиент: {found_order.customer_name}")
        print(f"   Статус: {found_order.status}")
        print(f"   Курьер: {found_order.courier_id}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    print("\n" + "=" * 60)
    print("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
    print("=" * 60)


if __name__ == "__main__":
    main()

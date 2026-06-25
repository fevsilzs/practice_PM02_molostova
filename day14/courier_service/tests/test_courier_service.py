# tests/test_courier_service.py

import sys
import os

# Добавляем корневую папку в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.courier_service import CourierService
from src.services.routing import RoutingService
from src.repositories.in_memory import InMemoryOrderRepository, InMemoryCourierRepository
from src.domain.exceptions import ValidationError, OrderNotFoundError


def test_create_order():
    """Тест создания заказа"""
    print("\n🧪 Тест 1: Создание заказа")
    
    order_repo = InMemoryOrderRepository()
    courier_repo = InMemoryCourierRepository()
    routing = RoutingService(use_mock=True)
    service = CourierService(order_repo, courier_repo, routing)
    
    order_data = {
        "customer_name": "Тестовый Клиент",
        "customer_phone": "+79111234567",
        "pickup": {
            "street": "ул. Тестовая, 1",
            "city": "Москва",
            "postal_code": "101000",
            "latitude": 55.7558,
            "longitude": 37.6173
        },
        "delivery": {
            "street": "ул. Тестовая, 2",
            "city": "Москва",
            "postal_code": "101001",
            "latitude": 55.7516,
            "longitude": 37.6189
        }
    }
    
    order = service.create_order(order_data)
    
    assert order.id > 0, "ID заказа должен быть больше 0"
    assert order.customer_name == "Тестовый Клиент", "Имя клиента не совпадает"
    assert order.status.value == "pending", "Статус должен быть pending"
    print(f"   ✅ Заказ создан: ID={order.id}")


def test_create_order_invalid_data():
    """Тест создания заказа с невалидными данными"""
    print("\n🧪 Тест 2: Создание заказа с невалидными данными")
    
    order_repo = InMemoryOrderRepository()
    courier_repo = InMemoryCourierRepository()
    routing = RoutingService(use_mock=True)
    service = CourierService(order_repo, courier_repo, routing)
    
    invalid_data = {
        "customer_name": "A",  # Слишком короткое имя
        "customer_phone": "+79111234567",
        "pickup": {
            "street": "ул. Тест, 1",
            "city": "Москва",
            "postal_code": "101000"
        },
        "delivery": {
            "street": "ул. Тест, 2",
            "city": "Москва",
            "postal_code": "101001"
        }
    }
    
    try:
        service.create_order(invalid_data)
        assert False, "Должна быть ошибка валидации"
    except ValidationError:
        print("   ✅ Ошибка валидации поймана")


def test_register_courier():
    """Тест регистрации курьера"""
    print("\n🧪 Тест 3: Регистрация курьера")
    
    order_repo = InMemoryOrderRepository()
    courier_repo = InMemoryCourierRepository()
    routing = RoutingService(use_mock=True)
    service = CourierService(order_repo, courier_repo, routing)
    
    courier_data = {
        "name": "Тестовый Курьер",
        "phone": "+79119876543",
        "max_orders": 3
    }
    
    courier = service.register_courier(courier_data)
    
    assert courier.id > 0, "ID курьера должен быть больше 0"
    assert courier.name == "Тестовый Курьер", "Имя курьера не совпадает"
    assert courier.status.value == "available", "Статус должен быть available"
    print(f"   ✅ Курьер зарегистрирован: ID={courier.id}")


def test_assign_courier():
    """Тест назначения курьера на заказ"""
    print("\n🧪 Тест 4: Назначение курьера на заказ")
    
    order_repo = InMemoryOrderRepository()
    courier_repo = InMemoryCourierRepository()
    routing = RoutingService(use_mock=True)
    service = CourierService(order_repo, courier_repo, routing)
    
    # Создаём заказ
    order_data = {
        "customer_name": "Клиент",
        "customer_phone": "+79111234567",
        "pickup": {
            "street": "ул. Тест, 1",
            "city": "Москва",
            "postal_code": "101000"
        },
        "delivery": {
            "street": "ул. Тест, 2",
            "city": "Москва",
            "postal_code": "101001"
        }
    }
    order = service.create_order(order_data)
    
    # Создаём курьера
    courier_data = {
        "name": "Курьер",
        "phone": "+79119876543",
        "max_orders": 3
    }
    courier = service.register_courier(courier_data)
    
    # Назначаем
    assigned_order = service.assign_courier(order.id, courier.id)
    
    assert assigned_order.courier_id == courier.id, "Курьер не назначен"
    assert assigned_order.status.value == "assigned", "Статус должен быть assigned"
    print(f"   ✅ Заказ {assigned_order.id} назначен курьеру {assigned_order.courier_id}")


def test_update_order_status():
    """Тест обновления статуса заказа (полный цикл)"""
    print("\n🧪 Тест 5: Обновление статуса заказа")
    
    order_repo = InMemoryOrderRepository()
    courier_repo = InMemoryCourierRepository()
    routing = RoutingService(use_mock=True)
    service = CourierService(order_repo, courier_repo, routing)
    
    # 1. Создаём заказ
    order_data = {
        "customer_name": "Клиент",
        "customer_phone": "+79111234567",
        "pickup": {
            "street": "ул. Тест, 1",
            "city": "Москва",
            "postal_code": "101000"
        },
        "delivery": {
            "street": "ул. Тест, 2",
            "city": "Москва",
            "postal_code": "101001"
        }
    }
    order = service.create_order(order_data)
    print(f"   📦 Заказ создан: статус={order.status.value}")
    
    # 2. Создаём курьера
    courier_data = {
        "name": "Курьер",
        "phone": "+79119876543",
        "max_orders": 3
    }
    courier = service.register_courier(courier_data)
    
    # 3. Назначаем курьера (PENDING -> ASSIGNED)
    assigned = service.assign_courier(order.id, courier.id)
    assert assigned.status.value == "assigned", "Статус должен быть assigned"
    print(f"   ✅ Назначен курьер: статус={assigned.status.value}")
    
    # 4. Меняем статус на IN_PROGRESS (ASSIGNED -> IN_PROGRESS)
    in_progress = service.update_order_status(order.id, "in_progress")
    assert in_progress.status.value == "in_progress", "Статус должен быть in_progress"
    print(f"   ✅ В пути: статус={in_progress.status.value}")
    
    # 5. Меняем статус на DELIVERED (IN_PROGRESS -> DELIVERED)
    delivered = service.update_order_status(order.id, "delivered")
    assert delivered.status.value == "delivered", "Статус должен быть delivered"
    print(f"   ✅ Доставлен: статус={delivered.status.value}")


def test_get_order_not_found():
    """Тест получения несуществующего заказа"""
    print("\n🧪 Тест 6: Получение несуществующего заказа")
    
    order_repo = InMemoryOrderRepository()
    courier_repo = InMemoryCourierRepository()
    routing = RoutingService(use_mock=True)
    service = CourierService(order_repo, courier_repo, routing)
    
    try:
        service.get_order(999)
        assert False, "Должна быть ошибка OrderNotFoundError"
    except OrderNotFoundError:
        print("   ✅ Ошибка OrderNotFoundError поймана")


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("ЗАПУСК ТЕСТОВ КУРЬЕРСКОЙ СЛУЖБЫ")
    print("="*60)
    
    tests = [
        test_create_order,
        test_create_order_invalid_data,
        test_register_courier,
        test_assign_courier,
        test_update_order_status,
        test_get_order_not_found
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"   ❌ Ошибка: {e}")
    
    print("\n" + "="*60)
    print(f"РЕЗУЛЬТАТЫ: {passed} пройдено, {failed} ошибок")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
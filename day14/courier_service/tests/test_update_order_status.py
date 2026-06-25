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

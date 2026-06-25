"""
Простой ручной тест для проверки работы системы
"""
from app.database import Database
from app.repositories import OrderRepository
from app.exceptions import EntityNotFoundException, ValidationException


def test_system():
    """Ручной тест системы"""
    print("Тестирование системы управления заказами...")
    
    # Создаем базу в памяти для теста
    db = Database("sqlite:///:memory:")
    db.create_tables()
    
    with db.get_session() as session:
        repo = OrderRepository(session)
        
        # Тест 1: Создание заказа
        print("\nТест 1: Создание заказа")
        order_data = {
            "customer_name": "Тест Клиент",
            "delivery_address": "г. Тест, ул. Тестовая, д. 1",
            "items": [
                {"product_name": "Товар 1", "quantity": 2, "price": 100.0},
                {"product_name": "Товар 2", "quantity": 1, "price": 250.0}
            ]
        }
        
        try:
            order = repo.create(order_data)
            print(f"✓ Заказ создан: ID={order.id}, сумма={order.total_amount}")
            assert order.total_amount == 450.0, "Неверная сумма заказа"
        except Exception as e:
            print(f"✗ Ошибка: {e}")
            return False
        
        # Тест 2: Поиск по ID
        print("\nТест 2: Поиск по ID")
        found = repo.find_by_id(order.id)
        if found:
            print(f"✓ Заказ найден: ID={found.id}, клиент={found.customer_name}")
        else:
            print("✗ Заказ не найден")
            return False
        
        # Тест 3: Обновление статуса
        print("\nТест 3: Обновление статуса")
        try:
            updated = repo.update_status(order.id, "PAID")
            print(f"✓ Статус обновлен: {updated.status}")
            assert updated.status == "PAID", "Статус не обновился"
        except Exception as e:
            print(f"✗ Ошибка: {e}")
            return False
        
        # Тест 4: Поиск по статусу
        print("\nТест 4: Поиск по статусу")
        paid_orders = repo.find_all_by_status("PAID")
        print(f"✓ Найдено заказов со статусом PAID: {len(paid_orders)}")
        assert len(paid_orders) >= 1, "Заказы не найдены"
        
        # Тест 5: Подсчет суммы
        print("\nТест 5: Подсчет суммы")
        total = repo.get_total_amount_for_order(order.id)
        print(f"✓ Сумма заказа: {total}")
        assert total == 450.0, "Неверная сумма"
        
        # Тест 6: Поиск по диапазону дат
        print("\nТест 6: Поиск по датам")
        from datetime import datetime, timedelta
        start = datetime.now() - timedelta(days=1)
        end = datetime.now() + timedelta(days=1)
        orders = repo.find_by_date_range(start, end)
        print(f"✓ Найдено заказов за период: {len(orders)}")
        
        # Тест 7: Удаление
        print("\nТест 7: Удаление заказа")
        repo.delete(order.id)
        deleted = repo.find_by_id(order.id)
        if deleted is None:
            print("✓ Заказ успешно удален")
        else:
            print("✗ Заказ не удален")
            return False
        
        print("\n✅ Все тесты пройдены успешно!")
        return True


if __name__ == "__main__":
    test_system()

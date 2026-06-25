# app/repositories.py

from sqlalchemy import func as db_func
from app.exceptions import EntityNotFoundException, ValidationException
from app.models import Order, OrderItem

class OrderRepository:
    """
    Репозиторий для работы с заказами.
    Принимает сессию БД при инициализации и предоставляет CRUD-операции.
    """

    def __init__(self, db_session):
        """Инициализирует репозиторий с заданной сессией базы данных."""
        self.db_session = db_session

    # --- Вспомогательный метод ---
    def _calculate_total_amount(self, items_data):
        """Вычисляет общую стоимость заказа по списку товаров."""
        return sum(item['quantity'] * item['price'] for item in items_data)

    # --- Приватный метод валидации ---
    # <-- ЭТОТ МЕТОД НУЖНО ДОБАВИТЬ ОБРАТНО
    def _validate_item_data(self, item_data):
        """Валидирует данные одного товара."""
        quantity = item_data.get('quantity')
        product_name = item_data.get('product_name', "'неизвестный'")

        if not isinstance(quantity, int) or quantity <= 0:
            raise ValidationException(
                f"Некорректное количество для товара '{product_name}'. "
                f"Количество должно быть положительным целым числом."
            )
    # --------------------------------------------------

    # --- Методы создания ---

    def create(self, order_data):
        """
        Создает новый заказ в базе данных.
        :param order_data: Словарь с данными заказа.
        :return: Сохраненный объект Order с присвоенным ID и рассчитанной суммой.
        """
        items_data = order_data.pop('items', [])
        total_amount = self._calculate_total_amount(items_data)
        order = Order(total_amount=total_amount, **order_data)

        try:
            for item in items_data:
                # Здесь вызывается восстановленный метод
                self._validate_item_data(item)
                
                order_item = OrderItem(**item)
                order.items.append(order_item)
            
            self.db_session.add(order)
            self.db_session.commit()

        except Exception as e:
            self.db_session.rollback()
            raise e

        return order

    # --- Методы чтения ---

    def find_by_id(self, order_id):
        """Находит заказ по его ID."""
        if order_id is None:
            return None
        return self.db_session.query(Order).get(order_id)

    def find_all_by_status(self, status):
        """Находит все заказы с определенным статусом."""
        return self.db_session.query(Order).filter(Order.status == status).all()

    # --- Методы обновления ---

    def update_status(self, order_id, new_status):
        """
        Обновляет статус существующего заказа.
        :raises EntityNotFoundException: Если заказ не найден.
        :return: Обновленный объект Order.
        """
        order = self.find_by_id(order_id)
        if not order:
            raise EntityNotFoundException(f"Заказ с ID {order_id} не найден.")
        
        order.status = new_status
        self.db_session.commit()
        return order 

    # --- Методы удаления ---

    def delete(self, order_id):
        """
        Удаляет заказ из базы данных.
        :raises EntityNotFoundException: Если заказ не найден.
        """
        order = self.find_by_id(order_id)
        if not order:
            raise EntityNotFoundException(f"Заказ с ID {order_id} не найден.")
            
        self.db_session.delete(order)
        self.db_session.commit()
        return True

    # --- Вспомогательные методы ---

    def get_total_amount_for_order(self, order_id):
        """
        Вычисляет итоговую сумму заказа, агрегируя данные из связанных OrderItem.
        """
        result = self.db_session.query(
            db_func.sum(OrderItem.quantity * OrderItem.price)
        ).filter(OrderItem.order_id == order_id).scalar()
        
        return result or 0.0

from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities import Order, Courier, OrderStatus, CourierStatus

class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> Order:
        """Сохранить заказ (новый или обновлённый)."""
        pass

    @abstractmethod
    def find_by_id(self, order_id: int) -> Optional[Order]:
        """Найти заказ по ID."""
        pass

    @abstractmethod
    def find_by_status(self, status: OrderStatus) -> List[Order]:
        """Найти все заказы с определённым статусом."""
        pass

    @abstractmethod
    def find_by_courier_id(self, courier_id: int) -> List[Order]:
        """Найти заказы, назначенные курьеру."""
        pass

    @abstractmethod
    def update(self, order: Order) -> Order:
        """Обновить заказ."""
        pass

    @abstractmethod
    def delete(self, order_id: int) -> None:
        """Удалить заказ."""
        pass

class CourierRepository(ABC):
    @abstractmethod
    def save(self, courier: Courier) -> Courier:
        """Сохранить курьера."""
        pass

    @abstractmethod
    def find_by_id(self, courier_id: int) -> Optional[Courier]:
        """Найти курьера по ID."""
        pass

    @abstractmethod
    def find_by_status(self, status: CourierStatus) -> List[Courier]:
        """Найти курьеров по статусу."""
        pass

    @abstractmethod
    def find_available(self) -> List[Courier]:
        """Найти всех свободных курьеров."""
        pass

    @abstractmethod
    def update(self, courier: Courier) -> Courier:
        """Обновить данные курьера."""
        pass

    @abstractmethod
    def delete(self, courier_id: int) -> None:
        """Удалить курьера."""
        pass

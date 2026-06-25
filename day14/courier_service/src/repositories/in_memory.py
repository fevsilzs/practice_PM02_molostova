from typing import Optional, List, Dict
from src.domain.entities import Order, Courier, OrderStatus, CourierStatus
from src.repositories.interfaces import OrderRepository, CourierRepository
from src.domain.exceptions import NotFoundError

class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self._storage: Dict[int, Order] = {}
        self._counter = 1

    def save(self, order: Order) -> Order:
        if order.id is None or order.id == 0:
            order.id = self._counter
            self._counter += 1
        self._storage[order.id] = order
        return order

    def find_by_id(self, order_id: int) -> Optional[Order]:
        return self._storage.get(order_id)

    def find_by_status(self, status: OrderStatus) -> List[Order]:
        return [o for o in self._storage.values() if o.status == status]

    def find_by_courier_id(self, courier_id: int) -> List[Order]:
        return [o for o in self._storage.values() if o.courier_id == courier_id]

    def update(self, order: Order) -> Order:
        if order.id not in self._storage:
            raise NotFoundError(f"Order {order.id} not found")
        self._storage[order.id] = order
        return order

    def delete(self, order_id: int) -> None:
        if order_id in self._storage:
            del self._storage[order_id]

class InMemoryCourierRepository(CourierRepository):
    def __init__(self):
        self._storage: Dict[int, Courier] = {}
        self._counter = 1

    def save(self, courier: Courier) -> Courier:
        if courier.id is None or courier.id == 0:
            courier.id = self._counter
            self._counter += 1
        self._storage[courier.id] = courier
        return courier

    def find_by_id(self, courier_id: int) -> Optional[Courier]:
        return self._storage.get(courier_id)

    def find_by_status(self, status: CourierStatus) -> List[Courier]:
        return [c for c in self._storage.values() if c.status == status]

    def find_available(self) -> List[Courier]:
        return [c for c in self._storage.values() if c.status == CourierStatus.AVAILABLE]

    def update(self, courier: Courier) -> Courier:
        if courier.id not in self._storage:
            raise NotFoundError(f"Courier {courier.id} not found")
        self._storage[courier.id] = courier
        return courier

    def delete(self, courier_id: int) -> None:
        if courier_id in self._storage:
            del self._storage[courier_id]

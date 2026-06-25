import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from src.domain.entities import Order, Courier, Address, OrderStatus, CourierStatus
from src.domain.schemas import OrderCreateSchema, CourierCreateSchema, AddressSchema
from src.domain.exceptions import (
    OrderNotFoundError,
    CourierNotFoundError,
    NoAvailableCourierError,
    InvalidOrderStatusError,
    ValidationError,
    BusinessRuleViolation,
    RouteCalculationError,
    OrderAlreadyAssignedError,
    CourierMaxOrdersExceededError
)
from src.repositories.interfaces import OrderRepository, CourierRepository
from src.services.routing import RoutingService

logger = logging.getLogger(__name__)

class CourierService:
    """
    Сервис управления курьерской доставкой.
    Содержит всю бизнес-логику.
    """
    
    def __init__(
        self,
        order_repo: OrderRepository,
        courier_repo: CourierRepository,
        routing_service: RoutingService
    ):
        self.order_repo = order_repo
        self.courier_repo = courier_repo
        self.routing = routing_service
    
    # ========== УПРАВЛЕНИЕ ЗАКАЗАМИ ==========
    
    def create_order(self, data: Dict[str, Any]) -> Order:
        """
        Создать новый заказ.
        """
        # 1. Валидация через Pydantic
        try:
            schema = OrderCreateSchema(**data)
        except Exception as e:
            logger.error(f"Validation error: {e}")
            raise ValidationError(f"Invalid order data: {str(e)}")
        
        # 2. Создание сущности
        pickup = Address(
            street=schema.pickup.street,
            city=schema.pickup.city,
            postal_code=schema.pickup.postal_code,
            country=schema.pickup.country,
            latitude=schema.pickup.latitude,
            longitude=schema.pickup.longitude
        )
        delivery = Address(
            street=schema.delivery.street,
            city=schema.delivery.city,
            postal_code=schema.delivery.postal_code,
            country=schema.delivery.country,
            latitude=schema.delivery.latitude,
            longitude=schema.delivery.longitude
        )
        
        order = Order(
            id=0,
            customer_name=schema.customer_name,
            customer_phone=schema.customer_phone,
            pickup_address=pickup,
            delivery_address=delivery,
            status=OrderStatus.PENDING
        )
        
        # 3. Расчёт предполагаемого времени доставки
        try:
            distance, time_minutes = self.routing.calculate_distance_and_time(pickup, delivery)
            order.estimated_delivery_time_minutes = time_minutes
        except RouteCalculationError as e:
            logger.warning(f"Route calculation failed, using default: {e}")
            order.estimated_delivery_time_minutes = 30  # Значение по умолчанию
        
        # 4. Сохранение
        saved_order = self.order_repo.save(order)
        logger.info(f"Order created: ID={saved_order.id}, customer={saved_order.customer_name}")
        return saved_order
    
    def get_order(self, order_id: int) -> Order:
        """Получить заказ по ID."""
        order = self.order_repo.find_by_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Order with ID {order_id} not found")
        return order
    
    def get_orders_by_status(self, status: str) -> List[Order]:
        """Получить заказы по статусу."""
        try:
            order_status = OrderStatus(status)
        except ValueError:
            raise ValidationError(f"Invalid status: {status}")
        
        return self.order_repo.find_by_status(order_status)
    
    def assign_courier(self, order_id: int, courier_id: Optional[int] = None) -> Order:
        """
        Назначить курьера на заказ.
        Если courier_id не указан - выбрать ближайшего доступного.
        """
        # 1. Проверка заказа
        order = self.order_repo.find_by_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Order {order_id} not found")
        
        if order.status != OrderStatus.PENDING:
            raise InvalidOrderStatusError(
                f"Order {order_id} has status '{order.status}', cannot assign"
            )
        
        # 2. Выбор курьера
        if courier_id is None:
            # Автоматический выбор
            available_couriers = self.courier_repo.find_available()
            if not available_couriers:
                raise NoAvailableCourierError("No available couriers")
            
            # Выбор ближайшего
            best_courier = self.routing.find_nearest_available_courier(
                order.pickup_address,
                available_couriers
            )
            if not best_courier:
                raise NoAvailableCourierError("No courier near pickup point")
            courier = best_courier
        else:
            # Конкретный курьер
            courier = self.courier_repo.find_by_id(courier_id)
            if not courier:
                raise CourierNotFoundError(f"Courier {courier_id} not found")
            
            if courier.status != CourierStatus.AVAILABLE:
                raise BusinessRuleViolation(f"Courier {courier_id} is not available")
        
        # 3. Проверка лимита заказов курьера
        if len(courier.active_order_ids) >= courier.max_orders:
            raise CourierMaxOrdersExceededError(
                f"Courier {courier.id} already has {len(courier.active_order_ids)} orders"
            )
        
        # 4. Назначение (транзакционно)
        # Сохраняем состояние для возможного отката
        old_order_status = order.status
        old_courier_status = courier.status
        old_courier_orders = courier.active_order_ids.copy()
        
        try:
            order.courier_id = courier.id
            order.status = OrderStatus.ASSIGNED
            courier.active_order_ids.append(order.id)
            
            # Если у курьера достигнут лимит - меняем статус
            if len(courier.active_order_ids) >= courier.max_orders:
                courier.status = CourierStatus.BUSY
            
            # Сохраняем
            self.order_repo.update(order)
            self.courier_repo.update(courier)
            
            logger.info(f"Order {order_id} assigned to courier {courier.id}")
            return order
            
        except Exception as e:
            # Откат изменений
            order.status = old_order_status
            courier.status = old_courier_status
            courier.active_order_ids = old_courier_orders
            logger.error(f"Assignment failed, rollback: {e}")
            raise
    
    def update_order_status(self, order_id: int, new_status: str) -> Order:
        """Обновить статус заказа."""
        order = self.order_repo.find_by_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Order {order_id} not found")
        
        try:
            status = OrderStatus(new_status)
        except ValueError:
            raise ValidationError(f"Invalid status: {new_status}")
        
        # Проверка допустимости перехода
        if not self._is_valid_status_transition(order.status, status):
            raise InvalidOrderStatusError(
                f"Cannot transition from {order.status} to {status}"
            )
        
        old_status = order.status
        try:
            order.status = status
            
            if status == OrderStatus.DELIVERED:
                order.delivered_at = datetime.now()
                # Рассчёт фактического времени доставки
                if order.created_at:
                    delta = (order.delivered_at - order.created_at).total_seconds() / 60
                    order.actual_delivery_time_minutes = int(delta)
                
                # Освободить курьера
                if order.courier_id:
                    courier = self.courier_repo.find_by_id(order.courier_id)
                    if courier:
                        if order.id in courier.active_order_ids:
                            courier.active_order_ids.remove(order.id)
                        if len(courier.active_order_ids) < courier.max_orders:
                            courier.status = CourierStatus.AVAILABLE
                        self.courier_repo.update(courier)
            
            elif status == OrderStatus.CANCELLED and order.courier_id:
                # Освободить курьера при отмене
                courier = self.courier_repo.find_by_id(order.courier_id)
                if courier and order.id in courier.active_order_ids:
                    courier.active_order_ids.remove(order.id)
                    if len(courier.active_order_ids) < courier.max_orders:
                        courier.status = CourierStatus.AVAILABLE
                    self.courier_repo.update(courier)
            
            self.order_repo.update(order)
            logger.info(f"Order {order_id}: {old_status} -> {status}")
            return order
            
        except Exception as e:
            logger.error(f"Status update failed: {e}")
            raise
    
    def _is_valid_status_transition(self, current: OrderStatus, new: OrderStatus) -> bool:
        """Проверка допустимости перехода статуса."""
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.ASSIGNED, OrderStatus.CANCELLED],
            OrderStatus.ASSIGNED: [OrderStatus.IN_PROGRESS, OrderStatus.CANCELLED],
            OrderStatus.IN_PROGRESS: [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
            OrderStatus.DELIVERED: [],
            OrderStatus.CANCELLED: [],
        }
        return new in valid_transitions.get(current, [])
    
    # ========== УПРАВЛЕНИЕ КУРЬЕРАМИ ==========
    
    def register_courier(self, data: Dict[str, Any]) -> Courier:
        """Зарегистрировать нового курьера."""
        try:
            schema = CourierCreateSchema(**data)
        except Exception as e:
            raise ValidationError(f"Invalid courier data: {str(e)}")
        
        courier = Courier(
            id=0,
            name=schema.name,
            phone=schema.phone,
            max_orders=schema.max_orders
        )
        
        saved = self.courier_repo.save(courier)
        logger.info(f"Courier registered: ID={saved.id}, name={saved.name}")
        return saved
    
    def get_courier(self, courier_id: int) -> Courier:
        """Получить курьера по ID."""
        courier = self.courier_repo.find_by_id(courier_id)
        if not courier:
            raise CourierNotFoundError(f"Courier {courier_id} not found")
        return courier
    
    def get_available_couriers(self) -> List[Courier]:
        """Получить всех свободных курьеров."""
        return self.courier_repo.find_available()
    
    def update_courier_location(self, courier_id: int, lat: float, lon: float) -> Courier:
        """Обновить местоположение курьера."""
        courier = self.courier_repo.find_by_id(courier_id)
        if not courier:
            raise CourierNotFoundError(f"Courier {courier_id} not found")
        
        courier.current_location = Address(
            street="",
            city="",
            postal_code="00000",
            latitude=lat,
            longitude=lon
        )
        
        self.courier_repo.update(courier)
        logger.info(f"Courier {courier_id} location updated: ({lat}, {lon})")
        return courier
    
    # ========== ОТЧЁТЫ И СТАТИСТИКА ==========
    
    def get_courier_performance(self, courier_id: int) -> Dict[str, Any]:
        """Получить статистику работы курьера."""
        courier = self.courier_repo.find_by_id(courier_id)
        if not courier:
            raise CourierNotFoundError(f"Courier {courier_id} not found")
        
        orders = self.order_repo.find_by_courier_id(courier_id)
        delivered = [o for o in orders if o.status == OrderStatus.DELIVERED]
        
        return {
            "courier_id": courier_id,
            "name": courier.name,
            "total_orders": len(orders),
            "delivered": len(delivered),
            "active_orders": len([o for o in orders if o.status not in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]]),
            "avg_delivery_time": self._calc_avg_delivery_time(delivered) if delivered else None
        }
    
    def _calc_avg_delivery_time(self, orders: List[Order]) -> Optional[int]:
        """Рассчитать среднее время доставки."""
        times = [o.actual_delivery_time_minutes for o in orders if o.actual_delivery_time_minutes]
        if not times:
            return None
        return int(sum(times) / len(times))

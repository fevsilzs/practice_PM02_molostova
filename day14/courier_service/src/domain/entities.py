
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class CourierStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"

@dataclass
class Address:
    street: str
    city: str
    postal_code: str
    country: str = "Russia"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@dataclass
class Order:
    id: int
    customer_name: str
    customer_phone: str
    pickup_address: Address
    delivery_address: Address
    status: OrderStatus = OrderStatus.PENDING
    courier_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    delivered_at: Optional[datetime] = None
    estimated_delivery_time_minutes: Optional[int] = None
    actual_delivery_time_minutes: Optional[int] = None

@dataclass
class Courier:
    id: int
    name: str
    phone: str
    status: CourierStatus = CourierStatus.AVAILABLE
    current_location: Optional[Address] = None
    max_orders: int = 3
    active_order_ids: List[int] = field(default_factory=list)

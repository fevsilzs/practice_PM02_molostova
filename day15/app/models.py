from typing import Dict, Any

class Order:
    """Модель заказа для тестирования"""
    def __init__(self, order_id: int, total: float, status: str = "PENDING"):
        self.order_id = order_id
        self.total = total
        self.status = status
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "total": self.total,
            "status": self.status
        }

import time
import random
from datetime import datetime, time as datetime_time
from typing import List, Dict, Any
from pydantic import BaseModel, Field

# --- PYDANTIC СХЕМЫ ДЛЯ ВАЛИДАЦИИ ВХОДА И ВЫХОДА (ЧЕРНЫЙ ЯЩИК) ---

class OrderItem(BaseModel):
    product_id: str = Field(..., min_length=1)
    quantity: int = Field(..., ge=1, le=1000)
    price: float = Field(..., gt=0)

class OrderInput(BaseModel):
    order_id: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)
    items: List[OrderItem] = Field(..., min_length=1)  # ИСПРАВЛЕНО: min_items заменено на min_length
    created_at: datetime
    is_new_user: bool = False
    delivery_address: str = Field(..., min_length=5)

class ValidationResult(BaseModel):
    valid: bool
    risk_score: float = Field(..., ge=0.0, le=1.0)
    reasons: List[str]
    validated_at: datetime

# --- ФЕЙКОВЫЙ ВАЛИДАТОР ---

class FakeValidator:
    """
    Эталонная реализация валидатора (черный ящик) для отладки тестов.
    """
    def __init__(self, chaos_mode: bool = False, delay: float = 0.0):
        self.chaos_mode = chaos_mode
        self.delay = delay

    def validate_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        if self.delay > 0:
            time.sleep(self.delay)

        # Имитация хаоса (непредсказуемый сбой структуры или логики)
        if self.chaos_mode and random.random() < 0.05:
            return {
                "valid": random.choice([True, False]),
                "risk_score": 999.0,  # Невалидный риск-скор для проверки тестов
                "reasons": ["CHAOS_ERR"],
                "validated_at": datetime.now()
            }

        # Шаг 1: Валидация входной схемы
        try:
            order = OrderInput(**order_data)
        except Exception as e:
            return {
                "valid": False,
                "risk_score": 1.0,
                "reasons": [f"INVALID_SCHEMA: {str(e)}"],
                "validated_at": datetime.now()
            }

        valid = True
        reasons = []
        base_risk = 0.0

        # Расчет базовых метрик заказа
        total_amount = sum(item.quantity * item.price for item in order.items)
        total_items = sum(item.quantity for item in order.items)

        # Правило 1: Время работы магазина (08:00 - 22:00)
        order_time = order.created_at.time()
        start_time = datetime_time(8, 0)
        end_time = datetime_time(22, 0)
        if not (start_time <= order_time <= end_time):
            valid = False
            reasons.append("STORE_CLOSED")
            base_risk += 0.3

        # Правило 2: Ограничение для новых пользователей
        if order.is_new_user and total_amount > 50000:
            valid = False
            reasons.append("NEW_USER_MAX_AMOUNT_EXCEEDED")
            base_risk += 0.5

        # Расчет динамического риск-скора (0.0 до 1.0)
        base_risk += min(0.4, total_amount / 250000)
        if total_items > 50:
            base_risk += 0.2
            reasons.append("HIGH_ITEMS_COUNT")

        risk_score = min(1.0, max(0.0, base_risk))

        # Если риск слишком высок, заказ отклоняется
        if risk_score >= 0.8 and valid:
            valid = False
            reasons.append("HIGH_RISK_SCORE")

        result = ValidationResult(
            valid=valid,
            risk_score=round(risk_score, 2),
            reasons=reasons,
            validated_at=datetime.now()
        )
        return result.model_dump()


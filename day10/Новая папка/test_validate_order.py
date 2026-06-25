import pytest
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, HealthCheck

# --- 2.2 ПАРАМЕТРИЗОВАННЫЕ ТЕСТЫ (DECISION TABLE & BOUNDARIES) ---

@pytest.mark.parametrize(
    "order, expected_valid, expected_risk_min, expected_risk_max, reasons_contain",
    [
        # Кейс 1: Идеальный валидный заказ старого пользователя днем
        ({
            "order_id": "ORD-001", "user_id": "USR-1", "is_new_user": False,
            "created_at": datetime(2026, 6, 1, 12, 0), "delivery_address": "Main St 10",
            "items": [{"product_id": "P1", "quantity": 2, "price": 100.0}]
         }, True, 0.0, 0.2, []),
        
        # Кейс 2: Граница времени: Ровно в 08:00 (Открытие) — Валидно
        ({
            "order_id": "ORD-002", "user_id": "USR-1", "is_new_user": False,
            "created_at": datetime(2026, 6, 1, 8, 0), "delivery_address": "Main St 10",
            "items": [{"product_id": "P1", "quantity": 1, "price": 10.0}]
         }, True, 0.0, 0.2, []),

        # Кейс 3: Граница времени: Ночь (07:59) — Невалидно
        ({
            "order_id": "ORD-003", "user_id": "USR-1", "is_new_user": False,
            "created_at": datetime(2026, 6, 1, 7, 59), "delivery_address": "Main St 10",
            "items": [{"product_id": "P1", "quantity": 1, "price": 10.0}]
         }, False, 0.3, 0.6, ["STORE_CLOSED"]),

        # Кейс 4: Новый пользователь, сумма ровно 50 000 — Валидно
        ({
            "order_id": "ORD-004", "user_id": "USR-NEW", "is_new_user": True,
            "created_at": datetime(2026, 6, 1, 15, 0), "delivery_address": "Main St 10",
            "items": [{"product_id": "P1", "quantity": 1, "price": 50000.0}]
         }, True, 0.1, 0.4, []),

        # Кейс 5: Новый пользователь, сумма 50 000.01 (Превышение лимита) — Невалидно
        ({
            "order_id": "ORD-005", "user_id": "USR-NEW", "is_new_user": True,
            "created_at": datetime(2026, 6, 1, 15, 0), "delivery_address": "Main St 10",
            "items": [{"product_id": "P1", "quantity": 1, "price": 50000.01}]
         }, False, 0.5, 0.9, ["NEW_USER_MAX_AMOUNT_EXCEEDED"]),

        # Кейс 6: Комбинация нарушений: Ночь + Превышение суммы нового пользователя
        ({
            "order_id": "ORD-006", "user_id": "USR-NEW", "is_new_user": True,
            "created_at": datetime(2026, 6, 1, 23, 0), "delivery_address": "Main St 10",
            "items": [{"product_id": "P1", "quantity": 1, "price": 60000.0}]
         }, False, 0.8, 1.0, ["STORE_CLOSED", "NEW_USER_MAX_AMOUNT_EXCEEDED"]),
    ]
)
def test_validate_order_decision_table(clean_validator, order, expected_valid, expected_risk_min, expected_risk_max, reasons_contain):
    result = clean_validator.validate_order(order)
    assert result["valid"] == expected_valid
    assert expected_risk_min <= result["risk_score"] <= expected_risk_max
    for reason in reasons_contain:
        assert reason in result["reasons"]


# --- 2.3 PROPERTY-BASED ТЕСТЫ (HYPOTHESIS) ---

item_strategy = st.builds(
    dict,
    product_id=st.text(min_size=1, max_size=10, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"),
    quantity=st.integers(min_value=1, max_value=100),
    price=st.floats(min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False)
)

order_strategy = st.builds(
    dict,
    order_id=st.text(min_size=3, max_size=10),
    user_id=st.text(min_size=3, max_size=10),
    is_new_user=st.booleans(),
    created_at=st.datetimes(min_value=datetime(2026, 1, 1), max_value=datetime(2026, 12, 31)),
    delivery_address=st.text(min_size=5, max_size=50),
    items=st.lists(item_strategy, min_size=1, max_size=5)
)

# ИСПРАВЛЕНО: Добавлен HealthCheck.function_scoped_fixture для игнорирования предупреждения фикстур
@settings(
    max_examples=100, 
    suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.function_scoped_fixture]
)
@given(order=order_strategy)
def test_property_invariant_and_ranges(clean_validator, order):
    """Инвариант: Если order невалиден, должна быть минимум одна причина."""
    result = clean_validator.validate_order(order)
    
    assert isinstance(result["valid"], bool)
    assert 0.0 <= result["risk_score"] <= 1.0
    assert isinstance(result["reasons"], list)

    if not result["valid"]:
        assert len(result["reasons"]) >= 1


# ИСПРАВЛЕНО: Добавлен HealthCheck.function_scoped_fixture для игнорирования предупреждения фикстур
@settings(
    max_examples=50, 
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(order=order_strategy)
def test_property_monotonicity_by_time(clean_validator, order):
    """Монотонность по времени: Сдвиг внутри разрешенного окна не меняет логику хаотично."""
    order["created_at"] = order["created_at"].replace(hour=12, minute=0, second=0)
    
    res1 = clean_validator.validate_order(order)
    
    order_delayed = order.copy()
    order_delayed["created_at"] += timedelta(minutes=5)
    res2 = clean_validator.validate_order(order_delayed)
    
    assert res1["valid"] == res2["valid"]


# --- 2.4 ТЕСТЫ НЕСТАБИЛЬНОСТИ И ВРЕМЕНИ ---

def test_time_boundaries_exact_seconds(clean_validator):
    """Проверка жестких временных границ с точностью до секунды."""
    base_order = {
        "order_id": "T1", "user_id": "U1", "is_new_user": False,
        "delivery_address": "Address", "items": [{"product_id": "P1", "quantity": 1, "price": 10.0}]
    }

    # 1 секунда до открытия (07:59:59) -> Невалидно
    order_before = base_order.copy()
    order_before["created_at"] = datetime(2026, 6, 1, 7, 59, 59)
    assert clean_validator.validate_order(order_before)["valid"] is False

    # Ровно секунда открытия (08:00:00) -> Валидно
    order_open = base_order.copy()
    order_open["created_at"] = datetime(2026, 6, 1, 8, 0, 0)
    assert clean_validator.validate_order(order_open)["valid"] is True


def test_duplicate_orders_stability(clean_validator):
    """Проверка устойчивости к дубликатам."""
    order = {
        "order_id": "DUP-100", "user_id": "U1", "is_new_user": False,
        "created_at": datetime(2026, 6, 1, 14, 0), "delivery_address": "Address",
        "items": [{"product_id": "P1", "quantity": 1, "price": 10.0}]
    }
    
    res1 = clean_validator.validate_order(order)
    res2 = clean_validator.validate_order(order)
    
    assert res1["valid"] == res2["valid"]
    assert res1["risk_score"] == res2["risk_score"]


def test_chaos_mode_handling(chaos_validator):
    """Тест проверяет реакцию на хаос-режим."""
    order = {
        "order_id": "CH-1", "user_id": "U1", "is_new_user": False,
        "created_at": datetime(2026, 6, 1, 14, 0), "delivery_address": "Address",
        "items": [{"product_id": "P1", "quantity": 1, "price": 10.0}]
    }
    
    chaos_detected = False
    for _ in range(200):
        res = chaos_validator.validate_order(order)
        if "CHAOS_ERR" in res["reasons"] or res["risk_score"] == 999.0:
            chaos_detected = True
            break
            
    assert chaos_detected, "Режим хаоса не воспроизвелся за 200 итераций"

import pytest
from typing import Dict, Any

@pytest.fixture
def sample_order_data() -> Dict[str, Any]:
    """
    Фикстура с тестовыми данными заказа
    """
    return {
        "order_id": 1,
        "total": 500,
        "status": "PENDING"
    }

@pytest.fixture
def sample_order_data_2() -> Dict[str, Any]:
    """
    Фикстура с другими тестовыми данными заказа
    """
    return {
        "order_id": 2,
        "total": 750.50,
        "status": "CONFIRMED"
    }

@pytest.fixture
def invalid_order_data() -> Dict[str, Any]:
    """
    Фикстура с невалидными данными (без order_id)
    """
    return {
        "total": 500
    }

@pytest.fixture
def empty_order_data() -> Dict[str, Any]:
    """
    Фикстура с пустыми данными
    """
    return {}

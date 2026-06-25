# tests/test_api_client_improved.py
"""Улучшенные тесты для API клиента (достижение покрытия > 90%)"""

import pytest
import requests
import json
from unittest.mock import patch, Mock
from src.api_client import APIClient


# ============================================
# ТЕСТЫ ДЛЯ _make_request
# ============================================

def test_make_request_post_method():
    client = APIClient("https://example.com")
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"created": True, "id": 1}
    
    with patch('requests.Session.post') as mock_post:
        mock_post.return_value = mock_response
        result = client._make_request('POST', 'test', data={"key": "value"})
        assert result["created"] is True


def test_make_request_unsupported_method():
    client = APIClient("https://example.com")
    result = client._make_request('PATCH', 'test')
    assert result["error"] == "Unsupported method: PATCH"


def test_make_request_json_decode_error():
    client = APIClient("https://example.com")
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    
    with patch('requests.Session.get') as mock_get:
        mock_get.return_value = mock_response
        result = client._make_request('GET', 'test')
        assert result["error"] == "Invalid JSON response"


# ============================================
# ТЕСТЫ ДЛЯ get_hotel_info
# ============================================

def test_get_hotel_info_with_zero_id():
    client = APIClient("https://example.com")
    result = client.get_hotel_info(0)
    assert result["error"] == "Hotel ID must be positive"


def test_get_hotel_info_with_negative_id():
    client = APIClient("https://example.com")
    result = client.get_hotel_info(-1)
    assert result["error"] == "Hotel ID must be positive"


def test_get_hotel_info_404_not_found():
    client = APIClient("https://example.com")
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"error": "Hotel not found"}
    
    with patch('requests.Session.get') as mock_get:
        mock_get.return_value = mock_response
        result = client.get_hotel_info(999)
        assert result["error"] == "Hotel not found"


# ============================================
# ТЕСТЫ ДЛЯ create_payment
# ============================================

def test_create_payment_with_negative_amount():
    client = APIClient("https://example.com")
    result = client.create_payment(100, -500.0, "credit_card")
    assert result["error"] == "Amount must be positive"


def test_create_payment_with_zero_amount():
    client = APIClient("https://example.com")
    result = client.create_payment(100, 0.0, "credit_card")
    assert result["error"] == "Amount must be positive"


def test_create_payment_with_invalid_method():
    client = APIClient("https://example.com")
    result = client.create_payment(100, 500.0, "")
    assert result["error"] == "Invalid payment method"


def test_create_payment_with_float_amount():
    client = APIClient("https://example.com")
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"payment_id": 123, "status": "pending"}
    
    with patch('requests.Session.post') as mock_post:
        mock_post.return_value = mock_response
        result = client.create_payment(100, 500.50, "credit_card")
        assert result["payment_id"] == 123


# ============================================
# ТЕСТЫ ДЛЯ send_notification
# ============================================

def test_send_notification_empty_message():
    client = APIClient("https://example.com")
    result = client.send_notification(1, "", "email")
    assert result["error"] == "Message cannot be empty"


def test_send_notification_with_invalid_channel():
    client = APIClient("https://example.com")
    result = client.send_notification(1, "Test", "telegram")
    assert result["error"] == "Invalid channel: telegram"


def test_send_notification_with_all_channels():
    client = APIClient("https://example.com")
    channels = ["email", "sms", "push"]
    
    for channel in channels:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"notification_id": 999, "status": "sent", "channel": channel}
        
        with patch('requests.Session.post') as mock_post:
            mock_post.return_value = mock_response
            result = client.send_notification(1, "Test message", channel)
            assert result["channel"] == channel


# ============================================
# ТЕСТЫ ДЛЯ get_payment_status
# ============================================

def test_get_payment_status_with_zero_id():
    client = APIClient("https://example.com")
    result = client.get_payment_status(0)
    assert result["error"] == "Payment ID must be positive"


def test_get_payment_status_pending():
    client = APIClient("https://example.com")
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"payment_id": 12345, "status": "pending"}
    
    with patch('requests.Session.get') as mock_get:
        mock_get.return_value = mock_response
        result = client.get_payment_status(12345)
        assert result["status"] == "pending"


# ============================================
# ТЕСТЫ ДЛЯ refund_payment
# ============================================

def test_refund_payment_with_zero_id():
    client = APIClient("https://example.com")
    result = client.refund_payment(0)
    assert result["error"] == "Payment ID must be positive"


def test_refund_payment_already_refunded():
    client = APIClient("https://example.com")
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "Payment already refunded"}
    
    with patch('requests.Session.post') as mock_post:
        mock_post.return_value = mock_response
        result = client.refund_payment(12345)
        assert result["error"] == "Payment already refunded"


# ============================================
# ТЕСТЫ ДЛЯ batch_get_hotels
# ============================================

def test_batch_get_hotels_with_empty_list():
    client = APIClient("https://example.com")
    result = client.batch_get_hotels([])
    assert result["error"] == "Hotel list cannot be empty"


def test_batch_get_hotels_with_invalid_ids():
    client = APIClient("https://example.com")
    result = client.batch_get_hotels([1, -1, 0])
    assert result["error"] == "Invalid hotel IDs"


def test_batch_get_hotels_with_single_id():
    client = APIClient("https://example.com")
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"hotels": [{"id": 1, "name": "Grand Hotel"}]}
    
    with patch('requests.Session.get') as mock_get:
        mock_get.return_value = mock_response
        result = client.batch_get_hotels([1])
        assert len(result["hotels"]) == 1


# ============================================
# ТЕСТЫ НА РАЗЛИЧНЫЕ HTTP СТАТУСЫ
# ============================================

@pytest.mark.parametrize("status_code, expected_error", [
    (400, "Bad Request"),
    (401, "Unauthorized"),
    (403, "Forbidden"),
    (404, "Not Found"),
    (500, "Internal Server Error"),
    (502, "Bad Gateway"),
    (503, "Service Unavailable"),
])
def test_http_error_status_codes(status_code, expected_error):
    client = APIClient("https://example.com")
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = {"error": expected_error}
    
    with patch('requests.Session.get') as mock_get:
        mock_get.return_value = mock_response
        result = client.get_hotel_info(1)
        assert result["error"] == expected_error


# ============================================
# ТЕСТЫ НА ТАЙМАУТЫ
# ============================================

@pytest.mark.parametrize("timeout_value", [1, 5, 10, 30, 60])
def test_custom_timeout_values(timeout_value):
    """Тестирование различных значений таймаута"""
    client = APIClient("https://example.com", timeout=timeout_value)
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "OK"}
    
    with patch('requests.Session.get') as mock_get:
        mock_get.return_value = mock_response
        client.get_hotel_info(1)
        
        # ИСПРАВЛЕНО: проверяем только timeout, без headers
        args, kwargs = mock_get.call_args
        assert args[0] == "https://example.com/hotels/1"
        assert kwargs["timeout"] == timeout_value


def test_timeout_exception_handling():
    client = APIClient("https://example.com", timeout=1)
    
    with patch('requests.Session.get') as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout()
        result = client.get_hotel_info(1)
        assert result["error"] == "Timeout occurred"

# tests/test_api_client.py
"""Готовые тесты для API клиента"""

import pytest
import requests
from unittest.mock import patch, Mock
from src.api_client import APIClient


def test_get_hotel_info_success():
    """Успешное получение информации об отеле"""
    client = APIClient("https://example.com")
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1,
        "name": "Grand Hotel",
        "rating": 4.5
    }
    
    with patch('requests.Session.get') as mock_get:
        mock_get.return_value = mock_response
        result = client.get_hotel_info(1)
        
        assert result["id"] == 1
        assert result["name"] == "Grand Hotel"


def test_get_hotel_info_timeout():
    """Таймаут при получении информации об отеле"""
    client = APIClient("https://example.com")
    
    with patch('requests.Session.get') as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout()
        result = client.get_hotel_info(1)
        
        assert result["error"] == "Timeout occurred"


def test_get_hotel_info_connection_error():
    """Ошибка соединения при получении информации об отеле"""
    client = APIClient("https://example.com")
    
    with patch('requests.Session.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()
        result = client.get_hotel_info(1)
        
        assert result["error"] == "Connection error"


def test_create_payment_success():
    """Успешное создание платежа"""
    client = APIClient("https://example.com")
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "payment_id": 12345,
        "status": "pending"
    }
    
    with patch('requests.Session.post') as mock_post:
        mock_post.return_value = mock_response
        result = client.create_payment(
            booking_id=100,
            amount=500.0,
            payment_method="credit_card"
        )
        
        assert result["payment_id"] == 12345
        assert result["status"] == "pending"


def test_create_payment_timeout():
    """Таймаут при создании платежа"""
    client = APIClient("https://example.com")
    
    with patch('requests.Session.post') as mock_post:
        mock_post.side_effect = requests.exceptions.Timeout()
        result = client.create_payment(100, 500.0, "credit_card")
        
        assert result["error"] == "Timeout occurred"


def test_send_notification_success():
    """Успешная отправка уведомления"""
    client = APIClient("https://example.com")
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "notification_id": 999,
        "status": "sent"
    }
    
    with patch('requests.Session.post') as mock_post:
        mock_post.return_value = mock_response
        result = client.send_notification(
            user_id=1,
            message="Your booking is confirmed",
            channel="email"
        )
        
        assert result["notification_id"] == 999
        assert result["status"] == "sent"


def test_send_notification_connection_error():
    """Ошибка соединения при отправке уведомления"""
    client = APIClient("https://example.com")
    
    with patch('requests.Session.post') as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectionError()
        result = client.send_notification(1, "Test message")
        
        assert result["error"] == "Connection error"


def test_get_payment_status_success():
    """Успешное получение статуса платежа"""
    client = APIClient("https://example.com")
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "payment_id": 12345,
        "status": "completed"
    }
    
    with patch('requests.Session.get') as mock_get:
        mock_get.return_value = mock_response
        result = client.get_payment_status(12345)
        
        assert result["payment_id"] == 12345
        assert result["status"] == "completed"


def test_refund_payment_success():
    """Успешный возврат платежа"""
    client = APIClient("https://example.com")
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "refund_id": 6789,
        "status": "processed"
    }
    
    with patch('requests.Session.post') as mock_post:
        mock_post.return_value = mock_response
        result = client.refund_payment(12345)
        
        assert result["refund_id"] == 6789
        assert result["status"] == "processed"


def test_batch_get_hotels_success():
    """Успешное получение информации о нескольких отелях"""
    client = APIClient("https://example.com")
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "hotels": [
            {"id": 1, "name": "Hotel A"},
            {"id": 2, "name": "Hotel B"}
        ]
    }
    
    with patch('requests.Session.get') as mock_get:
        mock_get.return_value = mock_response
        result = client.batch_get_hotels([1, 2])
        
        assert len(result["hotels"]) == 2

# src/api_client.py
"""
Модуль для работы с внешними API (платежные системы, уведомления, отели)
"""

import requests
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

class APIClient:
    """Клиент для взаимодействия с внешними API"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
    def _make_request(self, method: str, endpoint: str, 
                      data: Optional[Dict] = None,
                      headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Базовый метод для выполнения HTTP запросов"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = headers or {}
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=self.timeout, headers=headers)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=self.timeout, headers=headers)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, timeout=self.timeout, headers=headers)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=self.timeout, headers=headers)
            else:
                return {"error": f"Unsupported method: {method}"}
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    return {"error": error_data.get("error", f"HTTP {response.status_code}")}
                except:
                    return {"error": f"HTTP {response.status_code}"}
            
            return response.json()
            
        except requests.exceptions.Timeout:
            return {"error": "Timeout occurred", "status": "timeout"}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection error", "status": "connection_error"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response", "status": "json_error"}
        except Exception as e:
            return {"error": str(e), "status": "unknown_error"}

    def get_hotel_info(self, hotel_id: int) -> Dict[str, Any]:
        """Получение информации об отеле"""
        if hotel_id <= 0:
            return {"error": "Hotel ID must be positive"}
        return self._make_request('GET', f'hotels/{hotel_id}')

    def create_payment(self, booking_id: int, amount: float, 
                       payment_method: str) -> Dict[str, Any]:
        """Создание платежа через внешнюю платежную систему"""
        if amount <= 0:
            return {"error": "Amount must be positive"}
        if not payment_method or not isinstance(payment_method, str):
            return {"error": "Invalid payment method"}
        
        data = {
            'booking_id': booking_id,
            'amount': amount,
            'method': payment_method,
            'timestamp': datetime.now().isoformat()
        }
        return self._make_request('POST', 'payments', data=data)

    def send_notification(self, user_id: int, message: str, 
                          channel: str = 'email') -> Dict[str, Any]:
        """Отправка уведомления пользователю"""
        if not message or not message.strip():
            return {"error": "Message cannot be empty"}
        if channel not in ['email', 'sms', 'push']:
            return {"error": f"Invalid channel: {channel}"}
        
        data = {
            'user_id': user_id,
            'message': message,
            'channel': channel
        }
        return self._make_request('POST', 'notifications', data=data)

    def get_payment_status(self, payment_id: int) -> Dict[str, Any]:
        """Получение статуса платежа"""
        if payment_id <= 0:
            return {"error": "Payment ID must be positive"}
        return self._make_request('GET', f'payments/{payment_id}/status')

    def refund_payment(self, payment_id: int) -> Dict[str, Any]:
        """Возврат платежа"""
        if payment_id <= 0:
            return {"error": "Payment ID must be positive"}
        return self._make_request('POST', f'payments/{payment_id}/refund')

    def batch_get_hotels(self, hotel_ids: List[int]) -> Dict[str, Any]:
        """Получение информации о нескольких отелях"""
        if not hotel_ids:
            return {"error": "Hotel list cannot be empty"}
        if any(h <= 0 for h in hotel_ids):
            return {"error": "Invalid hotel IDs"}
        
        return self._make_request('GET', f'hotels?ids={",".join(map(str, hotel_ids))}')

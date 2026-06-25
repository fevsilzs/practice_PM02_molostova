import json
import requests
from typing import Dict, Union, List, Optional

class APIClient:
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.timeout = timeout

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict:
        """
        Внутренний метод для выполнения HTTP-запросов.
        Обрабатывает ошибки сети и декодирования JSON.
        """
        # --- ИСПРАВЛЕНИЕ 1: Проверка на поддерживаемый метод ---
        allowed_methods = ["GET", "POST", "PUT", "DELETE"]
        if method.upper() not in allowed_methods:
            raise ValueError(f"Unsupported method: {method}")

        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json_data,
                timeout=self.timeout
            )
            response.raise_for_status()  # Вызовет исключение для 4xx/5xx статусов
            return response.json()

        except requests.exceptions.HTTPError:
            # Возвращаем JSON-ответ сервера, если он есть, иначе пустой словарь
            try:
                return response.json()
            except (json.JSONDecodeError, AttributeError):
                return {}

        except (requests.exceptions.RequestException, json.JSONDecodeError):
            # --- ИСПРАВЛЕНИЕ 2: Обработка ошибки декодирования JSON ---
            # Возвращаем пустой словарь, если JSON не удалось распарсить
            return {}

    # --- ИСПРАВЛЕНИЕ 3: Валидация входных данных (сообщения об ошибках) ---
    def get_hotel_info(self, hotel_id: int) -> Dict:
        if hotel_id <= 0:
            return {"error": "Invalid hotel ID"}
        return self._make_request("GET", f"/hotels/{hotel_id}")

    def create_payment(self, user_id: int, amount: float, method: str) -> Dict:
        if amount <= 0:
            return {"error": "Amount must be greater than 0"}
        data = {"user_id": user_id, "amount": amount, "method": method}
        return self._make_request("POST", "/payments", json_data=data)

    def get_payment_status(self, payment_id: int) -> Dict:
        if payment_id <= 0:
            return {"error": "Invalid payment ID"}
        return self._make_request("GET", f"/payments/{payment_id}/status")

    def refund_payment(self, payment_id: int) -> Dict:
        if payment_id <= 0:
            return {"error": "Invalid payment ID"}
        return self._make_request("POST", f"/payments/{payment_id}/refund")

    def send_notification(self, user_id: int, message: str, channels: List[str]) -> Dict:
        data = {"user_id": user_id, "message": message, "channels": channels}
        return self._make_request("POST", "/notifications", json_data=data)

    def batch_get_hotels(self, hotel_ids: List[int]) -> Dict:
        params = {"ids": ",".join(map(str, hotel_ids))}
        return self._make_request("GET", "/hotels/batch", params=params)

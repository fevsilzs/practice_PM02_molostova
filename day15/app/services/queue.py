import json
from typing import Dict, Any, Optional

class OrderQueueService:
    """Сервис для отправки заказов в очередь"""
    
    EXCHANGE = "order.exchange"
    ROUTING_KEY = "order.created"
    
    def __init__(self, rabbit_client):
        """
        Инициализация сервиса с клиентом RabbitMQ
        
        Args:
            rabbit_client: Клиент для взаимодействия с RabbitMQ
        """
        self.rabbit = rabbit_client
    
    def send_order_to_queue(self, order_data: Dict[str, Any]) -> bool:
        """
        Отправляет данные заказа в очередь
        
        Args:
            order_data: Словарь с данными заказа
            
        Returns:
            bool: True если отправка успешна
            
        Raises:
            ValueError: Если order_data пустой или не содержит обязательных полей
        """
        if not order_data:
            raise ValueError("Order data cannot be empty")
        
        if "order_id" not in order_data:
            raise ValueError("Order data must contain 'order_id'")
        
        if "total" not in order_data:
            raise ValueError("Order data must contain 'total'")
        
        try:
            # Сериализуем данные в JSON и кодируем в байты
            message_body = json.dumps(order_data).encode('utf-8')
            
            # Публикуем сообщение в очередь
            self.rabbit.publish(
                exchange=self.EXCHANGE,
                routing_key=self.ROUTING_KEY,
                body=message_body
            )
            return True
        except Exception as e:
            # Логирование ошибки можно добавить здесь
            raise RuntimeError(f"Failed to send order to queue: {str(e)}")
    
    def send_order_object(self, order) -> bool:
        """
        Отправляет объект заказа в очередь
        
        Args:
            order: Объект заказа с методом to_dict()
            
        Returns:
            bool: True если отправка успешна
        """
        return self.send_order_to_queue(order.to_dict())

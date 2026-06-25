import json
import pytest
from unittest.mock import Mock, call

from app.services.queue import OrderQueueService
from app.models import Order


class TestOrderQueueService:
    """Тестовый класс для OrderQueueService"""
    
    def test_send_order_to_queue_success(self, mocker, sample_order_data):
        """
        Тест успешной отправки сообщения в очередь
        Проверяет, что publish вызван ровно 1 раз с правильными параметрами
        """
        # Arrange (Подготовка)
        mock_rabbit = mocker.Mock()
        service = OrderQueueService(mock_rabbit)
        expected_body = json.dumps(sample_order_data).encode('utf-8')
        
        # Act (Действие)
        result = service.send_order_to_queue(sample_order_data)
        
        # Assert (Проверка)
        mock_rabbit.publish.assert_called_once_with(
            exchange="order.exchange",
            routing_key="order.created",
            body=expected_body
        )
        assert result is True
    
    def test_send_order_to_queue_with_different_data(self, mocker, sample_order_data_2):
        """
        Тест отправки сообщения с другими данными
        """
        # Arrange
        mock_rabbit = mocker.Mock()
        service = OrderQueueService(mock_rabbit)
        expected_body = json.dumps(sample_order_data_2).encode('utf-8')
        
        # Act
        result = service.send_order_to_queue(sample_order_data_2)
        
        # Assert
        mock_rabbit.publish.assert_called_once_with(
            exchange="order.exchange",
            routing_key="order.created",
            body=expected_body
        )
        assert result is True
    
    def test_send_order_object_to_queue(self, mocker, sample_order_data):
        """
        Тест отправки объекта заказа в очередь
        """
        # Arrange
        mock_rabbit = mocker.Mock()
        service = OrderQueueService(mock_rabbit)
        order = Order(
            order_id=sample_order_data["order_id"],
            total=sample_order_data["total"]
        )
        expected_body = json.dumps(order.to_dict()).encode('utf-8')
        
        # Act
        result = service.send_order_object(order)
        
        # Assert
        mock_rabbit.publish.assert_called_once_with(
            exchange="order.exchange",
            routing_key="order.created",
            body=expected_body
        )
        assert result is True
    
    def test_send_order_to_queue_empty_data_raises_error(self, mocker, empty_order_data):
        """
        Тест: при передаче пустых данных должно выбрасываться исключение
        """
        # Arrange
        mock_rabbit = mocker.Mock()
        service = OrderQueueService(mock_rabbit)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Order data cannot be empty"):
            service.send_order_to_queue(empty_order_data)
        
        mock_rabbit.publish.assert_not_called()
    
    def test_send_order_to_queue_missing_order_id_raises_error(self, mocker, invalid_order_data):
        """
        Тест: при отсутствии order_id должно выбрасываться исключение
        """
        # Arrange
        mock_rabbit = mocker.Mock()
        service = OrderQueueService(mock_rabbit)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Order data must contain 'order_id'"):
            service.send_order_to_queue(invalid_order_data)
        
        mock_rabbit.publish.assert_not_called()
    
    def test_send_order_to_queue_missing_total_raises_error(self, mocker):
        """
        Тест: при отсутствии total должно выбрасываться исключение
        """
        # Arrange
        mock_rabbit = mocker.Mock()
        service = OrderQueueService(mock_rabbit)
        invalid_data = {"order_id": 1}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Order data must contain 'total'"):
            service.send_order_to_queue(invalid_data)
        
        mock_rabbit.publish.assert_not_called()
    
    def test_send_order_to_queue_publish_failure(self, mocker, sample_order_data):
        """
        Тест: при ошибке публикации должно выбрасываться исключение
        """
        # Arrange
        mock_rabbit = mocker.Mock()
        mock_rabbit.publish.side_effect = Exception("Connection refused")
        service = OrderQueueService(mock_rabbit)
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="Failed to send order to queue: Connection refused"):
            service.send_order_to_queue(sample_order_data)
        
        mock_rabbit.publish.assert_called_once()
    
    def test_send_order_to_queue_publish_call_count(self, mocker, sample_order_data):
        """
        Тест проверки количества вызовов publish с использованием spy
        Проверяет, что метод publish вызывается правильное количество раз
        и с правильными параметрами при нескольких вызовах
        """
        # Arrange
        mock_rabbit = mocker.Mock()
        service = OrderQueueService(mock_rabbit)
        
        # Act - вызываем метод несколько раз
        service.send_order_to_queue(sample_order_data)
        service.send_order_to_queue({"order_id": 2, "total": 300})
        
        # Assert - проверяем количество вызовов
        assert mock_rabbit.publish.call_count == 2
        
        # Проверяем конкретные вызовы
        expected_calls = [
            call(
                exchange="order.exchange",
                routing_key="order.created",
                body=json.dumps(sample_order_data).encode('utf-8')
            ),
            call(
                exchange="order.exchange",
                routing_key="order.created",
                body=json.dumps({"order_id": 2, "total": 300}).encode('utf-8')
            )
        ]
        mock_rabbit.publish.assert_has_calls(expected_calls)

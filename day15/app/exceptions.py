class QueueServiceError(Exception):
    """Базовое исключение для ошибок сервиса очередей"""
    pass

class OrderDataValidationError(QueueServiceError):
    """Ошибка валидации данных заказа"""
    pass

class QueuePublishError(QueueServiceError):
    """Ошибка публикации в очередь"""
    pass

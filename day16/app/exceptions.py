
class EntityNotFoundException(Exception):
    """Исключение, когда сущность не найдена в базе данных."""
    pass

class DeliveryCalculationException(Exception):
    """Исключение при ошибке в расчете стоимости доставки."""
    pass

class ValidationException(Exception):
    """Исключение при ошибке валидации данных."""
    pass


class DomainError(Exception):
    """Базовое исключение для всех доменных ошибок."""
    pass

class NotFoundError(DomainError):
    """Объект не найден."""
    pass

class ValidationError(DomainError):
    """Ошибка валидации входных данных."""
    pass

class BusinessRuleViolation(DomainError):
    """Нарушение бизнес-правила."""
    pass

class OrderNotFoundError(NotFoundError):
    pass

class CourierNotFoundError(NotFoundError):
    pass

class NoAvailableCourierError(BusinessRuleViolation):
    pass

class InvalidOrderStatusError(BusinessRuleViolation):
    pass

class RouteCalculationError(DomainError):
    """Ошибка при расчёте маршрута."""
    pass

class OrderAlreadyAssignedError(BusinessRuleViolation):
    pass

class CourierMaxOrdersExceededError(BusinessRuleViolation):
    pass

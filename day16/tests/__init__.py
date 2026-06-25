class EntityNotFoundException(Exception):
    """Исключение, выбрасываемое когда сущность не найдена"""
    def __init__(self, entity_name: str, entity_id: int):
        self.entity_name = entity_name
        self.entity_id = entity_id
        super().__init__(f"{entity_name} with id {entity_id} not found")


class DeliveryCalculationException(Exception):
    """Исключение при расчете стоимости доставки"""
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(f"Delivery calculation failed: {message}")


class ValidationException(Exception):
    """Исключение при валидации данных"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Validation error: {message}")
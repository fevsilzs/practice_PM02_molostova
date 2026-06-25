import logging
import random
from typing import Optional, Tuple
from src.domain.entities import Address
from src.domain.exceptions import RouteCalculationError

logger = logging.getLogger(__name__)

class RoutingService:
    """
    Сервис расчёта маршрутов.
    В реальном проекте здесь был бы вызов OSRM API.
    """
    
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
        # В реальном проекте здесь настройка клиента OSRM
        # self.osrm_client = OSRMClient(base_url="http://router.project-osrm.org")
    
    def calculate_distance_and_time(
        self, 
        pickup: Address, 
        delivery: Address,
        speed_kmh: float = 40.0
    ) -> Tuple[float, int]:
        """
        Рассчитать расстояние (км) и время доставки (минуты).
        В реальности - вызов OSRM API.
        """
        try:
            if self.use_mock:
                # Мок-реализация для тестирования
                distance = self._mock_distance(pickup, delivery)
                time_minutes = int((distance / speed_kmh) * 60)
                logger.debug(f"Route calculated: {distance:.2f} km, {time_minutes} min")
                return distance, time_minutes
            else:
                # Здесь реальный вызов OSRM
                # response = self.osrm_client.route(
                #     coordinates=[(pickup.longitude, pickup.latitude), 
                #                 (delivery.longitude, delivery.latitude)]
                # )
                # distance = response['routes'][0]['distance'] / 1000
                # time_minutes = response['routes'][0]['duration'] / 60
                # return distance, int(time_minutes)
                raise NotImplementedError("Real OSRM integration not implemented")
        except Exception as e:
            logger.error(f"Route calculation failed: {e}")
            raise RouteCalculationError(f"Failed to calculate route: {str(e)}")
    
    def _mock_distance(self, pickup: Address, delivery: Address) -> float:
        """Мок-расчёт расстояния на основе координат."""
        if pickup.latitude and pickup.longitude and delivery.latitude and delivery.longitude:
            # Приблизительный расчёт по формуле гаверсинусов
            import math
            lat1, lon1 = pickup.latitude, pickup.longitude
            lat2, lon2 = delivery.latitude, delivery.longitude
            R = 6371  # Радиус Земли в км
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            return R * c
        else:
            # Случайное расстояние, если координат нет
            return random.uniform(1.0, 15.0)
    
    def find_nearest_available_courier(
        self, 
        pickup: Address, 
        couriers: list
    ) -> Optional[dict]:
        """
        Найти ближайшего доступного курьера к точке забора.
        """
        if not couriers:
            return None
        
        # В реальности нужно было бы рассчитать расстояние до каждого курьера
        # и выбрать ближайшего. Для демонстрации возвращаем первого.
        return couriers[0]

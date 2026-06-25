import sys

import os



\# Добавляем корневую папку в путь

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(\_\_file\_\_))))



import pytest

from src.services.courier\_service import CourierService

from src.services.routing import RoutingService

from src.repositories.in\_memory import InMemoryOrderRepository, InMemoryCourierRepository

from src.domain.exceptions import ValidationError, OrderNotFoundError





def test\_create\_order():

&#x20;   """Тест создания заказа"""

&#x20;   print("\\n🧪 Тест 1: Создание заказа")

&#x20;   

&#x20;   # Подготовка

&#x20;   order\_repo = InMemoryOrderRepository()

&#x20;   courier\_repo = InMemoryCourierRepository()

&#x20;   routing = RoutingService(use\_mock=True)

&#x20;   service = CourierService(order\_repo, courier\_repo, routing)

&#x20;   

&#x20;   # Данные для заказа

&#x20;   order\_data = {

&#x20;       "customer\_name": "Тестовый Клиент",

&#x20;       "customer\_phone": "+79111234567",

&#x20;       "pickup": {

&#x20;           "street": "ул. Тестовая, 1",

&#x20;           "city": "Москва",

&#x20;           "postal\_code": "101000",

&#x20;           "latitude": 55.7558,

&#x20;           "longitude": 37.6173

&#x20;       },

&#x20;       "delivery": {

&#x20;           "street": "ул. Тестовая, 2",

&#x20;           "city": "Москва",

&#x20;           "postal\_code": "101001",

&#x20;           "latitude": 55.7516,

&#x20;           "longitude": 37.6189

&#x20;       }

&#x20;   }

&#x20;   

&#x20;   # Действие

&#x20;   order = service.create\_order(order\_data)

&#x20;   

&#x20;   # Проверки

&#x20;   assert order.id > 0, "ID заказа должен быть больше 0"

&#x20;   assert order.customer\_name == "Тестовый Клиент", "Имя клиента не совпадает"

&#x20;   assert order.status.value == "pending", "Статус должен быть pending"

&#x20;   print(f"   ✅ Заказ создан: ID={order.id}")





def test\_create\_order\_invalid\_data():

&#x20;   """Тест создания заказа с невалидными данными"""

&#x20;   print("\\n🧪 Тест 2: Создание заказа с невалидными данными")

&#x20;   

&#x20;   order\_repo = InMemoryOrderRepository()

&#x20;   courier\_repo = InMemoryCourierRepository()

&#x20;   routing = RoutingService(use\_mock=True)

&#x20;   service = CourierService(order\_repo, courier\_repo, routing)

&#x20;   

&#x20;   # Невалидные данные (короткое имя)

&#x20;   invalid\_data = {

&#x20;       "customer\_name": "A",  # Слишком короткое

&#x20;       "customer\_phone": "+79111234567",

&#x20;       "pickup": {

&#x20;           "street": "ул. Тест, 1",

&#x20;           "city": "Москва",

&#x20;           "postal\_code": "101000"

&#x20;       },

&#x20;       "delivery": {

&#x20;           "street": "ул. Тест, 2",

&#x20;           "city": "Москва",

&#x20;           "postal\_code": "101001"

&#x20;       }

&#x20;   }

&#x20;   

&#x20;   # Должна быть ошибка валидации

&#x20;   try:

&#x20;       service.create\_order(invalid\_data)

&#x20;       assert False, "Должна быть ошибка валидации"

&#x20;   except ValidationError:

&#x20;       print("   ✅ Ошибка валидации поймана")





def test\_register\_courier():

&#x20;   """Тест регистрации курьера"""

&#x20;   print("\\n🧪 Тест 3: Регистрация курьера")

&#x20;   

&#x20;   order\_repo = InMemoryOrderRepository()

&#x20;   courier\_repo = InMemoryCourierRepository()

&#x20;   routing = RoutingService(use\_mock=True)

&#x20;   service = CourierService(order\_repo, courier\_repo, routing)

&#x20;   

&#x20;   courier\_data = {

&#x20;       "name": "Тестовый Курьер",

&#x20;       "phone": "+79119876543",

&#x20;       "max\_orders": 3

&#x20;   }

&#x20;   

&#x20;   courier = service.register\_courier(courier\_data)

&#x20;   

&#x20;   assert courier.id > 0, "ID курьера должен быть больше 0"

&#x20;   assert courier.name == "Тестовый Курьер", "Имя курьера не совпадает"

&#x20;   assert courier.status.value == "available", "Статус должен быть available"

&#x20;   print(f"   ✅ Курьер зарегистрирован: ID={courier.id}")





def test\_assign\_courier():

&#x20;   """Тест назначения курьера на заказ"""

&#x20;   print("\\n🧪 Тест 4: Назначение курьера на заказ")

&#x20;   

&#x20;   order\_repo = InMemoryOrderRepository()

&#x20;   courier\_repo = InMemoryCourierRepository()

&#x20;   routing = RoutingService(use\_mock=True)

&#x20;   service = CourierService(order\_repo, courier\_repo, routing)

&#x20;   

&#x20;   # Создаём заказ

&#x20;   order\_data = {

&#x20;       "customer\_name": "Клиент",

&#x20;       "customer\_phone": "+79111234567",

&#x20;       "pickup": {

&#x20;           "street": "ул. Тест, 1",

&#x20;           "city": "Москва",

&#x20;           "postal\_code": "101000"

&#x20;       },

&#x20;       "delivery": {

&#x20;           "street": "ул. Тест, 2",

&#x20;           "city": "Москва",

&#x20;           "postal\_code": "101001"

&#x20;       }

&#x20;   }

&#x20;   order = service.create\_order(order\_data)

&#x20;   

&#x20;   # Создаём курьера

&#x20;   courier\_data = {

&#x20;       "name": "Курьер",

&#x20;       "phone": "+79119876543",

&#x20;       "max\_orders": 3

&#x20;   }

&#x20;   courier = service.register\_courier(courier\_data)

&#x20;   

&#x20;   # Назначаем

&#x20;   assigned\_order = service.assign\_courier(order.id, courier.id)

&#x20;   

&#x20;   assert assigned\_order.courier\_id == courier.id, "Курьер не назначен"

&#x20;   assert assigned\_order.status.value == "assigned", "Статус должен быть assigned"

&#x20;   print(f"   ✅ Заказ {assigned\_order.id} назначен курьеру {assigned\_order.courier\_id}")





def test\_update\_order\_status():

&#x20;   """Тест обновления статуса заказа"""

&#x20;   print("\\n🧪 Тест 5: Обновление статуса заказа")

&#x20;   

&#x20;   order\_repo = InMemoryOrderRepository()

&#x20;   courier\_repo = InMemoryCourierRepository()

&#x20;   routing = RoutingService(use\_mock=True)

&#x20;   service = CourierService(order\_repo, courier\_repo, routing)

&#x20;   

&#x20;   # Создаём заказ

&#x20;   order\_data = {

&#x20;       "customer\_name": "Клиент",

&#x20;       "customer\_phone": "+79111234567",

&#x20;       "pickup": {

&#x20;           "street": "ул. Тест, 1",

&#x20;           "city": "Москва",

&#x20;           "postal\_code": "101000"

&#x20;       },

&#x20;       "delivery": {

&#x20;           "street": "ул. Тест, 2",

&#x20;           "city": "Москва",

&#x20;           "postal\_code": "101001"

&#x20;       }

&#x20;   }

&#x20;   order = service.create\_order(order\_data)

&#x20;   

&#x20;   # Меняем статус на in\_progress

&#x20;   updated = service.update\_order\_status(order.id, "in\_progress")

&#x20;   assert updated.status.value == "in\_progress", "Статус должен быть in\_progress"

&#x20;   print(f"   ✅ Статус изменён на: {updated.status.value}")





def test\_get\_order\_not\_found():

&#x20;   """Тест получения несуществующего заказа"""

&#x20;   print("\\n🧪 Тест 6: Получение несуществующего заказа")

&#x20;   

&#x20;   order\_repo = InMemoryOrderRepository()

&#x20;   courier\_repo = InMemoryCourierRepository()

&#x20;   routing = RoutingService(use\_mock=True)

&#x20;   service = CourierService(order\_repo, courier\_repo, routing)

&#x20;   

&#x20;   try:

&#x20;       service.get\_order(999)

&#x20;       assert False, "Должна быть ошибка OrderNotFoundError"

&#x20;   except OrderNotFoundError:

&#x20;       print("   ✅ Ошибка OrderNotFoundError поймана")





def run\_all\_tests():

&#x20;   """Запуск всех тестов"""

&#x20;   print("\\n" + "="\*60)

&#x20;   print("ЗАПУСК ТЕСТОВ КУРЬЕРСКОЙ СЛУЖБЫ")

&#x20;   print("="\*60)

&#x20;   

&#x20;   tests = \[

&#x20;       test\_create\_order,

&#x20;       test\_create\_order\_invalid\_data,

&#x20;       test\_register\_courier,

&#x20;       test\_assign\_courier,

&#x20;       test\_update\_order\_status,

&#x20;       test\_get\_order\_not\_found

&#x20;   ]

&#x20;   

&#x20;   passed = 0

&#x20;   failed = 0

&#x20;   

&#x20;   for test in tests:

&#x20;       try:

&#x20;           test()

&#x20;           passed += 1

&#x20;       except Exception as e:

&#x20;           failed += 1

&#x20;           print(f"   ❌ Ошибка: {e}")

&#x20;   

&#x20;   print("\\n" + "="\*60)

&#x20;   print(f"РЕЗУЛЬТАТЫ: {passed} пройдено, {failed} ошибок")

&#x20;   print("="\*60)

&#x20;   

&#x20;   return failed == 0





if \_\_name\_\_ == "\_\_main\_\_":

&#x20;   success = run\_all\_tests()

&#x20;   exit(0 if success else 1)


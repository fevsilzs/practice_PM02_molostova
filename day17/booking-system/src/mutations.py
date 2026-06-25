
from mutagen import *

# Импортируем файл, который будем мутировать.
# Важно: это должен быть именно путь для импорта Python.
import src.api_client as api_client_file

# Создаем мутацию: меняем условие 'if hotel_id <= 0' на 'if hotel_id < 0'
# Если тесты не упадут, значит, они не проверяют случай с hotel_id == 0.

@mutate_of(api_client_file.APIClient.get_hotel_info)
def mutate_get_hotel_info_if_condition(mutation):
    # Заменяем "<=" на "<"
    return mutation.replace("<=", "<")

# Создаем мутацию: меняем return price * (total_discount / 100) на return price * total_discount
# Если тесты не упадут, значит, они не проверяют правильность расчета скидки.

@mutate_of(api_client_file.APIClient.calculate_discount)
def mutate_calculate_discount_return(mutation):
    # Заменяем "/ 100" на "" (удаляем деление)
    return mutation.replace(" / 100", "")

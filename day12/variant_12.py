import numpy as np
import tracemalloc
import time
import sys

# Глобальный кеш для хранения результатов - потенциальная утечка
RESULT_CACHE = {}

def process_matrix_operation(matrix_a, matrix_b, operation_type='multiply'):
    """
    Обработка матричных операций с несколькими ошибками:
    1. Ошибка индексации в многомерном массиве
    2. Логическая ошибка в матричном умножении
    3. Утечка памяти (временные массивы не удаляются)
    4. Ошибка с np.vectorize
    """
    
    # ОШИБКА 1: Обработка с np.vectorize - неправильное применение
    def custom_func(x):
        # ЛОГИЧЕСКАЯ ОШИБКА: неправильное условие
        if x > 0:
            return np.sqrt(x)  # sqrt от отрицательного при x < 0 не обработано
        else:
            return x * 2
    
    vectorized_func = np.vectorize(custom_func)
    
    # ОШИБКА 2: Индексация с ошибкой
    try:
        # Пытаемся получить доступ к несуществующему срезу
        temp_a = matrix_a[:, :, 0]  # Если matrix_a 2D, это вызовет ошибку
    except:
        # Восстанавливаемся, но создаем копию вместо view - утечка
        temp_a = matrix_a.copy()
    
    # ОШИБКА 3: Логическая ошибка в матричном умножении
    if operation_type == 'multiply':
        # Должно быть np.dot(matrix_a, matrix_b), а здесь неправильная операция
        result = matrix_a * matrix_b  # Поэлементное умножение вместо матричного!
    elif operation_type == 'add':
        result = matrix_a + matrix_b
    else:
        result = matrix_a
    
    # ОШИБКА 4: Создание временных массивов без очистки - утечка
    temp_results = []
    for i in range(10):
        # Создаем большие временные массивы
        temp_array = np.random.rand(1000, 1000) * 1000
        # Применяем vectorize с ошибкой
        processed = vectorized_func(temp_array)
        temp_results.append(processed)
        # НЕ ОЧИЩАЕМ temp_array и processed - утечка!
    
    # Кешируем результат - еще одна утечка
    cache_key = f"{id(matrix_a)}_{id(matrix_b)}_{operation_type}"
    RESULT_CACHE[cache_key] = result
    
    # ОШИБКА 5: Ошибка в матричном умножении для больших массивов
    if matrix_a.shape[0] > 100:
        # Неправильное использование broadcasting
        result = result + np.random.rand(matrix_a.shape[0], 1)  # Ошибка размерности
    
    return result

def process_booking_data(data):
    """Обработка входных данных с матрицами"""
    results = []
    
    for i, item in enumerate(data):
        # ОШИБКА 6: Индексация с ошибкой - обращение по несуществующему ключу
        matrix_a = item['matrix_a']  # KeyError, если ключа нет
        matrix_b = item['matrix_b']
        op_type = item.get('operation', 'multiply')
        
        # ОШИБКА 7: Ошибка при работе с многомерными массивами
        if len(matrix_a.shape) == 3:
            # Неправильная индексация
            matrix_a = matrix_a[0, :, :]  # Если матрица 3D, но индексация неверна
        
        result = process_matrix_operation(matrix_a, matrix_b, op_type)
        results.append(result)
    
    return results

# Функция для демонстрации утечки памяти
def run_memory_leak_demo():
    """Запуск демонстрации утечки памяти"""
    print("Запуск демонстрации утечки памяти...")
    
    # Создаем тестовые данные
    test_data = [
        {
            'matrix_a': np.random.rand(50, 50),
            'matrix_b': np.random.rand(50, 50),
            'operation': 'multiply'
        },
        {
            'matrix_a': np.random.rand(100, 100),
            'matrix_b': np.random.rand(100, 100),
            'operation': 'add'
        },
        # ОШИБКА 8: Элемент без ключа 'matrix_b'
        {
            'matrix_a': np.random.rand(30, 30),
            'operation': 'multiply'
        },
        {
            'matrix_a': np.random.rand(200, 200),
            'matrix_b': np.random.rand(200, 200),
            'operation': 'multiply'
        }
    ]
    
    try:
        results = process_booking_data(test_data)
        print(f"Обработано {len(results)} элементов")
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Включаем tracemalloc для отслеживания памяти
    tracemalloc.start()
    
    print("=== Вариант 12: NumPy ошибки ===")
    print("1. Запуск с трассировкой памяти")
    
    # Запускаем демонстрацию
    run_memory_leak_demo()
    
    # Снимаем снапшот памяти
    snapshot = tracemalloc.take_snapshot()
    print("\n=== Топ-10 объектов по потреблению памяти ===")
    for stat in snapshot.statistics('lineno')[:10]:
        print(stat)
    
    # Проверяем размер кеша
    print(f"\nРазмер глобального кеша: {len(RESULT_CACHE)} элементов")
    
    # Попытка вызвать сборщик мусора
    import gc
    gc.collect()
    
    # Снимаем еще один снапшот после GC
    snapshot_after = tracemalloc.take_snapshot()
    print("\n=== Топ-10 объектов после GC ===")
    for stat in snapshot_after.statistics('lineno')[:10]:
        print(stat)
    
    print("\nПрограмма завершена")

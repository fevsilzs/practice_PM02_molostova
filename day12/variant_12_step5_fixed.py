import numpy as np
import tracemalloc
import gc
from collections import OrderedDict

# ИСПРАВЛЕНИЕ 1: Кеш с ограничением 
class LimitedCache:
    def __init__(self, maxsize=5):
        self.cache = OrderedDict()
        self.maxsize = maxsize
    
    def __setitem__(self, key, value):
        if len(self.cache) >= self.maxsize:
            self.cache.popitem(last=False)
        self.cache[key] = value
    
    def __len__(self):
        return len(self.cache)

RESULT_CACHE = LimitedCache(maxsize=5)

def process_matrix_operation(matrix_a, matrix_b, operation_type='multiply'):
    """ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    
    #ИСПРАВЛЕНИЕ 2: vectorize с проверкой
    def custom_func(x):
        return np.sqrt(x) if x > 0 else 0  # Безопасный sqrt
    
    vectorized_func = np.vectorize(custom_func)
    
    #ИСПРАВЛЕНИЕ 3: Безопасная индексация 
    if len(matrix_a.shape) >= 3:
        temp_a = matrix_a[0, :, :]
    else:
        temp_a = matrix_a
    
    # ИСПРАВЛЕНИЕ 4: Правильное матричное умножение 
    if operation_type == 'multiply':
        try:
            result = np.dot(matrix_a, matrix_b)  # Матричное умножение
        except ValueError:
            result = matrix_a * matrix_b
    elif operation_type == 'add':
        result = matrix_a + matrix_b
    else:
        result = matrix_a
    
    #  ИСПРАВЛЕНИЕ 5: Удаление временных массивов 
    temp_results = []
    for i in range(3):
        temp_array = np.random.rand(100, 100) * 1000
        processed = vectorized_func(temp_array)
        temp_results.append(processed)
        # ЯВНО УДАЛЯЕМ
        del temp_array
        del processed
    
    # ИСПРАВЛЕНИЕ 6: Кеширование с ограничением 
    cache_key = f"{matrix_a.shape}_{matrix_b.shape}_{operation_type}"
    RESULT_CACHE[cache_key] = result
    
    # ИСПРАВЛЕНИЕ 7: Безопасное broadcasting 
    if matrix_a.shape[0] > 50:
        try:
            add_array = np.random.rand(matrix_a.shape[0], 1)
            if add_array.shape[0] == result.shape[0]:
                result = result + add_array
        except ValueError:
            pass
    
    return result

def process_booking_data(data):
    """ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    results = []
    
    for i, item in enumerate(data):
        print(f"\n📦 Обработка элемента {i}")
        
        # ИСПРАВЛЕНИЕ 8: Безопасный доступ к ключам 
        matrix_a = item.get('matrix_a')
        if matrix_a is None:
            print(f"   ⚠️ Пропуск: нет 'matrix_a'")
            continue
        
        matrix_b = item.get('matrix_b')
        if matrix_b is None:
            print(f"   ⚠️ Пропуск: нет 'matrix_b'")
            continue
        
        op_type = item.get('operation', 'multiply')
        
        print(f"   ✅ matrix_a: {matrix_a.shape}, matrix_b: {matrix_b.shape}")
        
        # Безопасная работа с многомерными массивами
        if len(matrix_a.shape) == 3:
            matrix_a = matrix_a[0, :, :]
        
        result = process_matrix_operation(matrix_a, matrix_b, op_type)
        results.append(result)
        print(f"   ✅ Результат добавлен ({len(results)} элементов)")
    
    return results

def run_demo():
    """Запуск исправленной версии"""
    print("\n" + "="*50)
    print("ЭТАП 5: ИСПРАВЛЕННАЯ ВЕРСИЯ")
    print("="*50)
    
    # Все элементы содержат все ключи
    test_data = [
        {'matrix_a': np.random.rand(10, 10), 'matrix_b': np.random.rand(10, 10), 'operation': 'multiply'},
        {'matrix_a': np.random.rand(60, 60), 'matrix_b': np.random.rand(60, 60), 'operation': 'multiply'},
        {'matrix_a': np.random.rand(20, 20), 'matrix_b': np.random.rand(20, 20), 'operation': 'multiply'},
        {'matrix_a': np.random.rand(5, 10, 10), 'matrix_b': np.random.rand(5, 10, 10), 'operation': 'multiply'}
    ]
    
    print(f"📊 Всего элементов: {len(test_data)}")
    
    try:
        results = process_booking_data(test_data)
        print(f"\n✅ УСПЕШНО Обработано {len(results)} элементов")
        return results
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    tracemalloc.start()
    
    print("="*50)
    print("ИСПРАВЛЕННАЯ ВЕРСИЯ ВАРИАНТА 12")
    print("="*50)
    
    results = run_demo()
    
    snapshot = tracemalloc.take_snapshot()
    print("\n" + "="*50)
    print("ТОП-10 ОБЪЕКТОВ ПО ПАМЯТИ")
    print("="*50)
    for stat in snapshot.statistics('lineno')[:10]:
        print(f"   {stat}")
    
    print(f"\n📦 Размер кеша: {len(RESULT_CACHE)} элементов")
    
    gc.collect()
    
    print("\n" + "="*50)
    print("✅ ПРОГРАММА УСПЕШНО ЗАВЕРШЕНА")
    print("="*50)

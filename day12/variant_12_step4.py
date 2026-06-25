import numpy as np
import tracemalloc
import gc
from collections import OrderedDict
import time

#КЕШ С ОГРАНИЧЕНИЕМ (будет использован в исправлении)
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

# Глобальный кеш - БЕЗ ОГРАНИЧЕНИЯ (для демонстрации утечки)
RESULT_CACHE = {}

def process_matrix_operation(matrix_a, matrix_b, operation_type='multiply'):
    def custom_func(x):
        if x > 0:
            return np.sqrt(x)
        else:
            return np.sqrt(-x)  # ОШИБКА!
    
    vectorized_func = np.vectorize(custom_func)
    
    try:
        temp_a = matrix_a[:, :, 0]
    except:
        temp_a = matrix_a.copy()
    
    if operation_type == 'multiply':
        result = matrix_a * matrix_b
    elif operation_type == 'add':
        result = matrix_a + matrix_b
    else:
        result = matrix_a
    
    #УТЕЧКА ПАМЯТИ: большие временные массивы НЕ УДАЛЯЮТСЯ 
    temp_results = []
    for i in range(5):
        temp_array = np.random.rand(500, 500) * 1000  # ~2 МБ каждый
        processed = vectorized_func(temp_array)
        temp_results.append(processed)
        # НЕ УДАЛЯЕМ - утечка!
    
    # Кешируем результат - кеш растет бесконечно
    cache_key = f"{matrix_a.shape}_{matrix_b.shape}_{operation_type}"
    RESULT_CACHE[cache_key] = result
    
    return result

def process_booking_data(data):
    results = []
    
    for i, item in enumerate(data):
        print(f"\n📦 Обработка элемента {i}")
        
        # Безопасный доступ
        matrix_a = item.get('matrix_a')
        if matrix_a is None:
            continue
        
        matrix_b = item.get('matrix_b')
        if matrix_b is None:
            continue
        
        op_type = item.get('operation', 'multiply')
        print(f"   matrix_a: {matrix_a.shape}, matrix_b: {matrix_b.shape}")
        
        result = process_matrix_operation(matrix_a, matrix_b, op_type)
        results.append(result)
    
    return results

def analyze_memory():
    """Анализ памяти с tracemalloc"""
    print("\n" + "="*50)
    print("ОТЛАДКА ПАМЯТИ С tracemalloc")
    print("="*50)
    
    # Включаем tracemalloc
    tracemalloc.start()
    
    # Снапшот ДО
    print("\n📸 Снапшот 1: ДО выполнения")
    snapshot1 = tracemalloc.take_snapshot()
    for stat in snapshot1.statistics('lineno')[:5]:
        print(f"   {stat}")
    
    # Выполняем операции (создаем утечки)
    print("\n🔄 Выполнение операций...")
    test_data = [
        {'matrix_a': np.random.rand(50, 50), 'matrix_b': np.random.rand(50, 50)},
        {'matrix_a': np.random.rand(60, 60), 'matrix_b': np.random.rand(60, 60)},
        {'matrix_a': np.random.rand(70, 70), 'matrix_b': np.random.rand(70, 70)},
        {'matrix_a': np.random.rand(80, 80), 'matrix_b': np.random.rand(80, 80)},
        {'matrix_a': np.random.rand(90, 90), 'matrix_b': np.random.rand(90, 90)},
    ]
    
    results = process_booking_data(test_data)
    print(f"✅ Обработано {len(results)} элементов")
    
    # Снапшот ПОСЛЕ
    print("\n📸 Снапшот 2: ПОСЛЕ выполнения")
    snapshot2 = tracemalloc.take_snapshot()
    for stat in snapshot2.statistics('lineno')[:10]:
        print(f"   {stat}")
    
    # Сравнение снапшотов
    print("\n📊 СРАВНЕНИЕ СНАПШОТОВ (прирост памяти):")
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    for stat in top_stats[:5]:
        print(f"   {stat}")
    
    # Анализ утечек
    print(f"\n📦 Размер кеша: {len(RESULT_CACHE)} элементов")
    
    # Находим функцию с наибольшим потреблением
    print("\n🔍 ФУНКЦИЯ С НАИБОЛЬШИМ ПОТРЕБЛЕНИЕМ ПАМЯТИ:")
    stats = snapshot2.statistics('lineno')
    for stat in stats[:3]:
        print(f"   {stat}")
    
    # ===== ИСПРАВЛЕНИЕ УТЕЧКИ =====
    print("\n" + "="*50)
    print("ИСПРАВЛЕНИЕ УТЕЧКИ ПАМЯТИ")
    print("="*50)
    
    # Очищаем кеш
    print("🧹 Очистка кеша...")
    RESULT_CACHE.clear()
    gc.collect()
    
    # Снапшот ПОСЛЕ ОЧИСТКИ
    print("\n📸 Снапшот 3: ПОСЛЕ ОЧИСТКИ")
    snapshot3 = tracemalloc.take_snapshot()
    for stat in snapshot3.statistics('lineno')[:5]:
        print(f"   {stat}")
    
    print(f"\n📦 Размер кеша после очистки: {len(RESULT_CACHE)} элементов")
    
    return snapshot1, snapshot2, snapshot3

if __name__ == "__main__":
    print("="*50)
    print("ЭТАП 4: ОТЛАДКА ПАМЯТИ С tracemalloc")
    print("="*50)
    
    s1, s2, s3 = analyze_memory()
    
    print("\n" + "="*50)
    print("ВЫВОДЫ:")
    print("="*50)
    print("1. Утечка памяти происходит из-за:")
    print("   - Временных массивов, которые не удаляются (temp_array, processed)")
    print("   - Бесконечного роста кеша RESULT_CACHE")
    print("2. Решение:")
    print("   - Добавить явное удаление: del temp_array, del processed")
    print("   - Ограничить размер кеша: использовать LimitedCache(maxsize=5)")
    print("="*50)

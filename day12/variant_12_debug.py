import numpy as np
import tracemalloc

RESULT_CACHE = {}

def process_matrix_operation(matrix_a, matrix_b, operation_type='multiply'):
    def custom_func(x):
        if x > 0:
            return np.sqrt(x)
        else:
            return x * 2
    
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
    
    temp_results = []
    for i in range(10):
        temp_array = np.random.rand(100, 100) * 1000
        processed = vectorized_func(temp_array)
        temp_results.append(processed)
    
    cache_key = f"{id(matrix_a)}_{id(matrix_b)}_{operation_type}"
    RESULT_CACHE[cache_key] = result
    
    if matrix_a.shape[0] > 100:
        result = result + np.random.rand(matrix_a.shape[0], 1)
    
    return result

def process_booking_data(data):
    results = []
    
    for i, item in enumerate(data):
        # ВСТАВЛЯЕМ breakpoint() ДЛЯ ОТЛАДКИ
        breakpoint()  #ТОЧКА ОСТАНОВА
        
        print(f"\n=== Обработка элемента {i} ===")
        print(f"Содержимое item: {item}")
        
        # ОШИБКА: KeyError при отсутствии ключа
        matrix_a = item['matrix_a']
        matrix_b = item['matrix_b']  # ЗДЕСЬ БУДЕТ ОШИБКА
        op_type = item.get('operation', 'multiply')
        
        if len(matrix_a.shape) == 3:
            matrix_a = matrix_a[0, :, :]
        
        result = process_matrix_operation(matrix_a, matrix_b, op_type)
        results.append(result)
    
    return results

def run_memory_leak_demo():
    print("Запуск демонстрации утечки памяти...")
    
    test_data = [
        {'matrix_a': np.random.rand(50, 50), 'matrix_b': np.random.rand(50, 50), 'operation': 'multiply'},
        {'matrix_a': np.random.rand(100, 100), 'matrix_b': np.random.rand(100, 100), 'operation': 'add'},
        {'matrix_a': np.random.rand(30, 30), 'operation': 'multiply'},  # ОШИБКА: нет 'matrix_b'
        {'matrix_a': np.random.rand(200, 200), 'matrix_b': np.random.rand(200, 200), 'operation': 'multiply'}
    ]
    
    try:
        results = process_booking_data(test_data)
        print(f"Обработано {len(results)} элементов")
    except Exception as e:
        print(f"ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    tracemalloc.start()
    print("=== ВАРИАНТ 12: ОТЛАДКА С breakpoint() ===")
    run_memory_leak_demo()

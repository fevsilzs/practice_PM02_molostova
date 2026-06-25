import numpy as np
import tracemalloc
import sys
from datetime import datetime

RESULT_CACHE = {}

def process_matrix_operation(matrix_a, matrix_b, operation_type='multiply'):
    def custom_func(x):
        if x > 0:
            return np.sqrt(x)
        else:
            return np.sqrt(-x)  # ОШИБКА: sqrt от отрицательного
    
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
    for i in range(3):
        temp_array = np.random.rand(100, 100) * 1000
        processed = vectorized_func(temp_array)
        temp_results.append(processed)
    
    cache_key = f"{id(matrix_a)}_{id(matrix_b)}_{operation_type}"
    RESULT_CACHE[cache_key] = result
    
    return result

def process_booking_data(data):
    results = []
    
    for i, item in enumerate(data):
        print(f"\n=== Обработка элемента {i} ===")
        print(f"item: {item}")
        
        # ==========================================
        # АВТОМАТИЧЕСКОЕ ЛОГИРОВАНИЕ СЕССИИ pdb
        # ==========================================
        # Создаем файл лога с уникальным именем
        log_filename = f'pdb_session_element_{i}.log'
        print(f"📝 Логирование pdb в файл: {log_filename}")
        
        # Открываем файл для записи
        log_file = open(log_filename, 'w', encoding='utf-8')
        log_file.write("="*80 + "\n")
        log_file.write(f"СЕССИЯ pdb - ЭЛЕМЕНТ {i}\n")
        log_file.write(f"Дата: {datetime.now()}\n")
        log_file.write("="*80 + "\n\n")
        
        # Записываем информацию о переменной item
        log_file.write(f"item: {item}\n")
        log_file.write(f"Ключи: {list(item.keys())}\n")
        log_file.write("-"*80 + "\n\n")
        
        # Перенаправляем stdout в файл
        original_stdout = sys.stdout
        sys.stdout = log_file
        
        # ==========================================
        # ТОЧКА ОСТАНОВА pdb
        # ==========================================
        breakpoint()  # <--- ТОЧКА ОСТАНОВА
        
        # Возвращаем stdout обратно
        sys.stdout = original_stdout
        log_file.write("\n" + "="*80 + "\n")
        log_file.write("КОНЕЦ СЕССИИ pdb\n")
        log_file.write("="*80 + "\n")
        log_file.close()
        
        print(f"✅ Лог сохранен в {log_filename}")
        print("-"*30)
        
        # ==========================================
        # ПОДОЗРИТЕЛЬНАЯ СТРОКА (ЗДЕСЬ БУДЕТ ОШИБКА)
        # ==========================================
        matrix_a = item['matrix_a']
        matrix_b = item['matrix_b']  # KeyError, если ключа нет
        op_type = item.get('operation', 'multiply')
        
        if len(matrix_a.shape) == 3:
            matrix_a = matrix_a[0, :, :]
        
        result = process_matrix_operation(matrix_a, matrix_b, op_type)
        results.append(result)
    
    return results

def run_demo():
    print("\n" + "="*50)
    print("ЭТАП 2: ЛОКАЛИЗАЦИЯ С breakpoint() + АВТОЛОГ")
    print("="*50)
    
    test_data = [
        {'matrix_a': np.random.rand(10, 10), 'matrix_b': np.random.rand(10, 10)},
        {'matrix_a': np.random.rand(20, 20), 'matrix_b': np.random.rand(20, 20)},
        {'matrix_a': np.random.rand(30, 30)},  # ОШИБКА: нет 'matrix_b'
        {'matrix_a': np.random.rand(40, 40), 'matrix_b': np.random.rand(40, 40)}
    ]
    
    print(f"📊 Всего элементов: {len(test_data)}")
    print("\n" + "="*50)
    print("ЛОГИ БУДУТ СОХРАНЕНЫ В ФАЙЛЫ:")
    print("  - pdb_session_element_0.log")
    print("  - pdb_session_element_1.log")
    print("  - pdb_session_element_2.log (ЗДЕСЬ БУДЕТ ОШИБКА)")
    print("  - pdb_session_element_3.log")
    print("="*50 + "\n")
    
    try:
        results = process_booking_data(test_data)
        print(f"\n✅ Обработано {len(results)} элементов")
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    tracemalloc.start()
    run_demo()
    
    # Анализ памяти
    snapshot = tracemalloc.take_snapshot()
    print("\n" + "="*50)
    print("ПАМЯТЬ:")
    for stat in snapshot.statistics('lineno')[:5]:
        print(f"  {stat}")

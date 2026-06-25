import numpy as np
from variant_12_step5_fixed import process_matrix_operation, process_booking_data, RESULT_CACHE

def test_1_keyerror_fixed():
    """Тест: проверка обработки отсутствующих ключей"""
    print("🧪 Тест 1: KeyError")
    data = [{'matrix_a': np.array([1, 2, 3])}]
    results = process_booking_data(data)
    assert len(results) == 0, "Должен быть пропуск элемента"
    print("   ✅ KeyError обработан\n")

def test_2_matrix_multiply():
    """Тест: правильность матричного умножения"""
    print("🧪 Тест 2: Матричное умножение")
    a = np.array([[1, 2], [3, 4]])
    b = np.array([[5, 6], [7, 8]])
    result = process_matrix_operation(a, b, 'multiply')
    expected = np.dot(a, b)
    assert np.array_equal(result, expected), "Неправильное умножение"
    print("   ✅ Умножение корректно\n")

def test_3_memory_leak():
    """Тест: проверка утечек памяти"""
    print("🧪 Тест 3: Утечки памяти")
    initial_size = len(RESULT_CACHE)
    for i in range(20):
        a = np.random.rand(5, 5)
        b = np.random.rand(5, 5)
        process_matrix_operation(a, b, 'multiply')
    assert len(RESULT_CACHE) <= 10, "Кеш превысил лимит"
    print(f"   ✅ Утечек нет (кеш: {len(RESULT_CACHE)} элементов)\n")

def test_4_negative_values():
    """Тест: обработка отрицательных чисел"""
    print("🧪 Тест 4: Отрицательные числа")
    a = np.array([[-1, -2], [3, 4]])
    b = np.array([[5, 6], [7, 8]])
    result = process_matrix_operation(a, b, 'multiply')
    assert not np.isnan(result).any(), "Есть NaN значения"
    print("   ✅ Отрицательные числа обработаны\n")

def test_5_index_error():
    """Тест: проверка IndexError"""
    print("🧪 Тест 5: IndexError")
    a = np.random.rand(5, 5)
    b = np.random.rand(5, 5)
    # Должно работать без ошибок
    result = process_matrix_operation(a, b, 'multiply')
    assert result is not None, "Результат не должен быть None"
    print("   ✅ IndexError обработан\n")

if __name__ == "__main__":
    print("="*50)
    print("ЭТАП 6: ФИНАЛЬНАЯ ПРОВЕРКА")
    print("="*50)
    
    test_1_keyerror_fixed()
    test_2_matrix_multiply()
    test_3_memory_leak()
    test_4_negative_values()
    test_5_index_error()
    
    print("="*50)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    print("="*50)

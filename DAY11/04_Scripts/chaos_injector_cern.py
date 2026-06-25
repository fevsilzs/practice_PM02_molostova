import os
import random
import shutil
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

# КОНФИГУРАЦИЯ (ВСЕ ЛОКАЛЬНО!)
TEST_DATA_DIR = "./test_data/"
METADATA_FILE = "./files_checksums.json"  # Будем удалять этот файл

def create_test_data():
    """Создание тестовых данных"""
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    
    # Создаем ROOT-файлы
    for i in range(1, 11):
        file_path = f"{TEST_DATA_DIR}/data_{i}.root"
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(f"=== ЭКСПЕРИМЕНТАЛЬНЫЕ ДАННЫЕ ===\n")
                f.write(f"Файл: data_{i}\n")
                f.write(f"Создан: {datetime.now()}\n")
                f.write("Данные: " + "X"*100 + "\n")
                f.write(f"Run: 2026-06-17\n")
            logger.info(f"Создан: {file_path}")
    
    # Создаем HDF5 файлы
    for i in range(1, 6):
        file_path = f"{TEST_DATA_DIR}/calib_{i}.h5"
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(f"=== КАЛИБРОВКИ ===\n")
                f.write(f"Набор: {i}\n")
                f.write(f"Параметры: {i*100}\n")
            logger.info(f"Создан: {file_path}")
    
    # Создаем метаданные (имитация PostgreSQL)
    if not os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'w') as f:
            f.write("=== МЕТАДАННЫЕ ЭКСПЕРИМЕНТА ===\n")
            f.write(f"Дата создания: {datetime.now()}\n")
            f.write("="*50 + "\n")
            for i in range(1, 11):
                f.write(f"data_{i}.root | SHA256: abc123_hash_{i}\n")
            for i in range(1, 6):
                f.write(f"calib_{i}.h5 | SHA256: def456_hash_{i}\n")
        logger.info(f"Созданы метаданные: {METADATA_FILE}")

def show_files():
    """Показать список файлов"""
    print("\n📋 ТЕКУЩИЕ ФАЙЛЫ:")
    for root, dirs, files in os.walk(TEST_DATA_DIR):
        for file in files:
            print(f"   - {file}")
    if os.path.exists(METADATA_FILE):
        print(f"   - {os.path.basename(METADATA_FILE)}")

def corrupt_root_files(corruption_rate=0.3):
    """Повреждение ROOT-файлов"""
    logger.warning(f"🔥 Повреждение {corruption_rate*100}% ROOT-файлов...")
    
    root_files = []
    for root, dirs, files in os.walk(TEST_DATA_DIR):
        for file in files:
            if file.endswith('.root'):
                root_files.append(os.path.join(root, file))
    
    if not root_files:
        logger.warning("ROOT-файлы не найдены!")
        return
    
    to_corrupt = random.sample(root_files, max(1, int(len(root_files) * corruption_rate)))
    
    for file_path in to_corrupt:
        try:
            with open(file_path, 'r+') as f:
                content = f.read()
                content = content.replace("ЭКСПЕРИМЕНТАЛЬНЫЕ", "ПОВРЕЖДЕННЫЕ")
                content = content.replace("X"*100, "!"*100)
                f.seek(0)
                f.write(content)
                f.truncate()
                logger.info(f"💥 Поврежден: {os.path.basename(file_path)}")
        except Exception as e:
            logger.error(f"Ошибка: {e}")

def encrypt_files(fraction=0.2):
    """Шифрование файлов (переименование)"""
    logger.warning(f"🔒 Шифрование {fraction*100}% файлов...")
    
    all_files = []
    for root, dirs, files in os.walk(TEST_DATA_DIR):
        for file in files:
            if file.endswith('.h5') or file.endswith('.hdf5'):
                all_files.append(os.path.join(root, file))
    
    if not all_files:
        return
    
    to_encrypt = random.sample(all_files, max(1, int(len(all_files) * fraction)))
    
    for file_path in to_encrypt:
        try:
            new_path = file_path + '.encrypted'
            os.rename(file_path, new_path)
            logger.info(f"🔒 Зашифрован: {os.path.basename(file_path)}")
        except Exception as e:
            logger.error(f"Ошибка: {e}")

def delete_metadata():
    """Удаление метаданных"""
    logger.warning("🗑️ УДАЛЕНИЕ МЕТАДАННЫХ...")
    try:
        if os.path.exists(METADATA_FILE):
            backup_name = f"{METADATA_FILE}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(METADATA_FILE, backup_name)
            logger.error(f"❌ Метаданные удалены! Резервная копия: {backup_name}")
        else:
            logger.warning("Файл метаданных не найден")
    except Exception as e:
        logger.error(f"Ошибка: {e}")

def simulate_tape_failure():
    """Имитация отказа ленточной библиотеки"""
    logger.warning("💿 ОТКАЗ ЛЕНТОЧНОЙ БИБЛИОТЕКИ...")
    try:
        if os.path.exists('./tape_library/'):
            shutil.move('./tape_library/', './tape_library_BROKEN/')
            logger.error("❌ Ленточная библиотека НЕДОСТУПНА!")
        else:
            os.makedirs('./tape_library/', exist_ok=True)
            shutil.move('./tape_library/', './tape_library_BROKEN/')
            logger.error("❌ Ленточная библиотека НЕДОСТУПНА!")
    except Exception as e:
        logger.error(f"Ошибка: {e}")

def main():
    print("="*70)
    print("🔥 CHAOS ENGINE - СИМУЛЯЦИЯ АВАРИИ")
    print("⚠️ ТОЛЬКО ТЕСТОВАЯ СРЕДА!")
    print("📁 Работаем в папке:", TEST_DATA_DIR)
    print("="*70)
    
    # Создаем тестовые данные
    create_test_data()
    
    print("\n📋 ДО АТАКИ:")
    show_files()
    
    print("\n" + "="*70)
    print("🚀 ЗАПУСК АТАКИ...")
    print("="*70)
    
    # ЗАПУСКАЕМ ХАОС
    corrupt_root_files(0.3)      # Повреждаем 30% ROOT-файлов
    encrypt_files(0.2)            # Шифруем 20% файлов
    delete_metadata()             # Удаляем метаданные
    simulate_tape_failure()       # Ломаем ленту
    
    print("\n📋 ПОСЛЕ АТАКИ:")
    show_files()
    
    print("\n" + "="*70)
    print("✅ АВАРИЯ СИМУЛИРОВАНА УСПЕШНО!")
    print("="*70)
    print("\n📌 СТАТУС:")
    print("   ❌ 30% ROOT-файлов повреждены")
    print("   ❌ 20% файлов зашифрованы")
    print("   ❌ Метаданные удалены")
    print("   ❌ Ленточная библиотека недоступна")
    print("="*70)
    print("\n📌 ДЛЯ ВОССТАНОВЛЕНИЯ:")
    print("   1. Запустите backup_physics_data.py")
    print("   2. Восстановите метаданные из резервной копии")
    print("   3. Проверьте целостность файлов")
    print("="*70)

if __name__ == "__main__":
    main()

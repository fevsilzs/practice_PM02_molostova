import os
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# КОНФИГУРАЦИЯ
DATA_DIR = "./test_data/"
METADATA_DB = "./files_checksums.json"
REPORT_FILE = "./verification_report.txt"

def calculate_sha256(file_path):
    """Вычисление SHA-256 контрольной суммы"""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Ошибка чтения {file_path}: {e}")
        return None

def find_metadata_backup():
    """Поиск резервной копии метаданных"""
    backups = []
    for f in os.listdir('.'):
        if f.startswith('files_checksums.json.backup_'):
            backups.append(f)
    return backups

def restore_metadata():
    """Восстановление метаданных из резервной копии"""
    backups = find_metadata_backup()
    if not backups:
        logger.error("❌ Резервные копии метаданных не найдены!")
        return False
    
    # Используем самую свежую копию
    latest_backup = sorted(backups)[-1]
    try:
        with open(latest_backup, 'r') as src:
            data = src.read()
        with open(METADATA_DB, 'w') as dst:
            dst.write(data)
        logger.info(f"✅ Метаданные восстановлены из: {latest_backup}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка восстановления метаданных: {e}")
        return False

def verify_all_files():
    """Проверка всех файлов на целостность"""
    logger.info("🔍 ПРОВЕРКА ЦЕЛОСТНОСТИ ДАННЫХ")
    print("="*70)
    
    # Проверяем наличие метаданных
    if not os.path.exists(METADATA_DB):
        logger.warning("⚠️ Метаданные не найдены! Пытаемся восстановить...")
        if not restore_metadata():
            logger.error("❌ Невозможно продолжить проверку без метаданных")
            return
    
    # Загружаем метаданные
    try:
        with open(METADATA_DB, 'r') as f:
            checksums = json.load(f)
        logger.info(f"📋 Загружено метаданных: {len(checksums)} записей")
    except Exception as e:
        logger.error(f"❌ Ошибка чтения метаданных: {e}")
        return
    
    # Проверяем каждый файл
    corrupted = []
    missing = []
    total = len(checksums)
    checked = 0
    
    print("\n📋 ПРОВЕРКА ФАЙЛОВ:")
    print("-"*50)
    
    for file_path, expected_checksum in checksums.items():
        # Проверяем существование файла
        if not os.path.exists(file_path):
            logger.warning(f"⚠️ Файл не найден: {file_path}")
            missing.append(file_path)
            continue
        
        # Проверяем контрольную сумму
        current_checksum = calculate_sha256(file_path)
        if current_checksum is None:
            missing.append(file_path)
            continue
        
        if current_checksum != expected_checksum:
            logger.error(f"❌ КОРРУПЦИЯ: {file_path}")
            logger.error(f"   Ожидался: {expected_checksum}")
            logger.error(f"   Получен:  {current_checksum}")
            corrupted.append(file_path)
        else:
            logger.info(f"✅ OK: {file_path}")
        
        checked += 1
        if checked % 10 == 0:
            print(f"   Проверено {checked}/{total} файлов...")
    
    # Формируем отчет
    print("\n" + "="*70)
    print("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ")
    print("="*70)
    
    print(f"\n📁 Всего файлов в метаданных: {total}")
    print(f"✅ Проверено успешно: {checked - len(corrupted) - len(missing)}")
    print(f"⚠️ Отсутствует: {len(missing)}")
    print(f"❌ Повреждено: {len(corrupted)}")
    
    if corrupted:
        print("\n❌ ПОВРЕЖДЕННЫЕ ФАЙЛЫ:")
        for f in corrupted:
            print(f"   - {f}")
    
    if missing:
        print("\n⚠️ ОТСУТСТВУЮЩИЕ ФАЙЛЫ:")
        for f in missing:
            print(f"   - {f}")
    
    if not corrupted and not missing:
        print("\n🎉 ВСЕ ФАЙЛЫ ЦЕЛЫ! ВОССТАНОВЛЕНИЕ УСПЕШНО!")
    
    # Сохраняем отчет
    with open(REPORT_FILE, 'w') as f:
        f.write(f"ОТЧЕТ О ПРОВЕРКЕ ЦЕЛОСТНОСТИ\n")
        f.write(f"Дата: {datetime.now()}\n")
        f.write(f"{'='*50}\n")
        f.write(f"Всего файлов: {total}\n")
        f.write(f"Проверено успешно: {checked - len(corrupted) - len(missing)}\n")
        f.write(f"Отсутствует: {len(missing)}\n")
        f.write(f"Повреждено: {len(corrupted)}\n")
        if corrupted:
            f.write(f"\nПоврежденные файлы:\n")
            for item in corrupted:
                f.write(f"  - {item}\n")
        if missing:
            f.write(f"\nОтсутствующие файлы:\n")
            for item in missing:
                f.write(f"  - {item}\n")
    
    logger.info(f"📄 Отчет сохранен: {REPORT_FILE}")
    print(f"\n📄 Отчет сохранен в файл: {REPORT_FILE}")
    print("="*70)
    
    return len(corrupted) == 0 and len(missing) == 0

def main():
    print("="*70)
    print("🔍 СКРИПТ ПРОВЕРКИ ЦЕЛОСТНОСТИ ДАННЫХ")
    print("📁 Работаем в папке:", os.getcwd())
    print("="*70)
    
    # Поиск файлов для проверки
    all_files = list(Path(DATA_DIR).glob('**/*'))
    print(f"\n📋 Найдено файлов в test_data/: {len(all_files)}")
    
    # Запускаем проверку
    success = verify_all_files()
    
    if success:
        print("\n🎉 ВСЕ ФАЙЛЫ ЦЕЛЫ! СИСТЕМА ВОССТАНОВЛЕНА!")
    else:
        print("\n⚠️ ЕСТЬ ПРОБЛЕМЫ! Требуется восстановление поврежденных файлов.")
        print("📌 Запустите backup_physics_data.py для восстановления.")

if __name__ == "__main__":
    main()
